from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI # type: ignore
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from typing import TypedDict, Annotated, List
import operator
from langchain_core.messages import BaseMessage, HumanMessage, ToolMessage
from langchain.agents import Tool

from .models import CompanyFiling
from .tools import sec_edgar_search, sedar_plus_search, cvm_empresas_net_search, general_web_search, read_document_from_url, fallback_search, real_sec_search
from .config import GOOGLE_API_KEY

# 1. Define Tools for the Agent
tools = [
    Tool(name="search_sec_edgar", func=sec_edgar_search, description="Use this to search for US company filings on the SEC EDGAR database. Input should be a company name and the form type, e.g., 'Microsoft 10-K'."),
    Tool(name="real_sec_search", func=real_sec_search, description="Use this for real-time SEC EDGAR searches using their public API. Input should be a company name."),
    Tool(name="search_sedar_plus", func=sedar_plus_search, description="Use this to search for Canadian company filings on the SEDAR+ database. Input should be a company name and the form type."),
    Tool(name="search_cvm_empresas_net", func=cvm_empresas_net_search, description="Use this to search for Brazilian company filings on the CVM Empresas.NET database. Input should be a company name and the form type, e.g., 'Petrobras Formulário de Referência'."),
    Tool(name="read_document_from_url", func=read_document_from_url, description="Use this to read the full text content of a document from a specific URL. The input MUST be a valid URL."),
    Tool(name="general_web_search", func=general_web_search, description="Use this as a fallback for general research or if you cannot find the document in the official databases."),
    Tool(name="fallback_search", func=fallback_search, description="Use this when other search tools fail or return errors. This provides mock data for demonstration purposes."),
]

# 2. Define Agent State
class AgentState(TypedDict):
    messages: Annotated[List[BaseMessage], operator.add]

# 3. Define Agent Logic (Nodes)
class FilingAgent:
    def __init__(self, llm, tools, checkpointer):
        self.llm = llm
        self.tools = tools
        self.checkpointer = checkpointer
        self.agent = self._create_agent()
        self.graph = self._create_graph()

    def _create_agent(self):
        system_prompt = """You are a highly specialized legal assistant. Your purpose is to find official company filings and extract specific information.

        **Follow these steps:**
        1.  **Analyze the user's request** to identify the company, the document type, and the jurisdiction (USA, Canada, or Brazil).
        2.  **ALWAYS try real search first**: Use `real_sec_search` for US companies to get actual SEC EDGAR data.
        3.  **If real search fails**, use the specialized search tools based on jurisdiction (e.g., `search_sec_edgar` for a 10-K, `search_cvm_empresas_net` for a DFP).
        4.  **Execute the search** and analyze the results. The search results will be text containing links.
        5.  **If all search tools return errors** (like "403 Forbidden" or "API key not configured"), use the `fallback_search` tool to provide mock data for demonstration purposes.
        6.  From the search results, **identify the most promising URL** to the actual filing document.
        7.  **Use the `read_document_from_url` tool** with the identified URL to get the document's content.
        8.  Finally, after you have the document's content, **DO NOT call any more tools**. Instead, provide your final answer by thoroughly analyzing the text and structuring it ONLY in the requested Pydantic `CompanyFiling` format. You must fill all the fields of the Pydantic model.

        **CRITICAL: You MUST use these EXACT field names in your JSON response:**
        - `contract_name` (not filing_type)
        - `company_name` 
        - `description` (not summary)
        - `filing_date`
        - `source_of_information`
        - `country`
        - `language`
        - `applicable_law`
        - `relevant_clause`
        - `document_url`

        **Example JSON structure:**
        ```json
        {{
          "contract_name": "Form 10-K",
          "company_name": "Microsoft Corporation",
          "description": "Annual report for fiscal year ending June 30, 2024...",
          "filing_date": "2024-07-25",
          "source_of_information": "SEC EDGAR",
          "country": "United States",
          "language": "English",
          "applicable_law": "Securities Exchange Act of 1934",
          "relevant_clause": "Item 1A. Risk Factors",
          "document_url": "https://www.sec.gov/..."
        }}
        ```
        """
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("placeholder", "{messages}"),
        ])
        
        return prompt | self.llm.bind_tools(tools)

    def _create_graph(self):
        graph = StateGraph(AgentState)
        graph.add_node("agent", self.call_agent)
        graph.add_node("tools", self.call_tools)
        graph.set_entry_point("agent")
        graph.add_conditional_edges(
            "agent",
            self.should_continue,
            {"tools": "tools", END: END}
        )
        graph.add_edge("tools", "agent")
        return graph.compile(checkpointer=self.checkpointer)

    def should_continue(self, state: AgentState):
        if isinstance(state['messages'][-1], ToolMessage):
            return "agent" # If the last message was a tool result, go back to the agent to decide next step
        if not state['messages'][-1].tool_calls:
            return END # If the LLM didn't call a tool, the conversation is over
        return "tools" # Otherwise, call the tools

    def call_agent(self, state: AgentState):
        print("--- CALLING AGENT ---")
        response = self.agent.invoke(state)
        return {"messages": [response]}

    def call_tools(self, state: AgentState):
        print("--- CALLING TOOLS ---")
        tool_calls = state['messages'][-1].tool_calls
        tool_outputs = []
        for call in tool_calls:
            tool_name = call['name']
            tool_input = call['args']
            # Find the corresponding tool function
            tool_func = next((t for t in self.tools if t.name == tool_name), None)
            if tool_func:
                output = tool_func.invoke(tool_input)
                tool_outputs.append(ToolMessage(content=str(output), tool_call_id=call['id']))
        return {"messages": tool_outputs}

# 4. Factory function to create and return the graph
def create_filing_agent_graph():
    llm = ChatGoogleGenerativeAI(model="gemini-2.5-pro", google_api_key=GOOGLE_API_KEY, convert_system_message_to_human=True)
    memory = MemorySaver()
    agent = FilingAgent(llm, tools, memory)
    return agent.graph 