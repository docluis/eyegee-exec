class UserInput:
    def __init__(self, name: str, input_type: str) -> None:
        self.name = name
        self.input_type = input_type


class Interaction:
    def __init__(
        self, name: str, description: str, user_inputs: list[UserInput]
    ) -> None:  # TODO: add observerd behavior
        self.name = name
        self.description = description
        self.user_inputs = user_inputs
