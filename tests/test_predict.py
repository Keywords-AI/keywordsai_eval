from keywordsai_eval.backends.redis_stack import RedisEvaluationBackend

def test_predict():
    kai_eval = RedisEvaluationBackend()
    result = kai_eval.predict("How to code \"Hello worlds\" in Python")

    assert result == "Coding", f"The result was {result} instead of Coding"

if __name__ == "__main__":
    test_predict()