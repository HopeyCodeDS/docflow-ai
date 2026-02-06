from typing import Dict, Any, List
from ..entities.document import DocumentType
from ..entities.validation_result import ValidationStatus, ValidationError

# Config-driven validation rules for new document types
VALIDATION_RULES: Dict[str, Dict[str, List[str]]] = {
    "BILL_OF_LADING": {
        "required_fields": ["bl_number", "shipper_name", "consignee_name", "port_of_loading", "port_of_discharge"],
        "date_fields": ["date_of_issue"],
        "numeric_fields": [],
    },
    "AIR_WAYBILL": {
        "required_fields": ["awb_number", "shipper_name", "consignee_name", "airport_of_departure"],
        "date_fields": ["date_of_issue"],
        "numeric_fields": [],
    },
    "SEA_WAYBILL": {
        "required_fields": ["swb_number", "shipper_name", "consignee_name", "port_of_loading"],
        "date_fields": ["date_of_issue"],
        "numeric_fields": [],
    },
    "PACKING_LIST": {
        "required_fields": ["packing_list_number", "shipper_name"],
        "date_fields": ["date"],
        "numeric_fields": ["gross_weight", "net_weight"],
    },
    "CUSTOMS_DECLARATION": {
        "required_fields": ["declaration_number", "goods_description"],
        "date_fields": ["date_of_declaration"],
        "numeric_fields": ["customs_value", "duty_amount"],
    },
    "CERTIFICATE_OF_ORIGIN": {
        "required_fields": ["certificate_number", "country_of_origin", "exporter_name"],
        "date_fields": ["date_of_issue"],
        "numeric_fields": [],
    },
    "DANGEROUS_GOODS_DECLARATION": {
        "required_fields": ["un_number", "proper_shipping_name", "hazard_class", "shipper_name"],
        "date_fields": ["date_of_issue"],
        "numeric_fields": [],
    },
    "FREIGHT_BILL": {
        "required_fields": ["freight_bill_number", "shipper_name", "origin", "destination"],
        "date_fields": ["date_of_issue"],
        "numeric_fields": ["freight_charges", "total_amount"],
    },
}


class ValidationEngine:
    """Domain service for validating extracted data"""

    def validate(self, document_type: DocumentType, extracted_data: Dict[str, Any]) -> List[ValidationError]:
        """
        Validate extracted data based on document type.

        Args:
            document_type: Type of document
            extracted_data: Extracted structured data

        Returns:
            List of validation errors
        """
        errors = []

        # Legacy methods for original 3 types
        if document_type == DocumentType.CMR:
            errors.extend(self._validate_cmr(extracted_data))
        elif document_type == DocumentType.INVOICE:
            errors.extend(self._validate_invoice(extracted_data))
        elif document_type == DocumentType.DELIVERY_NOTE:
            errors.extend(self._validate_delivery_note(extracted_data))
        else:
            # Config-driven validation for new types
            type_value = document_type.value if document_type else "UNKNOWN"
            rules = VALIDATION_RULES.get(type_value)
            if rules:
                errors.extend(self._validate_required(extracted_data, rules.get("required_fields", [])))
                errors.extend(self._validate_dates(extracted_data, rules.get("date_fields", [])))
                errors.extend(self._validate_numerics(extracted_data, rules.get("numeric_fields", [])))

        return errors
    
    def _validate_cmr(self, data: Dict[str, Any]) -> List[ValidationError]:
        """Validate CMR document fields"""
        errors = []
        required_fields = ["shipper_name", "consignee_name", "date_of_consignment"]
        
        for field in required_fields:
            if not data.get(field):
                errors.append(ValidationError(
                    field=field,
                    message=f"Required field '{field}' is missing",
                    severity="error"
                ))
        
        # Validate date format if present
        if "date_of_consignment" in data and data["date_of_consignment"]:
            # Basic date validation (can be enhanced)
            if not isinstance(data["date_of_consignment"], str):
                errors.append(ValidationError(
                    field="date_of_consignment",
                    message="Date must be a valid string",
                    severity="error"
                ))
        
        return errors
    
    def _validate_invoice(self, data: Dict[str, Any]) -> List[ValidationError]:
        """Validate Invoice document fields"""
        errors = []
        required_fields = ["invoice_number", "invoice_date", "total_amount"]
        
        for field in required_fields:
            if not data.get(field):
                errors.append(ValidationError(
                    field=field,
                    message=f"Required field '{field}' is missing",
                    severity="error"
                ))
        
        # Validate amount format
        if "total_amount" in data and data["total_amount"]:
            try:
                float(str(data["total_amount"]).replace(",", "").replace("€", "").replace("$", ""))
            except ValueError:
                errors.append(ValidationError(
                    field="total_amount",
                    message="Total amount must be a valid number",
                    severity="error"
                ))
        
        return errors
    
    def _validate_delivery_note(self, data: Dict[str, Any]) -> List[ValidationError]:
        """Validate Delivery Note document fields"""
        errors = []
        required_fields = ["delivery_date", "recipient_name"]
        
        for field in required_fields:
            if not data.get(field):
                errors.append(ValidationError(
                    field=field,
                    message=f"Required field '{field}' is missing",
                    severity="error"
                ))
        
        return errors
    
    def _validate_required(self, data: Dict[str, Any], required_fields: List[str]) -> List[ValidationError]:
        """Validate that required fields are present."""
        errors = []
        for field in required_fields:
            if not data.get(field):
                errors.append(ValidationError(
                    field=field,
                    message=f"Required field '{field}' is missing",
                    severity="error"
                ))
        return errors

    def _validate_dates(self, data: Dict[str, Any], date_fields: List[str]) -> List[ValidationError]:
        """Validate that date fields are valid strings."""
        errors = []
        for field in date_fields:
            value = data.get(field)
            if value and not isinstance(value, str):
                errors.append(ValidationError(
                    field=field,
                    message=f"Date field '{field}' must be a valid string",
                    severity="error"
                ))
        return errors

    def _validate_numerics(self, data: Dict[str, Any], numeric_fields: List[str]) -> List[ValidationError]:
        """Validate that numeric fields are parseable numbers."""
        errors = []
        for field in numeric_fields:
            value = data.get(field)
            if value:
                try:
                    cleaned = str(value).replace(",", "").replace(" ", "")
                    for symbol in ["$", "EUR", "USD", "GBP", "CHF", "€", "£"]:
                        cleaned = cleaned.replace(symbol, "")
                    float(cleaned)
                except ValueError:
                    errors.append(ValidationError(
                        field=field,
                        message=f"Field '{field}' must be a valid number",
                        severity="error"
                    ))
        return errors

    def get_validation_status(self, errors: List[ValidationError]) -> ValidationStatus:
        """Determine validation status from errors"""
        if not errors:
            return ValidationStatus.PASSED
        
        has_errors = any(e.severity == "error" for e in errors)
        if has_errors:
            return ValidationStatus.FAILED
        
        return ValidationStatus.WARNING

