class DialogResponse:
    def __init__(self, response, inputText=None, confidence=None):
        self.response = response
        self.input = inputText
        self.confidence = confidence
