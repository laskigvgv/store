import json
import uuid
import redis
from typing import Any


class RedisQueue(object):
    """
    Class to create a redis connection to a queue.
    Used for adding tasks to queue.
    """

    def __init__(
        self,
        host: str = "localhost",
        port: int = 6379,
        queue_name: str = "notification_queue",
        timeout: int = 300,
        queue_db: int = 14,
    ):
        self.client = redis.Redis(host=host, port=port, db=queue_db)
        self.queue_name = queue_name
        self.timeout = timeout

    def add_to_queue(self, msg_body: str, wait_for_response: Any = None) -> dict | bool:
        req = {"msg_body": msg_body, "id": str(uuid.uuid4())}
        if wait_for_response is not None:
            req["wait_for_response"] = wait_for_response
        request = json.dumps(req).encode("utf-8")
        self.client.lpush(self.queue_name, request)
        if not (result := self.client.brpop(req["id"], timeout=self.timeout)):
            return False
        _, response = result
        response = json.loads(response)
        return json.loads(response["result"])

    def add_to_task_queue(self, msg_body: str) -> bool:
        request = json.dumps(msg_body).encode("utf-8")
        self.client.lpush(self.queue_name, request)
        return True

    def close(self):
        pass
