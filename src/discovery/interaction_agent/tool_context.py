from typing import List, Dict, Tuple, Union

from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_core.messages import AnyMessage

from config import Config
from src.discovery.interaction_agent.tool_input_output_classes import AnyInput, AnyOutput



class ToolContext(BaseModel):
    """Stores additional information about tool usage for each test of an interaction."""

    cf: Config
    tool_history: List[Tuple[str, AnyInput, AnyOutput]] = Field(default=[], description="The history of tool usage.")
    initial_uri: str = Field(description="The initial URI of the page.")
    observed_uris: List[str] = Field(default=[], description="The list of URIs observed during the interaction.")

    class Config:
        arbitrary_types_allowed = True

    def get_tool_history_reset(self):
        tool_history = self.tool_history
        self.tool_history = []
        return tool_history
    
    def get_observed_uris(self):
        observed_uris = self.observed_uris
        return observed_uris
    
    def add_observed_uri(self, uri: str):
        if uri not in self.observed_uris:
            self.observed_uris.append(uri)
