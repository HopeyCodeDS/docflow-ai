from typing import Dict, Any
from prometheus_client import Counter, Histogram, Gauge
import time


# Metrics
document_uploads_total = Counter(
    'docflow_document_uploads_total',
    'Total number of document uploads'
)

document_extractions_total = Counter(
    'docflow_document_extractions_total',
    'Total number of document extractions',
    ['status']  # success, failure
)

extraction_duration_seconds = Histogram(
    'docflow_extraction_duration_seconds',
    'Time spent on document extraction',
    buckets=[1, 5, 10, 30, 60, 120]
)

validation_results_total = Counter(
    'docflow_validation_results_total',
    'Total number of validation results',
    ['status']  # passed, failed, warning
)

export_attempts_total = Counter(
    'docflow_export_attempts_total',
    'Total number of export attempts',
    ['status']  # success, failure
)

queue_depth = Gauge(
    'docflow_queue_depth',
    'Current queue depth',
    ['queue_name']
)


class MetricsCollector:
    """Metrics collection helper"""
    
    @staticmethod
    def record_document_upload():
        """Record document upload"""
        document_uploads_total.inc()
    
    @staticmethod
    def record_extraction(success: bool, duration: float):
        """Record extraction"""
        status = "success" if success else "failure"
        document_extractions_total.labels(status=status).inc()
        extraction_duration_seconds.observe(duration)
    
    @staticmethod
    def record_validation(status: str):
        """Record validation result"""
        validation_results_total.labels(status=status.lower()).inc()
    
    @staticmethod
    def record_export(success: bool):
        """Record export attempt"""
        status = "success" if success else "failure"
        export_attempts_total.labels(status=status).inc()
    
    @staticmethod
    def update_queue_depth(queue_name: str, depth: int):
        """Update queue depth"""
        queue_depth.labels(queue_name=queue_name).set(depth)

