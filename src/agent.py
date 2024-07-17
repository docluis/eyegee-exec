import time
from typing import Literal
import config as cf

from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By

from langchain_core.messages import HumanMessage
from langgraph.graph import END, StateGraph, MessagesState
from langchain_core.tools import tool
from langgraph.prebuilt import ToolNode
from langgraph.checkpoint import MemorySaver

from src.utils import parse_page_requests


# Define tools for interaction with the website using Selenium
@tool("navigate")
def navigate_tool(url: str):
    """
    Navigate to the given URL using Selenium.
    """
    cf.logger.info(f"Navigating to {url}")
    cf.driver.get(url)
    time.sleep(cf.selenium_rate)
    return ["Navigated to " + url]


@tool("fill_text_field")
def fill_text_field_tool(xpath_indenfifier: str, value: str):
    """
    Fill the text field with the given name with the given value.
    """
    cf.logger.info(f"Filling text field with value: {value}")
    # TODO: keep in mind that this is a very simple implementation, XPath is not always the best way to identify,
    #  it may return muliple elements, or the element may not be found at all, so check edgecases, and improve this
    element = cf.driver.find_element(By.XPATH, xpath_indenfifier)
    element.send_keys(value)
    return ["Filled text field with value: " + value]


@tool("click_button")
def click_button_tool(xpath_indenfifier: str):
    """
    Click the button with the given name.
    """
    cf.logger.info(f"Clicking button with name: {xpath_indenfifier}")
    element = cf.driver.find_element(By.XPATH, xpath_indenfifier)
    element.click()
    time.sleep(cf.selenium_rate)
    return ["Clicked button with name: " + xpath_indenfifier]


@tool("get_page_soup")
def get_page_soup_tool():
    """
    Get the page source.
    """
    cf.logger.info("Getting page source")
    return [BeautifulSoup(cf.driver.page_source, "html.parser")]


@tool("get_outgoing_requests")
def get_outgoing_requests():
    """
    Get the performance logs and parse the outgoing requests, to read the APIs called.
    """
    # TODO: use LLM again to parse out the APIs
    cf.logger.info("Getting outgoing requests")
    performance_logs = cf.driver.get_log("performance")
    page_requests = parse_page_requests("", performance_logs)
    return [page_requests]


tools = [navigate_tool, fill_text_field_tool, click_button_tool, get_page_soup_tool, get_outgoing_requests]

tool_node = ToolNode(tools)

cf.model = cf.model.bind_tools(tools)


def should_continue(state: MessagesState) -> Literal["tools", END]: # type: ignore
    print("Checking if should continue")
    messages = state["messages"]
    last_message = messages[-1]

    if last_message.tool_calls:
        return "tools"
    return END


def call_model(state: MessagesState):
    messages = state["messages"]
    response = cf.model.invoke(messages)
    return {"messages": [response]}


workflow = StateGraph(MessagesState)

workflow.add_node("agent", call_model)
workflow.add_node("tools", tool_node)

workflow.set_entry_point("agent")

workflow.add_conditional_edges(
    "agent",
    should_continue,
)

workflow.add_edge("tools", "agent")

checkpointer = MemorySaver()

app = workflow.compile(checkpointer=checkpointer)


def test():
    final_state = app.invoke(
        {
            "messages": [
                HumanMessage(
                    "Interact with the site: http://localhost:3000/contact and fill out the form. Start by navigating to the site. Then fill out the form with random data. Summarize the observed behavior and how the form works and how the server responds to the interaction from client perspective. Also observe the outgoing requets. Do not make any assumptions."
                )
            ]
        },
        config={"configurable": {"thread_id": 42}},
    )
    print(final_state["messages"][-1].content)
