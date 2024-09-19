from src.log import logger
from langchain_core.messages import HumanMessage, SystemMessage
from typing import Any, Dict, List, Tuple

from src.discovery.interaction import Interaction
from src.discovery.messages import api_system_message, interaction_ranking_system_message
import json

from langchain_core.pydantic_v1 import BaseModel, Field


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


class RankedInteraction(BaseModel):
    """Model for ranked interaction"""

    interaction: str = Field(description="The name of the interaction")
    approaches: int = Field(description="The number of approaches to be genereated for the interaction")


class RankedInteractions(BaseModel):
    """Model for ranked interactions"""

    interactions_list: List[RankedInteraction] = Field(description="The list of interactions to be ranked")


def llm_rank_interactions(cf, interactions_names: List[str]) -> List[Tuple[str, int]]:
    """
    Rank the given interactions using the LLM model to determine the most important interactions.
    """
    chain = cf.model.with_structured_output(RankedInteractions)
    logger.debug("Ranking interactions")
    messages = [
        SystemMessage(interaction_ranking_system_message),
        HumanMessage(json.dumps(interactions_names)),
    ]
    ranked_interactions = chain.invoke(messages)
    ranked_interactions_tuple_list = [
        (interaction.interaction, interaction.approaches) for interaction in ranked_interactions.interactions_list
    ]

    # try:
    #     ranked_interactions_json = json.loads(ranked_interactions)
    # except json.JSONDecodeError:
    #     logger.error(f"Failed to parse ranked interactions JSON: {ranked_interactions}")
    #     ranked_interactions_json = []

    # return ranked_interactions_json
    return ranked_interactions_tuple_list
