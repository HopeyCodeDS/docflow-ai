from typing import Dict, Any, Optional
from datetime import datetime
from uuid import UUID, uuid4
import json

from ..messaging.redis_queue import RedisQueue


class DeadLetterQueue:
    """Dead letter queue for failed jobs"""
    
    def __init__(self, redis_queue: RedisQueue, dlq_name: str = "dlq"):
        self.redis_queue = redis_queue
        self.dlq_name = dlq_name
    
    def enqueue_failed_job(
        self,
        original_queue: str,
        job_data: Dict[str, Any],
        error_message: str,
        retry_count: int
    ) -> None:
        """Add failed job to dead letter queue"""
        dlq_entry = {
            "id": str(uuid4()),
            "original_queue": original_queue,
            "job_data": job_data,
            "error_message": error_message,
            "retry_count": retry_count,
            "failed_at": datetime.utcnow().isoformat(),
        }
        self.redis_queue.enqueue(self.dlq_name, dlq_entry)
    
    def get_failed_jobs(self, limit: int = 100) -> list[Dict[str, Any]]:
        """Get failed jobs from DLQ (for manual review)"""
        jobs = []
        for _ in range(limit):
            job = self.redis_queue.dequeue(self.dlq_name, timeout=0)
            if job:
                jobs.append(job)
            else:
                break
        return jobs

