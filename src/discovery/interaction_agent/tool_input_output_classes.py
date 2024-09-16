from langchain_core.pydantic_v1 import BaseModel, Field
from typing import Type, List, Union, Tuple, Optional


class FillTextFieldInput(BaseModel):
    xpath_identifier: str = Field(description="The xpath of the text field.")
    value: str = Field(description="The value to be filled in the text field.", default="")


class FillTextFieldOutput(BaseModel):
    success: bool = Field(description="Whether the text field was filled successfully.")
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
]

AnyOutput = Union[
    ClickOutput,
    FillTextFieldOutput,
    GetPageSoupOutput,
    GetOutgoingRequestsOutput,
    SelectOptionOutput,
    NavigateOutput,
]
