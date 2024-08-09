from langchain_core.messages import HumanMessage, SystemMessage

from src.discovery.messages import interaction_system_message
from src.log import logger

import json

class LLM_InteractionParser:
    def __init__(self, cf):
        self.chain = cf.model | cf.parser
        self.messages = [SystemMessage(interaction_system_message)]

    def parse_interactions(self, soup):
        """
        Parse interactions of the given soup, using LLM.
        """
        logger.info("Parsing interactions")
        self.messages.append(HumanMessage(soup.prettify()))
        interactions = self.chain.invoke(self.messages)
        self.messages.append(interactions)

        try:
            interactions_json = json.loads(interactions)
        except json.JSONDecodeError:
            logger.error(f"Failed to parse interactions JSON: {interactions}")
            interactions_json = []
        
        return interactions_json