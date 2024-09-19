import json
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

# from src.discovery.interaction_agent.context import Context
from src.discovery.utils import extract_uri, filter_html
from src.discovery.interaction_agent.tool_context import ToolContext
from src.log import logger
from src.discovery.interaction_agent.classes import GetElementInput, GetElementOutput


class GetElement(BaseTool):
    cf: Config
    context: ToolContext

    name = "get_element"
    description = (
        "Function: Get the element. Use this tool to get the inspect the current value or text of the element.\n"
        "Args:\n"
        "  - xpath_identifier: str The xpath of the element to be clicked. (required)\n"
        "Returns:\n"
        "  - success: bool Whether the element was retrieved successfully.\n"
        "  - message: str The message indicating the result of the operation.\n"
        "  - element: str The element.\n"
        "  - error: str The error message if the operation failed.\n"
    )
    args_schema: Type[BaseModel] = GetElementInput

    def _run(self, xpath_identifier: str) -> GetElementOutput:
        """Use the tool."""
        input = GetElementInput(xpath_identifier=xpath_identifier)
        try:
            logger.debug(f"Getting element with xpath_identifier: {xpath_identifier}")
            res = BeautifulSoup(self.cf.driver.page_source, "html.parser")
            # self.last_page_soup = res

            element = res.find(xpath_identifier)

            # self.note_uri()
            logger.debug(element.prettify())
            output = GetElementOutput(
                success=True,
                message=f"Got element with xpath_identifier: {xpath_identifier}.",
                element=element.prettify(),
            )
            self.context.tool_history.append((self.name, input, output))
            self.context.add_observed_uri(extract_uri(self.cf.driver.current_url))
            return output
        except Exception as e:
            logger.debug("Error: Failed to get the element.")
            output = GetElementOutput(
                success=False, message="Failed to get the element.", error=str(e), element=None
            )
            self.context.tool_history.append((self.name, input, output))
            return output
