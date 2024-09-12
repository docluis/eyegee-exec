import json
import os
import time
import logging
import pandas as pd
from langchain_core.tools import BaseTool
from langchain_core.pydantic_v1 import BaseModel, Field
from typing import Type, List, Union, Tuple, Optional

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys

from config import Config

# from src.discovery.interaction_agent.context import Context
from src.log import logger


class Input(BaseModel):
    xpath_identifier: str = Field(description="The xpath of the text field.")
    value: str = Field(description="The value to be filled in the text field.", default="")


class Output(BaseModel):
    success: bool = Field(description="Whether the text field was filled successfully.")
    message: str = Field(description="The message indicating the result of the operation.")
    error: Optional[str] = Field(description="The error message if the operation failed.")


class FillTextField(BaseTool):
    cf: Config
    # context: Context

    name = "fill_text_field"
    description = (
        "Function: Fill in a text field."
        "Args:"
        "  - xpath_identifier: str The xpath of the element to be clicked. (required)"
        "  - value: str The value to be filled in the text field. (optional, default: '')"
        "Returns:"
        "  - success: bool Whether the text field was filled successfully."
        "  - message: str The message indicating the result of the operation."
        "  - error: str The error message if the operation failed."
    )
    args_schema: Type[BaseModel] = Input

    def _run(self, xpath_identifier: str, value: str = "") -> Output:
        """Use the tool."""
        try:
            # input_dict = json.loads(input)
            # xpath_identifier = input_dict["xpath_identifier"]
            # value = input_dict["value"]
            logger.info(f"Filling in the text field {xpath_identifier} with {value}")
            element = self.cf.driver.find_element(By.XPATH, xpath_identifier)
            # clear the field first
            element.clear()
            element.send_keys(Keys.CONTROL + "a")
            element.send_keys(Keys.DELETE)
            element.send_keys(50 * Keys.BACKSPACE)

            element.send_keys(value)
            actual_value = element.get_attribute("value")

            # self.context.note_uri(self.cf)
            return Output(success=True, message=f"Filled in the text field {xpath_identifier} with {value}.")
        except Exception as e:
            # logging.error(str(e))
            logging.error("Error: Failed to fill in the text field.")
            return Output(success=False, message="Failed to fill in the text field.", error=str(e))
