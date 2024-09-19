


class Parameter:
    def __init__(self, name: str, param_type: str) -> None:
        self.name = name
        self.observed_values = []
        self.param_type = param_type
    
    def add_observed_value(self, value: str) -> None:
        if value not in self.observed_values:
            self.observed_values.append(value)


class Api:
    def __init__(self, method: str, path: str) -> None:
        self.method = method
        self.path = path

        self.params = []

    def add_param(self, param_name: str, param_type: str) -> None:
        found = self.get_param(param_name)
        if found is None:
            self.params.append(Parameter(param_name, param_type))

    def get_param(self, param_name: str) -> Parameter:
        for param in self.params:
            if param.name == param_name:
                return param
        return None
        
