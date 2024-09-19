from src.log import logger
from langchain_core.messages import HumanMessage, SystemMessage
from typing import Any, Dict, List, Tuple

from src.discovery.llm.messages import api_system_message, interaction_ranking_system_message
import json

from src.discovery.llm.model_classes import ApiModel, ApiModelList, RankedInteractions

def llm_parse_requests_for_apis(cf, page_requests) -> List[ApiModel]:
    """
    Parse the APIs called from the given page_requests, using LLM.
    """

    chain = cf.model.with_structured_output(ApiModelList)
    logger.debug("Parsing APIs")
    messages = [
        SystemMessage(api_system_message),
        HumanMessage(page_requests),
    ]
    apis = chain.invoke(messages)
    # convert to dict

    # try:
    #     apis_json = json.loads(apis)
    # except json.JSONDecodeError:
    #     logger.error(f"Failed to parse apis JSON: {apis}")
    #     apis_json = []

    return apis.apis

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
    return ranked_interactions_tuple_list
