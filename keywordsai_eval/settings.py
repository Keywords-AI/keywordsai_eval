from os import getenv

# RedisEvaluationBackend settings
REDIS_HOST = getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(getenv("REDIS_PORT", "6379"))
REDIS_DB = int(getenv("REDIS_DB", "0"))

REDIS_CLIENT = {
    "host": REDIS_HOST,
    "port": REDIS_PORT,
    "db": REDIS_DB
}
EMBEDDING_MODEL_NAME = getenv("EMBEDDING_MODEL_NAME", "text-embedding-3-small")
CATEGORY_EMBEDDING_INDEX_NAME = getenv("CATEGORY_INDEX_NAME", "query_type_categories")
TOPIC_EMBEDDING_INDEX_NAME = getenv("EXPERTISE_INDEX_NAME", "expertise_categories")
# End of RedisEvaluationBackend settings