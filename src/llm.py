from langchain_core.messages import HumanMessage, SystemMessage

import config as cf
import src.messages as msg


def llm_create_summary(soup):
    """
    Create a summary of the given soup, using LLM.
    """
    chain = cf.model | cf.parser
    cf.logger.debug("Creating summary")
    messages = [
        SystemMessage(msg.summary_system_message),
        HumanMessage(soup.get_text()),
    ]
    summary = chain.invoke(messages)
    return summary


def llm_parse_interactions(soup):
    """
    Parse the interactions of the given soup, using LLM.
    """
    chain = cf.model | cf.parser
    cf.logger.debug("Parsing interactions")
    messages = [
        SystemMessage(msg.interaction_system_message),
        HumanMessage(soup.get_text()),
    ]
    interactions = chain.invoke(messages)
    return interactions

def llm_parse_apis(logs):
    """
    Parse the APIs called from the given logs, using LLM.
    """
    # chain = cf.model | cf.parser
    # cf.logger.debug("Parsing APIs")
    # messages = [
    #     SystemMessage(msg.api_system_message),
    #     HumanMessage(logs),
    # ]
    # apis = chain.invoke(messages)
    # return apis
    print(logs)
    return []