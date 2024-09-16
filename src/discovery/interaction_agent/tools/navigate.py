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
from src.discovery.interaction_agent.tool_input_output_classes import NavigateInput, NavigateOutput


class Navigate(BaseTool):
    cf: Config
    context: ToolContext

    name = "navigate"
    description = (
        "Function: Navigate to a URL."
        "Args:"
        "  - url: str The URL to be navigated to. (required)"
        "Returns:"
        "  - success: bool Whether the URL was navigated to successfully."
        "  - message: str The message indicating the result of the operation."
        "  - error: str The error message if the operation failed."
    )
    args_schema: Type[BaseModel] = NavigateInput

    def _run(self, url: str) -> NavigateOutput:
        """Use the tool."""
        input = NavigateInput(url=url)
        try:
            logger.info(f"Navigating to the URL {url}")
            self.cf.driver.get(url)
            time.sleep(self.cf.selenium_rate)

            uri_now = self.cf.driver.current_url
            output = NavigateOutput(success=True, message=f"Navigated to the URL {url}. Actual URI now: {uri_now}")
            self.context.tool_history.append((self.name, input, output))
            return output
        except Exception as e:
            logging.error("Error: Failed to navigate to the URL.")
            output = NavigateOutput(success=False, message="Failed to navigate to the URL.", error=str(e))
            self.context.tool_history.append((self.name, input, output))
            return output
