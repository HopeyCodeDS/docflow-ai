from datetime import datetime
from sqlalchemy import Column, String, Integer, BigInteger, Text, ForeignKey, JSON, DateTime
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
import uuid

from .database import Base


class UserModel(Base):
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(20), nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)


class DocumentModel(Base):
    __tablename__ = "documents"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    original_filename = Column(String(255), nullable=False)
    file_type = Column(String(10), nullable=False)
    file_size = Column(BigInteger, nullable=False)
    storage_path = Column(String(500), nullable=False)
    uploaded_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    uploaded_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    status = Column(String(20), nullable=False)
    document_type = Column(String(50))
    version = Column(Integer, default=1)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    extractions = relationship("ExtractionModel", back_populates="document", cascade="all, delete-orphan")
    reviews = relationship("ReviewModel", back_populates="document", cascade="all, delete-orphan")
    exports = relationship("ExportModel", back_populates="document", cascade="all, delete-orphan")
    audit_trails = relationship("AuditTrailModel", back_populates="document", cascade="all, delete-orphan")


class ExtractionModel(Base):
    __tablename__ = "extractions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id = Column(UUID(as_uuid=True), ForeignKey("documents.id"), nullable=False)
    extraction_method = Column(String(20), nullable=False)
    raw_text = Column(Text)
    structured_data = Column(JSONB, nullable=False)
    confidence_scores = Column(JSONB)
    extracted_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    extraction_metadata = Column(JSONB)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    
    # Relationships
    document = relationship("DocumentModel", back_populates="extractions")
    validation_results = relationship("ValidationResultModel", back_populates="extraction", cascade="all, delete-orphan")


class ValidationResultModel(Base):
    __tablename__ = "validation_results"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    extraction_id = Column(UUID(as_uuid=True), ForeignKey("extractions.id"), nullable=False)
    validation_rules = Column(JSONB, nullable=False)
    validation_status = Column(String(20), nullable=False)
    validation_errors = Column(JSONB)
    validated_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    
    # Relationships
    extraction = relationship("ExtractionModel", back_populates="validation_results")


class ReviewModel(Base):
    __tablename__ = "reviews"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id = Column(UUID(as_uuid=True), ForeignKey("documents.id"), nullable=False)
    reviewed_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    reviewed_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    corrections = Column(JSONB, nullable=False)
    review_status = Column(String(20), nullable=False)
    review_notes = Column(Text)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    
    # Relationships
    document = relationship("DocumentModel", back_populates="reviews")


class AuditTrailModel(Base):
    __tablename__ = "audit_trails"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id = Column(UUID(as_uuid=True), ForeignKey("documents.id"), nullable=False)
    action = Column(String(50), nullable=False)
    performed_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    performed_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    changes = Column(JSONB)
    audit_metadata = Column(JSONB)
    
    # Relationships
    document = relationship("DocumentModel", back_populates="audit_trails")


class ExportModel(Base):
    __tablename__ = "exports"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id = Column(UUID(as_uuid=True), ForeignKey("documents.id"), nullable=False)
    exported_to = Column(String(255), nullable=False)
    export_payload = Column(JSONB, nullable=False)
    export_status = Column(String(20), nullable=False)
    exported_at = Column(DateTime(timezone=True))
    retry_count = Column(Integer, default=0)
    error_message = Column(Text)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    
    # Relationships
    document = relationship("DocumentModel", back_populates="exports")

