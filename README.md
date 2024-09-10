# Keywords AI Eval
Keywords AI eval is an open-sourced evaluation package for classification


## Get started
Installation
```
pip install keywordsai-eval
```


## Available backends
- keywordsai_eval.backends.redis_stack import RedisEvaluationBackend

### Redis-Stack
```
from keywordsai_eval.backends.redis_stack import RedisEvaluationBackend
```
Setup:

1. Install [redis-stack-server](https://redis.io/docs/latest/operate/oss_and_stack/install/install-stack/), an in memory dictionary storage that can be used as a vector database for our use case
2. Run redis-stack, either on a remote service or locally:
```
redis-stack-server
```
Keep it live in the background.
3. Set up the environment variables for this backend:
```
REDIS_HOST=HOST
REDIS_PORT=PORT
REDIS_DB=YOUR_PORT
```
Alternatively, you can override the redis connection by initializing a redis client before using the backend
```
import redis
client = redis.Redis(host="localhost", port=6379, db=0)
backend = RedisEvaluationBackend(redis_client=client)
```
4. Run the example:
```
from keywordsai_eval.backends.redis_stack import RedisEvaluationBackend

def test_code_predict():
    kai_eval = RedisEvaluationBackend()
    result = kai_eval.predict("How to code \"Hello worlds\" in Python")

    assert result == "Coding", f"The result was {result} instead of Coding"

def test_writing_predict():
    kai_eval = RedisEvaluationBackend()
    result = kai_eval.predict("How to write a novel")
    assert result == "Writing", f"The result was {result} instead of Writing"

if __name__ == "__main__":
    test_code_predict()
    test_writing_predict()
```

