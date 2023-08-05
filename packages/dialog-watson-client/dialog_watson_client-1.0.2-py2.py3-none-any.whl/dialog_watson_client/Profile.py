class Profile:
    def __init__(self, client_id):
        self.client_id = client_id
        self._data = {}

    def get_data_value(self, key):
        return self._data[key]

    def set_data(self, data):
        self._data = data

    def get_data(self):
        return self._data

    def set_data_value(self, key, value):
        self._data[key] = value

    def load_data(self, jsonDatas):
        self._data = {}
        for jsonData in jsonDatas:
            self._data[jsonData["name"]] = jsonData["value"]
