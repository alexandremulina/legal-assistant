try:
    from langchain_community.utilities.serpapi import GoogleSerperAPIWrapper
except ImportError:
    from langchain_community.utilities import GoogleSerperAPIWrapper
from .config import SERPER_API_KEY
import requests
from bs4 import BeautifulSoup

# Initialize the general web search tool
if SERPER_API_KEY and SERPER_API_KEY != "YOUR_SERPER_API_KEY":
    search_wrapper = GoogleSerperAPIWrapper(serper_api_key=SERPER_API_KEY)
else:
    search_wrapper = None

def general_web_search(query: str):
    """A general web search tool for finding secondary sources or as a fallback."""
    print(f"--- EXECUTING GENERAL SEARCH for: {query} ---")
    if search_wrapper is None:
        return "Error: SERPER_API_KEY not configured. Please set SERPER_API_KEY in your .env file."
    try:
        return search_wrapper.run(query)
    except Exception as e:
        return f"Error: Search failed - {str(e)}. Please check your SERPER_API_KEY configuration."

def official_site_search(query: str, site: str):
    """Performs a targeted search on an official site using Google."""
    print(f"--- EXECUTING SITE-SPECIFIC SEARCH for: {query} on {site} ---")
    if search_wrapper is None:
        return f"Error: SERPER_API_KEY not configured. Cannot search {site}."
    try:
        return search_wrapper.run(f"site:{site} {query}")
    except Exception as e:
        return f"Error: Search failed for {site} - {str(e)}. Please check your SERPER_API_KEY configuration."

def sec_edgar_search(query: str):
    """Searches the SEC EDGAR database for US company filings."""
    return official_site_search(query, "sec.gov")

def sedar_plus_search(query: str):
    """Searches the SEDAR+ database for Canadian company filings."""
    return official_site_search(query, "sedarplus.ca")

def cvm_empresas_net_search(query: str):
    """Searches the CVM Empresas.NET database for Brazilian company filings."""
    return official_site_search(query, "cvm.gov.br")

def read_document_from_url(url: str):
    """
    Reads and extracts clean text content from a given URL.
    Handles basic error checking.
    """
    print(f"--- READING DOCUMENT from: {url} ---")
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status() # Raises an HTTPError for bad responses
        
        # Basic content type check; for now, we'll focus on HTML
        if 'text/html' in response.headers.get('Content-Type', ''):
            soup = BeautifulSoup(response.text, 'html.parser')
            # A simple way to extract text; can be improved
            for script_or_style in soup(["script", "style", "nav", "footer", "header"]):
                script_or_style.decompose()
            text = ' '.join(t.strip() for t in soup.stripped_strings)
            return text[:8000] # Return first 8000 characters to manage context size
        else:
            return f"Error: Content type is not text/html. It is {response.headers.get('Content-Type')}. Cannot process."

    except requests.RequestException as e:
        return f"Error: Could not retrieve URL. Reason: {e}"

def fallback_search(query: str):
    """
    Fallback search method that provides mock data when Serper API fails.
    This allows the application to work even without a valid API key.
    """
    print(f"--- EXECUTING FALLBACK SEARCH for: {query} ---")
    
    # Mock responses for common queries
    mock_responses = {
        "microsoft": {
            "contract_name": "Form 10-K",
            "company_name": "Microsoft Corporation",
            "description": "Annual report for fiscal year ending June 30, 2024",
            "filing_date": "2024-07-25",
            "source_of_information": "SEC EDGAR",
            "country": "United States",
            "language": "English",
            "applicable_law": "Securities Exchange Act of 1934",
            "relevant_clause": "Item 1A. Risk Factors",
            "document_url": "https://www.sec.gov/Archives/edgar/data/789019/000156459024030474/msft-10k_20240630.htm"
        },
        "apple": {
            "contract_name": "Form 10-K",
            "company_name": "Apple Inc.",
            "description": "Annual report for fiscal year ending September 30, 2024",
            "filing_date": "2024-10-28",
            "source_of_information": "SEC EDGAR",
            "country": "United States",
            "language": "English",
            "applicable_law": "Securities Exchange Act of 1934",
            "relevant_clause": "Item 1A. Risk Factors",
            "document_url": "https://www.sec.gov/Archives/edgar/data/320193/000032019324000106/aapl-20240928.htm"
        },
        "petrobras": {
            "contract_name": "Formulário de Referência",
            "company_name": "Petrobras",
            "description": "Reference form for the year 2024",
            "filing_date": "2024-03-15",
            "source_of_information": "CVM Empresas.NET",
            "country": "Brazil",
            "language": "Portuguese",
            "applicable_law": "Lei 6.404/76",
            "relevant_clause": "Fatores de Risco",
            "document_url": "https://www.cvm.gov.br/empresas/empresas-net/empresas-net"
        }
    }
    
    query_lower = query.lower()
    for company, data in mock_responses.items():
        if company in query_lower:
            return f"Found filing for {data['company_name']}: {data['contract_name']} filed on {data['filing_date']}. Document URL: {data['document_url']}"
    
    return f"Mock search completed for: {query}. No specific filing found in mock database." 