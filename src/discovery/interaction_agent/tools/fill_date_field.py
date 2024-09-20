import json
import os
import time
import logging
from langchain_core.tools import BaseTool
from langchain_core.pydantic_v1 import BaseModel, Field
from typing import Type, List, Union, Tuple, Optional

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys

from config import Config

# from src.discovery.interaction_agent.context import Context
from src.discovery.utils import extract_uri
from src.discovery.interaction_agent.tool_context import ToolContext
from src.log import logger
from src.discovery.interaction_agent.classes import FillDateFieldInput, FillDateFieldOutput


class FillDateField(BaseTool):
    cf: Config
    context: ToolContext

    name = "fill_date_field"
    description = (
        "Function: Fill in a date field.\n"
        "Args:\n"
        "  - xpath_identifier: str The xpath of the element to be clicked. (required)\n"
        "  - year_value: str The value of the year to be filled in the date field. (required)\n"
        "  - month_value: str The value of the month to be filled in the date field. (required)\n"
        "  - day_value: str The value of the day to be filled in the date field. (required)\n"
        "Returns:\n"
        "  - success: bool Whether the date field was filled successfully.\n"
        "  - message: str The message indicating the result of the operation.\n"
        "  - error: str The error message if the operation failed.\n"
    )
    args_schema: Type[BaseModel] = FillDateFieldInput

    def _run(self, xpath_identifier: str, year_value: str, month_value: str, day_value: str) -> FillDateFieldOutput:
        """Use the tool."""
        input = FillDateFieldInput(xpath_identifier=xpath_identifier, year_value=year_value, month_value=month_value, day_value=day_value)
        try:
            formatted_date = f"{month_value}-{day_value}-{year_value}" # match the american locale
            logger.debug(f"Filling in the date field {xpath_identifier} with {formatted_date}")
            element = self.cf.driver.find_element(By.XPATH, xpath_identifier)
            # clear the field first
            element.clear()
            element.send_keys(Keys.CONTROL + "a")
            element.send_keys(Keys.DELETE)
            element.send_keys(50 * Keys.BACKSPACE)

            element.send_keys(formatted_date)
            actual_value = element.get_attribute("value")

            # self.context.note_uri(self.cf)
            output = FillDateFieldOutput(
                success=True, message=f"Filled in the date field {xpath_identifier} with {formatted_date}."
            )
            self.context.tool_history.append((self.name, input, output))
            self.context.add_observed_uri(extract_uri(self.cf.driver.current_url))
            return output
        except Exception as e:
            # logging.error(str(e))
            logging.debug("Error: Failed to fill in the date field.")
            output = FillDateFieldOutput(success=False, message="Failed to fill in the date field.", error=str(e))
            self.context.tool_history.append((self.name, input, output))
            return output
