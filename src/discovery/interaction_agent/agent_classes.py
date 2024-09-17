from typing import List, Tuple, Any, Dict, Union
from langchain_core.pydantic_v1 import BaseModel, Field

from src.discovery.interaction_agent.tool_input_output_classes import AnyInput, AnyOutput

class HighHighLevelPlan(BaseModel):
    """High-level plan for testing an interaction feature."""

    approaches: List[str] = Field(
        description="Different approaches to test an interaction feature, should be in sorted order"
    )


class PlanModel(BaseModel):
    """Model for representing the plan for a single approach."""

    approach: str = Field(description="The approach for the interaction feature.")
    plan: List[str] = Field(description="The step-by-step plan for this approach.")


# class HighLevelPlan(BaseModel):
#     """High-level plan for each approach."""

#     plan: List[PlanModel] = Field(description="Detailed plans for each approach")


class CompletedTask(BaseModel):
    """Model for representing a completed step of a plan for a single approach."""

    task: str = Field(description="The task that was executed.")
    status: str = Field(default="pending", description="The status of the task.")
    result: str = Field(default="", description="The result of the task.")
    tool_history: List[Tuple[str, AnyInput, AnyOutput]] = Field(default=[], description="The history of tool usage.")


class TestModel(BaseModel):
    """Model for representing a test for a single approach."""

    approach: str = Field(description="The approach for the interaction feature.")
    plan: PlanModel = Field(description="The plan for this approach.")
    steps: List[CompletedTask] = Field(description="The steps executed for this approach.")
    soup_before_str: str = Field(description="The soup before the test.")
    soup_after_str: str = Field(default=None, description="The soup after the test.")
    # outgoing_requests_before: List[Dict] = Field(description="The outgoing requests before the test.")
    outgoing_requests_after: str = Field(default=None, description="The outgoing requests after the test. (JSON)")
    # TODO: add a flag so the replanner does not need to check this test after checked once and replan is not needed

class Response(BaseModel):
    """Response to user."""

    text: str


class Act(BaseModel):
    """Action to perform."""

    action: Union[Response, PlanModel] = Field(
        description="Action to perform. If you want to respond to user, send a Response text. \n"
        "If you need to further use tools to get the answer, use PlanModel with the plan and approach."
    )