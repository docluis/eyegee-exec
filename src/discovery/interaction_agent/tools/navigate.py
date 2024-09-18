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
from src.discovery.utils import extract_uri
from src.discovery.interaction_agent.tool_context import ToolContext
from src.log import logger
from src.discovery.interaction_agent.tool_input_output_classes import NavigateInput, NavigateOutput


class Navigate(BaseTool):
    cf: Config
    context: ToolContext

    name = "navigate"
    description = (
        "Function: Navigate to a URL.\n"
        "Args:\n"
        "  - url: str The URL to be navigated to. (required)\n"
        "Returns:\n"
        "  - success: bool Whether the URL was navigated to successfully.\n"
        "  - message: str The message indicating the result of the operation.\n"
        "  - error: str The error message if the operation failed.\n"
    )
    args_schema: Type[BaseModel] = NavigateInput

    def _run(self, url: str) -> NavigateOutput:
        """Use the tool."""
        input = NavigateInput(url=url)
        try:
            logger.debug(f"Navigating to the URL {url}")
            self.cf.driver.get(url)
            time.sleep(self.cf.selenium_rate)

            url_now = self.cf.driver.current_url
            output = NavigateOutput(success=True, message=f"Navigated to the URL {url}. Actual URL now: {url_now}")
            self.context.tool_history.append((self.name, input, output))
            self.context.add_observed_uri(extract_uri(self.cf.driver.current_url))
            return output
        except Exception as e:
            logging.debug("Error: Failed to navigate to the URL.")
            output = NavigateOutput(success=False, message="Failed to navigate to the URL.", error=str(e))
            self.context.tool_history.append((self.name, input, output))
            return output
