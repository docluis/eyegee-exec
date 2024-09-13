from difflib import unified_diff
import os
import time
import logging
from bs4 import BeautifulSoup
import pandas as pd
from langchain_core.tools import BaseTool
from langchain_core.pydantic_v1 import BaseModel, Field
from typing import Type, List, Union, Tuple, Optional

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys

from config import Config
from src.discovery.interaction_agent.tool_context import ToolContext
from src.log import logger
from src.discovery.interaction_agent.tool_input_output import ClickInput, ClickOutput


class Click(BaseTool):
    cf: Config
    context: ToolContext
    # context: Context

    name = "click"
    description = (
        "Function: Click on an element."
        "Args:"
        "  - xpath_identifier: str The xpath of the element to be clicked. (required)"
        "  - using_javascript: bool Whether to use JavaScript to click. (optional, default: False)"
        "Returns:"
        "  - success: bool Whether the element was clicked successfully."
        "  - message: str The message indicating the result of the operation."
        "  - page_diff: str The diff of the page before and after clicking."
        "  - error: str The error message if the operation failed."
    )
    args_schema: Type[BaseModel] = ClickInput

    def _run(self, xpath_identifier: str, using_javascript: bool = False) -> ClickOutput:
        """Use the tool."""
        input = ClickInput(xpath_identifier=xpath_identifier, using_javascript=using_javascript)
        try:
            logger.info(f"Clicking element with name: {xpath_identifier}, using JavaScript: {using_javascript}")
            time.sleep(self.cf.selenium_rate)
            soup_before = BeautifulSoup(self.cf.driver.page_source, "html.parser")
            element = self.cf.driver.find_element(By.XPATH, xpath_identifier)
            if using_javascript:
                self.cf.driver.execute_script("arguments[0].click();", element)
            else:
                element.click()

            time.sleep(self.cf.selenium_rate)
            soup_after = BeautifulSoup(self.cf.driver.page_source, "html.parser")
            if soup_before == soup_after:
                message = (
                    f"Clicked element with name: {xpath_identifier}, but soup before and after are the same.\n"
                    "Maybe check outgoing requests to see if something happened."
                )
                page_diff = None
            else:
                message = f"Clicked element with name: {xpath_identifier}."
                page_diff = str(
                    unified_diff(
                        soup_before.prettify().splitlines(),
                        soup_after.prettify().splitlines(),
                        lineterm="",
                    )
                ).strip()
            output = ClickOutput(success=True, message=message, page_diff=page_diff)
            self.context.tool_history.append((self.name, input, output))
            return output
        except Exception as e:
            # logging.error(str(e))
            logging.error("Error: Failed to click element.")
            output = ClickOutput(success=False, message="Failed to click element.", error=str(e))
            self.context.tool_history.append((self.name, input, output))
            return output
