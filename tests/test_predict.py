from keywordsai_eval.backends.redis_stack import RedisEvaluationBackend

def test_predict():
    kai_eval = RedisEvaluationBackend()
    result = kai_eval.predict("How do I create a new branch in git?")

    assert result == "Coding", f"The result was {result} instead of Coding"

if __name__ == "__main__":
    test_predict()