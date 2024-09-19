from src.log import logger
from langchain_core.messages import HumanMessage, SystemMessage
from typing import List, Tuple

from src.discovery.llm.messages import interaction_ranking_system_message
import json

from src.discovery.llm.model_classes import RankedInteractions

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
