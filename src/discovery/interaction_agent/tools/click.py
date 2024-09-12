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
from src.log import logger


class Input(BaseModel):
    xpath_identifier: str = Field(description="The xpath of the element to be clicked.")
    using_javascript: bool = Field(default=False, description="Whether to use JavaScript to click.")


class Output(BaseModel):
    success: bool = Field(description="Whether the element was clicked successfully.")
    message: str = Field(description="The message indicating the result of the operation.")
    page_diff: Optional[str] = Field(description="The diff of the page before and after clicking.")
    error: Optional[str] = Field(description="The error message if the operation failed.")


class Click(BaseTool):
    cf: Config
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
    args_schema: Type[BaseModel] = Input

    def _run(self, xpath_identifier: str, using_javascript: bool = False) -> Output:
        """Use the tool."""
        try:
            logger.info(f"Clicking element with name: {xpath_identifier}, using JavaScript: {using_javascript}")
            time.sleep(self.cf.selenium_rate)
            soup_before = BeautifulSoup(self.cf.driver.page_source, "html.parser")
            element = self.cf.driver.find_element(By.XPATH, xpath_identifier)
            if using_javascript:
                self.cf.driver.execute_script("arguments[0].click();", element)
            else:
                element.click()
            # TODO: diff stuff
            time.sleep(self.cf.selenium_rate)
            soup_after = BeautifulSoup(self.cf.driver.page_source, "html.parser")
            if soup_before == soup_after:
                res = (
                    f"Clicked element with name: {xpath_identifier}, but soup before and after are the same."
                    "Maybe check outgoing requests to see if something happened."
                )
                return Output(success=True, message=res)
            else:
                diff = str(
                    unified_diff(
                        soup_before.prettify().splitlines(),
                        soup_after.prettify().splitlines(),
                        lineterm="",
                    )
                )
                res = f"Clicked element with name: {xpath_identifier}."
                return Output(success=True, message=res, page_diff=diff.strip())
        except Exception as e:
            # logging.error(str(e))
            logging.error("Error: Failed to click element.")
            return Output(success=False, message="Failed to click element.", error=str(e))
