from typing import List
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage

from src.discovery.llm.model_classes import InteractionModel, InteractionModelList
from src.discovery.llm.messages import interaction_system_message
from src.log import logger

import json

class LLM_InteractionParser:
    def __init__(self, cf):
        self.chain = cf.model.with_structured_output(InteractionModelList)
        self.messages = [SystemMessage(interaction_system_message)]

    def parse_interactions(self, soup) -> List[InteractionModel]:
        """
        Parse interactions of the given soup, using LLM.
        """
        logger.debug("Parsing interactions")
        self.messages.append(HumanMessage(soup.prettify()))
        interactions = self.chain.invoke(self.messages)
        self.messages.append(AIMessage(str(interactions)))
        
        return interactions.interactions