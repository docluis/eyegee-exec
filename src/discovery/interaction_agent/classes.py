from pydantic import BaseModel, Field
from typing import List, Union, Tuple, Optional, Any

from src.discovery.llm.model_classes import ApiModel


class FillTextFieldInput(BaseModel):
    xpath_identifier: str = Field(description="The xpath of the text field.")
    value: str = Field(description="The value to be filled in the text field.", default="")


class FillTextFieldOutput(BaseModel):
    success: bool = Field(description="Whether the text field was filled successfully.")
    message: str = Field(description="The message indicating the result of the operation.")
    error: Optional[str] = Field(default=None, description="The error message if the operation failed.")


class FillDateFieldInput(BaseModel):
    xpath_identifier: str = Field(description="The xpath of the date field.")
    year_value: str = Field(description="The value of the year to be filled in the date field.")
    month_value: str = Field(description="The value of the month to be filled in the date field.")
    day_value: str = Field(description="The value of the day to be filled in the date field.")


class FillDateFieldOutput(BaseModel):
    success: bool = Field(description="Whether the date field was filled successfully.")
    message: str = Field(description="The message indicating the result of the operation.")
    error: Optional[str] = Field(default=None, description="The error message if the operation failed.")


class ClickInput(BaseModel):
    xpath_identifier: str = Field(description="The xpath of the element to be clicked.")
    using_javascript: bool = Field(default=False, description="Whether to use JavaScript to click.")


class ClickOutput(BaseModel):
    success: bool = Field(description="Whether the element was clicked successfully.")
    message: str = Field(description="The message indicating the result of the operation.")
    page_diff: Optional[str] = Field(description="The diff of the page before and after clicking.")
    error: Optional[str] = Field(default=None, description="The error message if the operation failed.")


class GetPageSoupInput(BaseModel):
    filtered: bool = Field(default=True, description="Whether the page source should be filtered.")


class GetPageSoupOutput(BaseModel):
    success: bool = Field(description="Whether the page source was retrieved successfully.")
    message: str = Field(description="The message indicating the result of the operation.")
    page_source: Optional[str] = Field(description="The page source.")
    error: Optional[str] = Field(default=None, description="The error message if the operation failed.")


class GetElementInput(BaseModel):
    xpath_identifier: str = Field(description="The xpath of the element to be clicked.")


class GetElementOutput(BaseModel):
    success: bool = Field(description="Whether the element was retrieved successfully.")
    message: str = Field(description="The message indicating the result of the operation.")
    element: Optional[str] = Field(description="The element.")
    error: Optional[str] = Field(default=None, description="The error message if the operation failed.")


class GetOutgoingRequestsInput(BaseModel):
    filtered: bool = Field(default=True, description="Whether the outgoing requests should be filtered.")


class GetOutgoingRequestsOutput(BaseModel):
    success: bool = Field(description="Whether the outgoing requests were retrieved successfully.")
    message: str = Field(description="The message indicating the result of the operation.")
    outgoing_requests: Optional[str] = Field(description="The outgoing requests.")
    error: Optional[str] = Field(default=None, description="The error message if the operation failed.")


class SelectOptionInput(BaseModel):
    xpath_identifier: str = Field(description="The xpath of the element to be clicked.")
    visible_value: str = Field(description="The visible value of the option to be selected.")


class SelectOptionOutput(BaseModel):
    success: bool = Field(description="Whether the option was selected successfully.")
    message: str = Field(description="The message indicating the result of the operation.")
    error: Optional[str] = Field(default=None, description="The error message if the operation failed.")


class NavigateInput(BaseModel):
    url: str = Field(description="The URL to be navigated to.")


class NavigateOutput(BaseModel):
    success: bool = Field(description="Whether the navigation was successful.")
    message: str = Field(description="The message indicating the result of the operation.")
    error: Optional[str] = Field(default=None, description="The error message if the operation failed.")


AnyInput = Union[
    ClickInput,
    FillTextFieldInput,
    GetPageSoupInput,
    GetOutgoingRequestsInput,
    SelectOptionInput,
    NavigateInput,
    GetElementInput,
    FillDateFieldInput,
]

AnyOutput = Union[
    ClickOutput,
    FillTextFieldOutput,
    GetPageSoupOutput,
    GetOutgoingRequestsOutput,
    SelectOptionOutput,
    NavigateOutput,
    GetElementOutput,
    FillDateFieldOutput,
]


class HighHighLevelPlan(BaseModel):
    """High-level plan for testing an interaction feature."""

    approaches: List[str] = Field(
        description="Different approaches to test an interaction feature, should be in sorted order. Pay attention to the specified limit of approaches."
    )


class PlanModel(BaseModel):
    """Model for representing the plan for a single approach."""

    approach: str = Field(description="The approach for the interaction feature.")
    plan: List[str] = Field(description="The step-by-step plan for this approach.")


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
    outgoing_requests_after: List[ApiModel] = Field(default=None, description="The outgoing requests after the test.")
    # TODO: add a flag so the replanner does not need to check this test after checked once and replan is not needed
    checked: bool = Field(default=False, description="Whether the test has been checked for this approach.")
    in_report: bool = Field(default=False, description="Whether the test is in the final report.")


class Response(BaseModel):
    """Response to user."""

    text: str


class Act(BaseModel):
    """Action to perform."""

    action: Union[Response, PlanModel] = Field(
        description="Action to perform. If you want to respond to user, send a Response text. \n"
        "If you need to further use tools to get the answer, use PlanModel with the plan and approach."
    )
