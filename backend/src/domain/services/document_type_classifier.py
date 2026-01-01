from typing import Dict, Any
from ..entities.document import DocumentType


class DocumentTypeClassifier:
    """Domain service for classifying document types"""
    
    def classify(self, content: str, metadata: Dict[str, Any] = None) -> DocumentType:
        """
        Classify document type based on content and metadata.
        
        Args:
            content: Extracted text content
            metadata: Additional metadata (filename, structure, etc.)
        
        Returns:
            DocumentType enum
        """
        content_upper = content.upper()
        metadata = metadata or {}
        
        # Check for CMR indicators
        if any(keyword in content_upper for keyword in ["CMR", "CONSIGNMENT NOTE", "TRANSPORT DOCUMENT"]):
            return DocumentType.CMR
        
        # Check for Invoice indicators
        if any(keyword in content_upper for keyword in ["INVOICE", "BILL TO", "INVOICE NUMBER", "TAX INVOICE"]):
            return DocumentType.INVOICE
        
        # Check for Delivery Note indicators
        if any(keyword in content_upper for keyword in ["DELIVERY NOTE", "DELIVERY RECEIPT", "PROOF OF DELIVERY"]):
            return DocumentType.DELIVERY_NOTE
        
        # Check filename hints
        filename = metadata.get("filename", "").upper()
        if "CMR" in filename:
            return DocumentType.CMR
        if "INVOICE" in filename or "INV" in filename:
            return DocumentType.INVOICE
        if "DELIVERY" in filename or "DEL" in filename:
            return DocumentType.DELIVERY_NOTE
        
        return DocumentType.UNKNOWN

