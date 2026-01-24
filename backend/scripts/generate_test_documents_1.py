from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.colors import grey


def create_standard_cmr(filename, data):
    c = canvas.Canvas(filename, pagesize=A4)
    width, height = A4

    # --- Draw the Grid (Based on your image) ---
    c.setLineWidth(0.2)
    c.setStrokeColor(grey)

    # Outer Frame
    c.rect(10 * mm, 10 * mm, 190 * mm, 277 * mm)

    # Vertical Dividers
    c.line(105 * mm, 180 * mm, 105 * mm, 287 * mm)  # Top half split
    c.line(140 * mm, 10 * mm, 140 * mm, 110 * mm)  # Bottom right split

    # Horizontal Dividers
    horiz_lines = [255, 225, 195, 180, 165, 110, 80, 50, 30]
    for h in horiz_lines:
        c.line(10 * mm, h * mm, 200 * mm, h * mm)

    # --- Box Headers (Multilingual as per image) ---
    c.setFont("Helvetica-Bold", 6)

    # Box 1: Sender
    c.drawString(12 * mm, 284 * mm, "1 Nosutitājs (nosaukums, adrese, valsts)")
    c.drawString(12 * mm, 281 * mm, "  Absender (Name, Anschrift, Land)")

    # Box 2: Consignee
    c.drawString(12 * mm, 252 * mm, "2 Saņēmējs (nosaukums, adrese, valsts)")
    c.drawString(12 * mm, 249 * mm, "  Empfänger (Name, Anschrift, Land)")

    # Box 16: Carrier (Right Side)
    c.drawString(107 * mm, 284 * mm, "16 Pārvadātājs (nosaukums, adrese, valsts)")
    c.drawString(107 * mm, 281 * mm, "   Frachtführer (Name, Anschrift, Land)")

    # --- Populate the Data ---
    c.setFont("Helvetica", 10)

    # Data from Source 1
    c.drawString(15 * mm, 275 * mm, data['shipper_name'])  # [cite: 3]
    c.drawString(15 * mm, 270 * mm, data['shipper_addr'])  # [cite: 4]

    c.drawString(15 * mm, 240 * mm, data['consignee_name'])  # [cite: 6]
    c.drawString(15 * mm, 235 * mm, data['consignee_addr'])  # [cite: 7]

    c.drawString(15 * mm, 158 * mm, f"Goods: {data['goods']}")  # [cite: 10]
    c.drawString(80 * mm, 158 * mm, f"Qty: {data['qty']}")  # [cite: 11]
    c.drawString(150 * mm, 158 * mm, f"Weight: {data['weight']}")  # [cite: 12]

    # --- Watermark (As seen in image center) ---
    c.setFont("Helvetica-Bold", 60)
    c.setFillGray(0.9)  # Light grey transparency effect
    c.drawCentredString(width / 2, 130 * mm, "CMR")  #

    c.showPage()
    c.save()


# Data Mapping from your upload
test_data = {
    "shipper_name": "ABC Logistics Ltd. 1",
    "shipper_addr": "124 Transport Street, London, UK",
    "consignee_name": "XYZ Trading Company 1",
    "consignee_addr": "457 Business Avenue, Paris, France",
    "goods": "Electronic Components 1",
    "qty": "51 boxes",
    "weight": "1260 kg"
}

if __name__ == "__main__":
    from pathlib import Path
    out = Path(__file__).parent.parent / "fixtures" / "synthetic_cmr_test.pdf"
    out.parent.mkdir(parents=True, exist_ok=True)
    create_standard_cmr(str(out), test_data)
    print(f"Created {out}")
