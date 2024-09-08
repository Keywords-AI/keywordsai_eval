from keywordsai_eval.backends.redis_stack import RedisEvaluationBackend

def test_initializtion():
    backend = RedisEvaluationBackend()
    assert backend is not RedisEvaluationBackend

if __name__ == "__main__":
    test_initializtion()