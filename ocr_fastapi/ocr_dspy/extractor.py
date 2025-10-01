# ocr_dspy/extractor.py
import dspy
import logging
from typing import List


# Define the signature for invoice extraction
class InvoiceExtractorSignature(dspy.Signature):
    """Extract structured data from invoice images."""
    input_image: dspy.Image = dspy.InputField(desc="The invoice image to analyze")
    total_net_worth: float = dspy.OutputField(desc="Total Net Worth (excluding VAT)", dtype=float)
    total_vat: float = dspy.OutputField(desc="Total VAT amount", dtype=float)
    gross_worth: float = dspy.OutputField(desc="Gross Worth (including VAT)", dtype=float)


class InvoiceExtractorModule(dspy.Module):
    def __init__(self):
        super().__init__()
        self.entity_extractor = dspy.Predict(InvoiceExtractorSignature)

    def forward(self, image_path: str):
        try:
            # Load image using dspy's Image primitive
            image = dspy.Image.from_file(file_path=image_path)

            # # Create extraction prompt
            # prompt = """Given the invoice image, extract the following financial values:
            # 1. Total Net Worth (excluding VAT)
            # 2. Total VAT amount
            # 3. Gross Worth (including VAT)
            #
            # Return only these numerical values in a structured format.
            # Be precise and return float values only."""

            # Perform extraction
            extracted_data = self.entity_extractor(
                input_image=image,
            )
            # return extracted_data
            return {
                "total_net_worth": extracted_data.total_net_worth if extracted_data.total_net_worth else 0.0,
                "total_vat": extracted_data.total_vat if extracted_data.total_vat else 0.0,
                "gross_worth": extracted_data.gross_worth if extracted_data.gross_worth else 0.0
            }
        except Exception as e:
            # logger.error(f"Error during invoice extraction: {e}")
            return {
                "total_net_worth": 0.0,
                "total_vat": 0.0,
                "gross_worth": 0.0
            }


def extract_invoice_data() :
    """Main function to extract invoice data."""
    lm = dspy.LM(
        model="gemini/gemini-2.5-flash",
        api_key="YOUR_API_KEY",
    )
    dspy.configure(lm=lm)
    image_path = "batch1-0002.jpg"
    # extractor = dspy.Predict(InvoiceExtractorSignature)
    # result =  extractor(input_image=dspy.Image.from_file(file_path=image_path))
    invoice_extractor_module = InvoiceExtractorModule()
    result = invoice_extractor_module(image_path)
    print(f"Extracted Invoice Data: {result}")

if __name__ == "__main__":
    extract_invoice_data()