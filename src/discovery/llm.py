from src.log import logger
from langchain_core.messages import HumanMessage, SystemMessage
from typing import Any, Dict, List

from src.discovery.messages import api_system_message, interaction_system_message
import json


def llm_parse_interactions(cf, soup) -> List[Dict]:
    """
    Parse the interactions of the given soup, using LLM.
    """
    chain = cf.model | cf.parser
    logger.debug("Parsing interactions")
    messages = [
        SystemMessage(interaction_system_message),
        HumanMessage(soup.prettify()),
    ]
    interactions = chain.invoke(messages)

    try:
        interactions_json = json.loads(interactions)
    except json.JSONDecodeError:
        logger.error(f"Failed to parse interactions JSON: {interactions}")
        interactions_json = []

    return interactions_json


def llm_parse_requests_for_apis(cf, page_requests) -> List[Dict]:
    """
    Parse the APIs called from the given page_requests, using LLM.
    """

    chain = cf.model | cf.parser
    logger.debug("Parsing APIs")
    messages = [
        SystemMessage(api_system_message),
        HumanMessage(page_requests),
    ]
    apis = chain.invoke(messages)

    try:
        apis_json = json.loads(apis)
    except json.JSONDecodeError:
        logger.error(f"Failed to parse apis JSON: {apis}")
        apis_json = []

    return apis_json
