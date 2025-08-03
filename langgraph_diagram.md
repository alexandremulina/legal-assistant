# AI Legal Filing Assistant - LangGraph Workflow Diagram

## Overview

This diagram shows the LangGraph workflow for the AI Legal Filing Assistant, which searches and extracts structured data from official company filings across multiple jurisdictions (SEC EDGAR, SEDAR+, CVM Empresas.NET).

## Workflow Diagram

```mermaid
graph TD
    A[User Query] --> B[FastAPI /search endpoint]
    B --> C[Create FilingAgent Graph]
    C --> D[Initialize StateGraph with AgentState]

    D --> E[Entry Point: Agent Node]
    E --> F[LLM Analysis]
    F --> G{Should Continue?}

    G -->|Tool Calls Detected| H[Tools Node]
    G -->|No Tool Calls| I[END - Return Response]

    H --> J[Execute Tools]
    J --> K{Which Tool?}

    K -->|US Filings| L[search_sec_edgar]
    K -->|Canadian Filings| M[search_sedar_plus]
    K -->|Brazilian Filings| N[search_cvm_empresas_net]
    K -->|Document Reading| O[read_document_from_url]
    K -->|General Research| P[general_web_search]

    L --> Q[Tool Results]
    M --> Q
    N --> Q
    O --> Q
    P --> Q

    Q --> R[ToolMessage to State]
    R --> E

    I --> S[Parse CompanyFiling Output]
    S --> T[Return FilingResponse]

    style A fill:#e1f5fe
    style B fill:#f3e5f5
    style E fill:#fff3e0
    style H fill:#e8f5e8
    style I fill:#ffebee
    style T fill:#e8f5e8
```

## Detailed Component Flow

```mermaid
sequenceDiagram
    participant U as User
    participant F as FastAPI
    participant G as Graph
    participant A as Agent Node
    participant T as Tools Node
    participant LLM as Gemini 2.5 Pro
    participant SEC as SEC EDGAR
    participant SEDAR as SEDAR+
    participant CVM as CVM Empresas.NET
    participant WEB as Web Search

    U->>F: POST /search with query
    F->>G: create_filing_agent_graph()
    G->>A: Entry Point

    A->>LLM: Analyze query & select jurisdiction
    LLM-->>A: Tool calls or final response

    alt Tool calls detected
        A->>T: Execute tools
        T->>SEC: search_sec_edgar(query)
        T->>SEDAR: search_sedar_plus(query)
        T->>CVM: search_cvm_empresas_net(query)
        T->>WEB: read_document_from_url(url)
        T->>WEB: general_web_search(query)

        SEC-->>T: Search results
        SEDAR-->>T: Search results
        CVM-->>T: Search results
        WEB-->>T: Document content
        WEB-->>T: Search results

        T-->>A: ToolMessage with results
        A->>LLM: Process results & decide next step
        LLM-->>A: Continue or finalize
    else No tool calls
        A->>F: Return structured CompanyFiling
    end

    F-->>U: FilingResponse with data
```

## State Management

```mermaid
stateDiagram-v2
    [*] --> InitialState
    InitialState --> AgentState: Create Graph

    AgentState --> ToolExecution: Tool calls detected
    ToolExecution --> AgentState: Tool results received

    AgentState --> FinalState: No more tool calls
    FinalState --> [*]: Return response

    note right of AgentState
        State contains:
        - messages: List[BaseMessage]
        - Accumulates conversation history
        - Includes HumanMessage, AIMessage, ToolMessage
    end note
```

## Tool Selection Logic

```mermaid
flowchart LR
    A[User Query] --> B{Analyze Query}

    B --> C{US Company?}
    B --> D{Canadian Company?}
    B --> E{Brazilian Company?}
    B --> F{General Research?}

    C --> G[search_sec_edgar]
    D --> H[search_sedar_plus]
    E --> I[search_cvm_empresas_net]
    F --> J[general_web_search]

    G --> K[Extract URLs]
    H --> K
    I --> K
    J --> K

    K --> L[read_document_from_url]
    L --> M[Parse Content]
    M --> N[Structure as CompanyFiling]

    style G fill:#ffcdd2
    style H fill:#c8e6c9
    style I fill:#fff9c4
    style J fill:#e1bee7
```

## Data Flow Architecture

```mermaid
graph TB
    subgraph "Input Layer"
        A[Natural Language Query]
        B[FilingRequest Model]
    end

    subgraph "Processing Layer"
        C[LangGraph StateGraph]
        D[Agent Node]
        E[Tools Node]
        F[Conditional Edges]
    end

    subgraph "Tool Layer"
        G[SEC EDGAR Search]
        H[SEDAR+ Search]
        I[CVM Empresas.NET Search]
        J[Document Reader]
        K[General Web Search]
    end

    subgraph "Output Layer"
        L[CompanyFiling Model]
        M[FilingResponse]
    end

    A --> B
    B --> C
    C --> D
    C --> E
    D --> F
    E --> F
    F --> G
    F --> H
    F --> I
    F --> J
    F --> K
    G --> L
    H --> L
    I --> L
    J --> L
    K --> L
    L --> M

    style A fill:#e3f2fd
    style M fill:#e8f5e8
    style C fill:#fff3e0
```

## Key Features

1. **Multi-Jurisdiction Support**: Automatically detects and routes to appropriate databases
2. **Structured Output**: Returns data in standardized `CompanyFiling` format
3. **Memory Management**: Uses `MemorySaver` for conversation persistence
4. **Error Handling**: Graceful fallback to general search when specialized tools fail
5. **Tool Chaining**: Sequential execution of search → document reading → parsing
6. **Conditional Logic**: Smart routing based on LLM decisions

## Tools Available

-   **search_sec_edgar**: US SEC EDGAR database searches
-   **search_sedar_plus**: Canadian SEDAR+ database searches
-   **search_cvm_empresas_net**: Brazilian CVM Empresas.NET searches
-   **read_document_from_url**: Extract content from document URLs
-   **general_web_search**: Fallback for general research

## Output Structure

The system returns structured data in the `CompanyFiling` format containing:

-   Contract name, company name, description
-   Filing date, source, country, language
-   Applicable law, relevant clause, document URL
