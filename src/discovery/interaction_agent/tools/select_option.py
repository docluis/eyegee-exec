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
from src.discovery.interaction_agent.tool_context import ToolContext
from src.log import logger
from src.discovery.interaction_agent.tool_input_output_classes import SelectOptionInput, SelectOptionOutput


class SelectOption(BaseTool):
    cf: Config
    context: ToolContext

    name = "select_option"
    description = (
        "Function: Select an option from a select menu."
        "Args:"
        "  - xpath_identifier: str The xpath of the select menu. (required)"
        "  - visible_value: str The visible value of the option to be selected. (required)"
        "Returns:"
        "  - success: bool Whether the option was selected successfully."
        "  - message: str The message indicating the result of the operation."
        "  - error: str The error message if the operation failed."
    )
    args_schema: Type[BaseModel] = SelectOptionInput

    def _run(self, xpath_identifier: str, visible_value: str = "") -> SelectOptionOutput:
        """Use the tool."""
        input = SelectOptionInput(xpath_identifier=xpath_identifier, visible_value=visible_value)
        try:
            logger.info(f"Selecting option with value: {visible_value}")
            element = self.cf.driver.find_element(By.XPATH, xpath_identifier)
            select = Select(element)
            select.select_by_visible_text(visible_value)

            actual_value = select.first_selected_option.text

            output = SelectOptionOutput(
                success=True, message=f"Selected option: {xpath_identifier} with value: {visible_value}. Actual value now: {actual_value}."
            )
            self.context.tool_history.append((self.name, input, output))
            return output
        except Exception as e:
            logging.error("Error: Failed to select option.")
            output = SelectOptionOutput(success=False, message="Failed to select option.", error=str(e))
            self.context.tool_history.append((self.name, input, output))
            return output
