from typing import List, Dict, Tuple, Union

from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_core.messages import AnyMessage

from config import Config
from src.discovery.interaction_agent.tool_input_output import AnyInput, AnyOutput



class ToolContext(BaseModel):
    """Stores additional information about tool usage for each test of an interaction."""

    cf: Config
    tool_history: List[Tuple[str, AnyInput, AnyOutput]] = Field(default=[], description="The history of tool usage.")
    initial_uri: str = Field(description="The initial URI of the page.")

    class Config:
        arbitrary_types_allowed = True
