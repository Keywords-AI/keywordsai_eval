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