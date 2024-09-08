from os import getenv

# RedisEvaluationBackend settings
REDIS_HOST = getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(getenv("REDIS_PORT", "6379"))
REDIS_DB = int(getenv("REDIS_DB", "0"))

REDIS_CLIENT = {
    "host": REDIS_HOST,
    "port": REDIS_PORT,
    "db": REDIS_DB,
    "decode_responses": True,
}

EMBEDDING_MODEL_NAME_KEY = "keywordsai_eval:embedding_model_name" # Key to store the current embedding model name
EMBEDDING_MODEL_NAME = getenv("EMBEDDING_MODEL_NAME", "text-embedding-3-large") # Embedding model for creating embeddings for both the query and the categories
QUERY_TYPE_EMBEDDING_INDEX_NAME = getenv("QUERY_TYPE_INDEX_NAME", "query_type_categories") # Index name for the query type embeddings (search query_type_categories.json in codebase to see more)
TOPIC_EMBEDDING_INDEX_NAME = getenv("TOPIC_INDEX_NAME", "topic_categories") # Index name for the topic embeddings (search topic_categories.json in codebase to see more)
# End of RedisEvaluationBackend settings