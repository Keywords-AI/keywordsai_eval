from keywordsai_eval.backends.base import BaseEvaluationBackend
from .redis_ops import get_category, init_embeddings
import redis
from keywordsai_eval import settings
from keywordsai_eval.utils import Choices


class RedisEvaluationBackend(BaseEvaluationBackend):
    class ClassificationType(Choices):
        QUERY_TYPE = "query_type_categories"
        TOPIC = "topic_categories"
        
    def __init__(self, redis_client: redis.Redis | None = None):
        if not redis_client:
            self.redis_client = redis.Redis(**settings.REDIS_CLIENT)
        else:
            self.redis_client = redis_client
        init_embeddings(self.redis_client)

    def predict(self, query: str, type: str=ClassificationType.QUERY_TYPE) -> str:
        if type not in self.ClassificationType.choices():
            raise ValueError(f"Invalid type: {type}. Must be one of {self.ClassificationType.choices()}")
        return get_category(query, index_name=type, client=self.redis_client)

    def evaluate(self, query: str) -> str:
        return self.predict(query)
