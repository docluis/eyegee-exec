from src.log import logger
from langchain_core.messages import HumanMessage, SystemMessage

import src.messages as msg
import json


def llm_create_summary(cf, soup):
    """
    Create a summary of the given soup, using LLM.
    """
    chain = cf.model | cf.parser
    logger.debug("Creating summary")
    messages = [
        SystemMessage(msg.summary_system_message),
        HumanMessage(soup.get_text()),
    ]
    summary = chain.invoke(messages)
    return summary


def llm_parse_interactions(cf, soup):
    """
    Parse the interactions of the given soup, using LLM.
    """
    chain = cf.model | cf.parser
    logger.debug("Parsing interactions")
    messages = [
        SystemMessage(msg.interaction_system_message),
        HumanMessage(soup.prettify()),
    ]
    interactions = chain.invoke(messages)

    try:
        interactions_json = json.loads(interactions)
    except json.JSONDecodeError:
        logger.error(f"Failed to parse interactions JSON: {interactions}")
        interactions_json = {}

    return interactions_json


def llm_parse_requests_for_apis(cf, page_requests):
    """
    Parse the APIs called from the given page_requests, using LLM.
    """

    chain = cf.model | cf.parser
    logger.debug("Parsing APIs")
    messages = [
        SystemMessage(msg.api_system_message),
        HumanMessage(page_requests),
    ]
    apis = chain.invoke(messages)
    logger.info(f"APIs: {apis}")

    try:
        apis_json = json.loads(apis)
    except json.JSONDecodeError:
        logger.error(f"Failed to parse apis JSON: {apis}")
        apis_json = {}

    return apis_json
