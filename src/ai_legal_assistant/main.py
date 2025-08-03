from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uuid
from langchain_core.messages import HumanMessage
from .agent_workflow import create_filing_agent_graph
from .models import CompanyFiling, FilingRequest, FilingResponse
from langchain_core.output_parsers import PydanticOutputParser
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="AI Legal Filing Assistant",
    description="An AI agent that searches and extracts structured data from official company filings across multiple jurisdictions (SEC EDGAR, SEDAR+, CVM Empresas.NET)",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global parser for structured output
parser = PydanticOutputParser(pydantic_object=CompanyFiling)

@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "AI Legal Filing Assistant API",
        "version": "1.0.0",
        "description": "Search and extract structured data from official company filings",
        "endpoints": {
            "/search": "POST - Search for company filings",
            "/health": "GET - Health check"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "AI Legal Filing Assistant"}

@app.post("/search", response_model=FilingResponse)
async def search_filing(request: FilingRequest):
    """
    Search for company filings based on natural language query.
    
    The agent will automatically:
    1. Identify the jurisdiction (US, Canada, Brazil)
    2. Search the appropriate official database
    3. Extract and structure the filing information
    4. Return a structured JSON response
    """
    try:
        logger.info(f"Processing search request: {request.query}")
        
        # Create a new graph instance for this request
        filing_agent_graph = create_filing_agent_graph()
        
        # Use a unique thread_id for each conversation
        thread_id = str(uuid.uuid4())
        config = {"configurable": {"thread_id": thread_id}}
        
        # Process the query through the agent
        final_state = filing_agent_graph.invoke(
            {"messages": [HumanMessage(content=request.query)]},
            config=config
        )
        
        # Extract the final response from the agent
        final_response_message = final_state['messages'][-1]
        
        # Parse the structured output
        try:
            parsed_output = parser.parse(final_response_message.content)
            logger.info("Successfully parsed structured output")
            
            return FilingResponse(
                success=True,
                data=parsed_output
            )
            
        except Exception as parse_error:
            logger.error(f"Failed to parse structured output: {parse_error}")
            logger.info(f"Raw agent response: {final_response_message.content}")
            
            # Try to extract useful information from the raw response
            try:
                import json
                raw_json = json.loads(final_response_message.content)
                
                # Create a structured response from the raw JSON
                structured_data = {
                    "contract_name": raw_json.get("filing_type", raw_json.get("contract_name", "Unknown")),
                    "company_name": raw_json.get("company_name", "Unknown"),
                    "description": raw_json.get("summary", raw_json.get("description", "No description available")),
                    "filing_date": raw_json.get("filing_date", "Unknown"),
                    "source_of_information": "SEC EDGAR" if "sec.gov" in raw_json.get("document_url", "") else "Unknown",
                    "country": "United States" if "sec.gov" in raw_json.get("document_url", "") else "Unknown",
                    "language": "English",
                    "applicable_law": "Securities Exchange Act of 1934",
                    "relevant_clause": "N/A",
                    "document_url": raw_json.get("document_url", "")
                }
                
                # Create CompanyFiling object manually
                from .models import CompanyFiling
                manual_parsed = CompanyFiling(**structured_data)
                
                logger.info("Successfully created structured output from raw response")
                return FilingResponse(
                    success=True,
                    data=manual_parsed
                )
                
            except Exception as manual_parse_error:
                logger.error(f"Failed to manually parse raw response: {manual_parse_error}")
                
                # Return the raw response if parsing fails
                return FilingResponse(
                    success=False,
                    error=f"Failed to parse structured output: {str(parse_error)}. Raw response: {final_response_message.content}"
                )

    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

@app.get("/examples")
async def get_examples():
    """Get example queries for testing the API."""
    return {
        "examples": [
            {
                "description": "Search for Microsoft's latest 10-K filing",
                "query": "Find Microsoft's most recent 10-K annual report"
            },
            {
                "description": "Search for a Brazilian company's reference form",
                "query": "Find Petrobras Formulário de Referência"
            },
            {
                "description": "Search for a Canadian company's annual report",
                "query": "Find Shopify's latest annual report on SEDAR"
            },
            {
                "description": "Search for Apple's risk factors",
                "query": "Find Apple's risk factors in their latest 10-K"
            }
        ]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 