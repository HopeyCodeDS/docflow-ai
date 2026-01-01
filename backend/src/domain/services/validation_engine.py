from typing import Dict, Any, List
from ..entities.document import DocumentType
from ..entities.validation_result import ValidationStatus, ValidationError


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
        
        if document_type == DocumentType.CMR:
            errors.extend(self._validate_cmr(extracted_data))
        elif document_type == DocumentType.INVOICE:
            errors.extend(self._validate_invoice(extracted_data))
        elif document_type == DocumentType.DELIVERY_NOTE:
            errors.extend(self._validate_delivery_note(extracted_data))
        
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
    
    def get_validation_status(self, errors: List[ValidationError]) -> ValidationStatus:
        """Determine validation status from errors"""
        if not errors:
            return ValidationStatus.PASSED
        
        has_errors = any(e.severity == "error" for e in errors)
        if has_errors:
            return ValidationStatus.FAILED
        
        return ValidationStatus.WARNING

