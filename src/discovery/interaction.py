from typing import List

class Interaction:
    def __init__(self, name: str, description: str, input_fields: List[dict]) -> None:
        self.name = name
        self.description = description
        self.input_fields = input_fields
        self.tested = False
        self.behaviour = None
        self.apis_called = []
    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "description": self.description,
            "input_fields": self.input_fields
        }