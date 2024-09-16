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
from src.discovery.utils import filter_html
from src.discovery.interaction_agent.tool_context import ToolContext
from src.log import logger
from src.discovery.interaction_agent.tool_input_output_classes import GetPageSoupInput, GetPageSoupOutput


class GetPageSoup(BaseTool):
    cf: Config
    context: ToolContext

    name = "get_page_soup"
    description = (
        "Function: Get the page source.\n"
        "Args:\n"
        "  - filtered: bool Whether the page source should be filtered. (optional, default: True)\n"
        "Returns:\n"
        "  - success: bool Whether the page source was retrieved successfully.\n"
        "  - message: str The message indicating the result of the operation.\n"
        "  - page_source: str The page source.\n"
        "  - error: str The error message if the operation failed.\n"
    )
    args_schema: Type[BaseModel] = GetPageSoupInput

    def _run(self, filtered: bool = True) -> GetPageSoupOutput:
        """Use the tool."""
        input = GetPageSoupInput(filtered=filtered)
        try:
            logger.info(f"Getting page source with filtered: {'True' if filtered else 'False'}")
            res = BeautifulSoup(self.cf.driver.page_source, "html.parser")
            # self.last_page_soup = res

            if filtered:
                res = filter_html(res)

            # self.note_uri()
            logger.debug(res.prettify())
            output = GetPageSoupOutput(
                success=True,
                message=f"Got page source with filtered: {'True' if filtered else 'False'}.",
                page_source=res.prettify(),
            )
            self.context.tool_history.append((self.name, input, output))
            return output
        except Exception as e:
            logging.error("Error: Failed to fill in the text field.")
            output = GetPageSoupOutput(success=False, message="Failed to fill in the text field.", error=str(e), page_source=None)
            self.context.tool_history.append((self.name, input, output))
            return output
