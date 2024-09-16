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
from src.discovery.utils import parse_page_requests
from src.discovery.interaction_agent.tool_context import ToolContext
from src.log import logger
from src.discovery.interaction_agent.tool_input_output_classes import GetOutgoingRequestsInput, GetOutgoingRequestsOutput


class GetOutgoingRequests(BaseTool):
    cf: Config
    context: ToolContext

    name = "get_outgoing_requests"
    description = (
        "Function: Get the outgoing requests."
        "Args:"
        "  - filtered: bool Whether the outgoing requests should be filtered. (optional, default: True)"
        "Returns:"
        "  - success: bool Whether the outgoing requests were retrieved successfully."
        "  - message: str The message indicating the result of the operation."
        "  - outgoing_requests: str The outgoing requests."
        "  - error: str The error message if the operation failed."
    )
    args_schema: Type[BaseModel] = GetOutgoingRequestsInput

    def _run(self, filtered: bool = True) -> GetOutgoingRequestsOutput:
        """Use the tool."""
        input = GetOutgoingRequestsInput(filtered=filtered)
        try:
            logger.info(f"Getting outgoing requests with filtered: {filtered}")
            p_reqs = parse_page_requests(
                driver=self.cf.driver,
                target=self.cf.target,
                uri=self.context.initial_uri,
                filtered=filtered,
            )
            p_reqs_str = json.dumps(p_reqs, indent=4)
            output = GetOutgoingRequestsOutput(
                success=True, message=f"Got outgoing requests with filtered: {filtered}.", outgoing_requests=p_reqs_str
            )
            self.context.tool_history.append((self.name, input, output))
            return output
        except Exception as e:
            logging.error("Error: Failed to get outgoing requests.")
            output = GetOutgoingRequestsOutput(
                success=False, message="Failed to get outgoing requests.", error=str(e)
            )
            self.context.tool_history.append((self.name, input, output))
            return output
