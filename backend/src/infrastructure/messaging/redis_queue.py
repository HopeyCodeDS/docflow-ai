import json
import redis
from typing import Any, Dict, Optional
from uuid import UUID


class RedisQueue:
    """Redis-based message queue"""
    
    def __init__(self, redis_url: str):
        self.redis_client = redis.from_url(redis_url)
    
    def enqueue(self, queue_name: str, task: Dict[str, Any]) -> None:
        """Enqueue a task"""
        self.redis_client.lpush(queue_name, json.dumps(task))
    
    def dequeue(self, queue_name: str, timeout: int = 0) -> Optional[Dict[str, Any]]:
        """Dequeue a task"""
        result = self.redis_client.brpop(queue_name, timeout=timeout)
        if result:
            _, data = result
            return json.loads(data)
        return None
    
    def get_queue_length(self, queue_name: str) -> int:
        """Get queue length"""
        return self.redis_client.llen(queue_name)

