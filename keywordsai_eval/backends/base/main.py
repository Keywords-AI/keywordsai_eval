class BaseEvaluationBackend:
    def __init__(self, model_path: str, model_name: str):
        self.model_path = model_path
        self.model_name = model_name

    def load_model(self):
        raise NotImplementedError

    def predict(self, input_data: dict):
        raise NotImplementedError

    def evaluate(self, input_data: dict):
        raise NotImplementedError