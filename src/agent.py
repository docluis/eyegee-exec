import time
import config as cf

from langchain_core.tools import tool


# Define tools for interaction with the website using Selenium
@tool
def interact_with_element(path: str, interaction_info: dict, input_values: dict):
    """
    Interact with an element on the website.
    """
    cf.logger.info(f"Agent interacting with element: {interaction_info['name']}")
    cf.driver.get(f"{cf.target}{path}")
    time.sleep(cf.selenium_rate)
    
    
    element = cf.driver.find_element_by_xpath(interaction_info["xpath"])
    if interaction_info["type"] == "click":
        element.click()
    elif interaction_info["type"] == "input":
        element.send_keys(input_values["value"])
    time.sleep(cf.selenium_rate)