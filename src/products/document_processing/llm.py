from src.products.document_processing.prompt import SYSTEM_PROMPT, build_document_prompt
from src.products.document_processing.schema import ProcessedDocument, ValidationIssue, DocumentValidationResult
from anthropic import Anthropic
from core.exceptions import LLMExtractionError
from dotenv import load_dotenv

load_dotenv()
client = Anthropic()
MODEL = "claude-sonnet-4-5"

def understand_document(raw_text: str, expected_document_type: str) -> ProcessedDocument:
    response = client.messages.parse(
    model=MODEL,
    max_tokens=2000,
    system = SYSTEM_PROMPT,
    messages = [
      {
        "role": "user",
        "content": build_document_prompt(raw_text, expected_document_type)
      }
    ],
    output_format=ProcessedDocument
  )
    parsed = response.parsed_output
    if response.stop_reason == "refusal":
      raise LLMExtractionError("The model refused to provide a response.")
      
    if response.stop_reason == "max_tokens":
      raise LLMExtractionError(
                  "Response was truncated; retry with a higher max_tokens."
              )
      
    if parsed is None:
      raise LLMExtractionError("No structured document was returned.")

    
    return parsed

if __name__ == "__main__":
    raw_text = """
    INVOICE

    Vendor: Acme Office Supplies
    Invoice Number: INV-4821
    Invoice Date: October 2, 2026
    Due Date: October 30, 2026

    Purchase Order: PO-9917

    Items:
    - Printer paper: $240.50
    - Toner cartridges: $600.00
    - Office chairs: $400.00

    Total Amount: $1,240.50
    Currency: USD

    Please remit payment by the due date.
    """

    expected_document_type = "invoice"

    try:
        document = understand_document(
            raw_text=raw_text,
            expected_document_type=expected_document_type,
        )

        print("\n--- Processed document ---")
        print(document)

        print("\n--- Extracted fields ---")
        print(f"Document type: {document.document_type}")
        print(f"Vendor: {document.vendor_name}")
        print(f"Invoice number: {document.invoice_number}")
        print(f"Invoice date: {document.invoice_date}")
        print(f"Due date: {document.due_date}")
        print(f"Total amount: {document.total_amount}")
        print(f"Currency: {document.currency}")
        print(f"Purchase order: {document.purchase_order_number}")
        print(f"Line items: {document.line_items}")
        print(f"Notes: {document.notes}")

    except LLMExtractionError as e:
        print(f"Error understanding document: {e}")