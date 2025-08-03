from pydantic import BaseModel, Field
from typing import Optional

class CompanyFiling(BaseModel):
    """
    Data model for a company's securities filing.
    """
    contract_name: str = Field(description="The official name of the form (e.g., 'Form 10-K', 'Formulário de Referência').")
    company_name: str = Field(description="The full name of the company.")
    description: str = Field(description="A concise summary of the document's purpose and key findings relevant to the user's query.")
    filing_date: str = Field(description="The filing date of the document in YYYY-MM-DD format.")
    source_of_information: str = Field(description="The official source platform (e.g., 'SEC EDGAR', 'CVM Empresas.NET', 'SEDAR+').")
    country: str = Field(description="The country of the filing's jurisdiction (e.g., 'United States', 'Brazil', 'Canada').")
    language: str = Field(description="The primary language of the document.")
    applicable_law: Optional[str] = Field(description="The main law or regulation governing the filing (e.g., 'Securities Exchange Act of 1934').", default=None)
    relevant_clause: Optional[str] = Field(description="The specific clause or section title relevant to the query (e.g., 'Item 1A. Risk Factors').", default="N/A")
    document_url: str = Field(description="The direct URL to the complete source document.")

class FilingRequest(BaseModel):
    """
    Request model for filing queries.
    """
    query: str = Field(description="Natural language query describing the filing to search for")

class FilingResponse(BaseModel):
    """
    Response model for filing results.
    """
    success: bool
    data: Optional[CompanyFiling] = None
    error: Optional[str] = None 