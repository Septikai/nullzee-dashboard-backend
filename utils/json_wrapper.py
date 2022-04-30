

class JsonWrapper(dict):
    def __init__(self, *args, parent=None, key="", **kwargs):
        self.parent = parent
        self.key = key
        super(JsonWrapper, self).__init__(*args, **kwargs)

    def __getattr__(self, item):
        try:
            result = self[item]
            if isinstance(result, dict) and not isinstance(result, JsonWrapper):
                result = JsonWrapper(result, parent=self, key=item)
            return result
        except KeyError as e:
            raise AttributeError() from e

    def __setattr__(self, key, value):
        try:
            self[key] = value
            if self.parent is not None and self.key != "":
                self.parent.__setattr__(self.key, self)
        except KeyError as e:
            raise AttributeError() from e

    def __delattr__(self, item):
        try:
            del self[item]
        except KeyError as e:
            raise AttributeError() from e

    def to_dict(self):

        temp = JsonWrapper(self)
        del temp.parent
        del temp.key

        for key in temp:
            if isinstance(temp[key], JsonWrapper):
                temp[key] = temp[key].to_dict()

        return dict(temp)

    def parse_str_ints(self):
        for key in self:
            if isinstance(self[key], str) and self[key].isdigit():
                self[key] = int(self[key])
            elif type(self[key]) == dict:
                self[key] = self.from_dict(self[key])
            elif isinstance(self[key], str) and self[key] in ("true", "false"):
                self[key] = self[key] == "true"
            if isinstance(self[key], JsonWrapper):
                self[key].parse_str_ints()

    @classmethod
    def from_dict(cls, data: dict):
        return JsonWrapper(data)

