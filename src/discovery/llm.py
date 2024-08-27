from src.log import logger
from langchain_core.messages import HumanMessage, SystemMessage
from typing import Any, Dict, List

from src.discovery.interaction import Interaction
from src.discovery.messages import api_system_message, interaction_ranking_system_message
import json


def llm_parse_requests_for_apis(cf, page_requests) -> List[Dict]:
    """
    Parse the APIs called from the given page_requests, using LLM.
    """

    chain = cf.model | cf.parser
    logger.info("Parsing APIs")
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



def llm_rank_interactions(cf, interactions_names: List[str]) -> List[Dict[str, Any]]:
    """
    Rank the given interactions using the LLM model to determine the most important interactions.
    """
    chain = cf.model | cf.parser
    logger.info("Ranking interactions")
    messages = [
        SystemMessage(interaction_ranking_system_message),
        HumanMessage(json.dumps(interactions_names)),
    ]
    ranked_interactions = chain.invoke(messages)

    try:
        ranked_interactions_json = json.loads(ranked_interactions)
    except json.JSONDecodeError:
        logger.error(f"Failed to parse ranked interactions JSON: {ranked_interactions}")
        ranked_interactions_json = []

    return ranked_interactions_json