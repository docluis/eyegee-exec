from langchain_core.messages import HumanMessage, SystemMessage

from src.discovery.llm.messages import summary_system_message
from src.log import logger

class LLM_Summarizer:
    def __init__(self, cf):
        self.chain = cf.model | cf.parser
        self.messages = [SystemMessage(summary_system_message)]

    def create_summary(self, soup):
        """
        Create a summary of the given soup, using LLM.
        """
        logger.debug("Creating summary")
        self.messages.append(HumanMessage(soup.prettify()))
        summary = self.chain.invoke(self.messages)
        self.messages.append(summary)
        
        return summary