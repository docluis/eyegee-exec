from typing import List
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage

from src.discovery.llm.model_classes import ApiModel, ApiModelList
from src.discovery.llm.messages import api_system_message
from src.log import logger


class LLM_ApiParser:
    def __init__(self, cf):
        self.chain = cf.model.with_structured_output(ApiModelList)
        self.messages = [SystemMessage(api_system_message)]

    def parse_apis(self, page_requests: str) -> List[ApiModel]:
        """
        Parse APIs of the given performance logs, using LLM.
        """
        logger.debug("Parsing page requests")
        self.messages.append(HumanMessage(page_requests))
        apis = self.chain.invoke(self.messages) # returns a object of type ApiModelList
        #  append the output to the messages
        self.messages.append(AIMessage(str(apis)))

        return apis.apis
