# AI Legal Filing Assistant

A sophisticated AI agent built with FastAPI, LangGraph, and Gemini 2.5 Pro that automates the search, retrieval, and structured data extraction of public company filings from official securities regulators in the United States (SEC EDGAR), Canada (SEDAR+), and Brazil (CVM Empresas.NET).

## Features

-   **Multi-Jurisdiction Intelligence**: Automatically identifies the correct country and data source based on the user's query
-   **Specialized Tool Usage**: Uses distinct, dedicated tools for searching each official database
-   **Hybrid Search Strategy**: Prioritizes official sources with fallback to reliable secondary sources
-   **Structured Output**: Uses Pydantic data models for consistent, clean, and predictable JSON output
-   **Robust Workflow**: Built with LangGraph for transparent, stateful, and resilient multi-step decision-making
-   **REST API**: FastAPI-based API for easy integration

## Project Structure

```
attorney-assist/
├── src/
│   └── ai_legal_assistant/
│       ├── __init__.py
│       ├── main.py                 # FastAPI application entry point
│       ├── agent_workflow.py       # LangGraph agent logic
│       ├── tools.py               # Search and document reading tools
│       ├── models.py              # Pydantic data models
│       └── config.py              # Configuration and API keys
├── requirements.txt       # Python dependencies
└── README.md             # This file
```

## Setup Instructions

### 1. Create Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### 2. Install Dependencies

```bash
# Option 1: Install in development mode (recommended)
pip install -e .

# Option 2: Install requirements directly
pip install -r requirements.txt
```

### 3. Configure API Keys

Create a `.env` file in the root directory with your API keys:

```env
GOOGLE_API_KEY="your_google_api_key_here"
SERPER_API_KEY="your_serper_api_key_here"
```

**How to get API keys:**

-   **Google API Key**: Visit [Google AI Studio](https://makersuite.google.com/app/apikey) to get your Gemini API key
-   **Serper API Key**: Visit [Serper.dev](https://serper.dev/) to get your web search API key

**Required API Keys:**

-   **Google API Key**: For Gemini 2.5 Pro LLM access (required for AI reasoning)
-   **Serper API Key**: For web search functionality (required for finding documents)

### 4. Run the Application

```bash
# Run with the module structure (recommended)
python -m src.ai_legal_assistant.main

# Or run with uvicorn command
uvicorn src.ai_legal_assistant.main:app --host 0.0.0.0 --port 8000 --reload
```

The API will be available at `http://localhost:8000`

### 5. Test the Setup

Run the test script to verify everything is working:

```bash
python test_setup.py
```

This will check:

-   All module imports work correctly
-   API key configuration
-   Basic functionality

## API Endpoints

### GET `/`

Root endpoint with API information.

### GET `/health`

Health check endpoint.

### POST `/search`

Main endpoint for searching company filings.

**Request Body:**

```json
{
    "query": "Find Microsoft's most recent 10-K annual report"
}
```

**Response:**

```json
{
    "success": true,
    "data": {
        "contract_name": "Form 10-K",
        "company_name": "Microsoft Corporation",
        "description": "Annual report for fiscal year ending June 30, 2024...",
        "filing_date": "2024-07-25",
        "source_of_information": "SEC EDGAR",
        "country": "United States",
        "language": "English",
        "applicable_law": "Securities Exchange Act of 1934",
        "relevant_clause": "Item 1A. Risk Factors",
        "document_url": "https://www.sec.gov/Archives/edgar/data/789019/000156459024030474/msft-10k_20240630.htm"
    }
}
```

### GET `/examples`

Get example queries for testing the API.

## Example Queries

-   "Find Microsoft's most recent 10-K annual report"
-   "Find Petrobras Formulário de Referência"
-   "Find Shopify's latest annual report on SEDAR"
-   "Find Apple's risk factors in their latest 10-K"

## API Documentation

Once the server is running, you can access:

-   **Interactive API docs**: `http://localhost:8000/docs`
-   **ReDoc documentation**: `http://localhost:8000/redoc`

## Supported Jurisdictions

1. **United States (SEC EDGAR)**

    - Form 10-K, 10-Q, 8-K, etc.
    - Uses `search_sec_edgar` tool

2. **Canada (SEDAR+)**

    - Annual reports, quarterly reports, etc.
    - Uses `search_sedar_plus` tool

3. **Brazil (CVM Empresas.NET)**
    - Formulário de Referência, DFP, etc.
    - Uses `search_cvm_empresas_net` tool

## Error Handling

The API includes comprehensive error handling:

-   Invalid API keys
-   Network connectivity issues
-   Document parsing errors
-   Structured output parsing failures

All errors are logged and returned with appropriate HTTP status codes.

## Development

### Running in Development Mode

```bash
uvicorn src.ai_legal_assistant.main:app --reload --host 0.0.0.0 --port 8000
```

### Testing the API

You can test the API using curl:

```bash
curl -X POST "http://localhost:8000/search" \
     -H "Content-Type: application/json" \
     -d '{"query": "Find Microsoft 10-K"}'
```

Or use the interactive documentation at `http://localhost:8000/docs`

## Dependencies

-   **FastAPI**: Modern web framework for building APIs
-   **LangGraph**: Framework for building stateful, multi-actor applications
-   **LangChain**: Framework for developing applications with LLMs
-   **Gemini 2.5 Pro**: Google's latest LLM for reasoning and analysis
-   **Pydantic**: Data validation using Python type annotations
-   **BeautifulSoup4**: HTML parsing and text extraction
-   **Google Serper**: Web search API for finding documents

## License

This project is for educational and research purposes.
