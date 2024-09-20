from difflib import unified_diff
import os
import time
import logging
from bs4 import BeautifulSoup
from langchain_core.tools import BaseTool
from langchain_core.pydantic_v1 import BaseModel, Field
from typing import Type, List, Union, Tuple, Optional

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys

from config import Config
from src.discovery.utils import extract_uri, filter_html
from src.discovery.interaction_agent.tool_context import ToolContext
from src.log import logger
from src.discovery.interaction_agent.classes import ClickInput, ClickOutput


class Click(BaseTool):
    cf: Config
    context: ToolContext
    # context: Context

    name = "click"
    description = (
        "Function: Click on an element.\n"
        "Args:\n"
        "  - xpath_identifier: str The xpath of the element to be clicked. (required)\n"
        "  - using_javascript: bool Whether to use JavaScript to click. (optional, default: True)\n"
        "Returns:\n"
        "  - success: bool Whether the element was clicked successfully.\n"
        "  - message: str The message indicating the result of the operation.\n"
        "  - page_diff: str The diff of the page before and after clicking.\n"
        "  - error: str The error message if the operation failed.\n"
    )
    args_schema: Type[BaseModel] = ClickInput

    def _run(self, xpath_identifier: str, using_javascript: bool = True) -> ClickOutput:
        """Use the tool."""
        input = ClickInput(xpath_identifier=xpath_identifier, using_javascript=using_javascript)
        try:
            logger.debug(f"Clicking element with name: {xpath_identifier}, using JavaScript: {using_javascript}")
            time.sleep(self.cf.selenium_rate)
            soup_before = BeautifulSoup(self.cf.driver.page_source, "html.parser")
            element = self.cf.driver.find_element(By.XPATH, xpath_identifier)
            if using_javascript:
                self.cf.driver.execute_script("arguments[0].click();", element)
            else:
                element.click()

            time.sleep(self.cf.selenium_rate)
            soup_after = BeautifulSoup(self.cf.driver.page_source, "html.parser")
            message = f"Clicked element with name: {xpath_identifier}. Current URL: {self.cf.driver.current_url}"
            page_diff = unified_diff(
                filter_html(soup_before).prettify().splitlines(),
                filter_html(soup_after).prettify().splitlines(),
                lineterm="",
            )
            page_diff = "\n".join(list(page_diff)).strip()

            output = ClickOutput(success=True, message=message, page_diff=page_diff)
            self.context.tool_history.append((self.name, input, output))
            self.context.add_observed_uri(extract_uri(self.cf.driver.current_url))
            return output
        except Exception as e:
            # logging.error(str(e))
            logging.debug("Error: Failed to click element.")
            output = ClickOutput(
                success=False,
                message=f"Failed to click element. Current URL: {self.cf.driver.current_url}",
                error=str(e),
            )
            self.context.tool_history.append((self.name, input, output))
            return output
