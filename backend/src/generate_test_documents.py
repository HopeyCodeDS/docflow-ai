from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
import os
from pathlib import Path

# Create test_documents directory if it doesn't exist
TEST_DOCS_DIR = Path(__file__).parent / "test_documents"
TEST_DOCS_DIR.mkdir(exist_ok=True)

def create_cmr_pdfs(count=10):
    for i in range(1, count + 1):
        filename = TEST_DOCS_DIR / f"test_cmr_{i}.pdf"
        c = canvas.Canvas(str(filename), pagesize=letter)
        width, height = letter

        # Title
        c.setFont("Helvetica-Bold", 16)
        c.drawString(2 * inch, height - 1 * inch, "CMR - CONSIGNMENT NOTE")

        # Shipper
        c.setFont("Helvetica", 12)
        c.drawString(0.5 * inch, height - 1.5 * inch, f"SHIPPER:")
        c.drawString(0.5 * inch, height - 1.7 * inch, f"ABC Logistics Ltd. {i}")
        c.drawString(0.5 * inch, height - 1.9 * inch, f"{123 + i} Transport Street, London, UK")

        # Consignee
        c.drawString(0.5 * inch, height - 2.3 * inch, "CONSIGNEE:")
        c.drawString(0.5 * inch, height - 2.5 * inch, f"XYZ Trading Company {i}")
        c.drawString(0.5 * inch, height - 2.7 * inch, f"{456 + i} Business Avenue, Paris, France")

        # Details
        c.drawString(0.5 * inch, height - 3.1 * inch, f"Date of Consignment: 2024-01-{15+i:02d}")
        c.drawString(0.5 * inch, height - 3.3 * inch, f"Place of Consignment: London, UK")
        c.drawString(0.5 * inch, height - 3.5 * inch, f"Reference Number: CMR-2024-{1000 + i:06d}")
        c.drawString(0.5 * inch, height - 3.7 * inch, f"Goods Description: Electronic Components {i}")
        c.drawString(0.5 * inch, height - 3.9 * inch, f"Quantity: {50 + i} boxes")
        c.drawString(0.5 * inch, height - 4.1 * inch, f"Weight: {1250 + 10 * i} kg")

        c.save()
        print(f"Created {filename}")

def create_invoice_pdfs(count=10):
    for i in range(1, count + 1):
        filename = TEST_DOCS_DIR / f"test_invoice_{i}.pdf"
        c = canvas.Canvas(str(filename), pagesize=letter)
        width, height = letter

        c.setFont("Helvetica-Bold", 16)
        c.drawString(2 * inch, height - 1 * inch, "INVOICE")

        c.setFont("Helvetica", 12)
        c.drawString(0.5 * inch, height - 1.5 * inch, f"Invoice Number: INV-2024-{5000 + i:06d}")
        c.drawString(0.5 * inch, height - 1.7 * inch, f"Invoice Date: 2024-01-{20 + i:02d}")
        c.drawString(0.5 * inch, height - 1.9 * inch, f"Seller: Global Supplies Inc. {i}")
        c.drawString(0.5 * inch, height - 2.1 * inch, f"Buyer: Retail Chain Corp. {i}")
        c.drawString(0.5 * inch, height - 2.5 * inch, f"Total Amount: €{5250 + 100 * i:.2f}")
        c.drawString(0.5 * inch, height - 2.7 * inch, "Currency: EUR")
        c.drawString(0.5 * inch, height - 2.9 * inch, f"Tax Amount: €{1050 + 20 * i:.2f}")

        c.save()
        print(f"Created {filename}")

if __name__ == "__main__":
    create_cmr_pdfs(10)
    create_invoice_pdfs(10)
    print(f"Test documents created in {TEST_DOCS_DIR}!")