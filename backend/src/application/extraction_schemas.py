"""Extraction schemas per document type for LLM field extraction."""
from typing import Any, Dict

DOCUMENT_TYPE_SCHEMAS: Dict[str, Dict[str, Any]] = {
    "CMR": {
        "type": "object",
        "properties": {
            "shipper_name": {"type": "string"},
            "shipper_address": {"type": "string"},
            "consignee_name": {"type": "string"},
            "consignee_address": {"type": "string"},
            "date_of_consignment": {"type": "string"},
            "place_of_consignment": {"type": "string"},
            "reference_number": {"type": "string"},
            "goods_description": {"type": "string"},
            "quantity": {"type": "string"},
            "weight": {"type": "string"},
        },
    },
    "INVOICE": {
        "type": "object",
        "properties": {
            "invoice_number": {"type": "string"},
            "invoice_date": {"type": "string"},
            "seller_name": {"type": "string"},
            "buyer_name": {"type": "string"},
            "total_amount": {"type": "string"},
            "currency": {"type": "string"},
            "tax_amount": {"type": "string"},
            "items": {"type": "array"},
        },
    },
    "DELIVERY_NOTE": {
        "type": "object",
        "properties": {
            "delivery_note_number": {"type": "string"},
            "delivery_date": {"type": "string"},
            "recipient_name": {"type": "string"},
            "recipient_address": {"type": "string"},
            "items": {"type": "array"},
        },
    },
}


def get_extraction_schema(document_type: str) -> Dict[str, Any]:
    """Return the extraction schema for the given document type."""
    return DOCUMENT_TYPE_SCHEMAS.get(document_type, {"type": "object", "properties": {}})
