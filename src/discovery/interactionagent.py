import time
import json
from typing import Literal

from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select

from langchain_core.messages import HumanMessage
from langgraph.graph import END, StateGraph, MessagesState
from langchain_core.tools import tool
from langgraph.prebuilt import ToolNode
from langgraph.checkpoint import MemorySaver

from src.discovery.utils import get_performance_logs, parse_page_requests
from src.log import logger
from src.discovery.templates import interactionagent_inital_prompt_template


class InteractionAgent:
    def __init__(self, cf):
        self.cf = cf
        self.tools = self.initialize_tools()
        self.app = self.initialize_app()
        self.p_reqs = []

    def initialize_tools(self):
        # Define tools for interaction with the website using Selenium
        @tool("navigate")
        def navigate_tool(url: str):
            """
            Navigate to the given URL using Selenium.
            """
            logger.info(f"Navigating to {url}")
            self.cf.driver.get(url)
            time.sleep(self.cf.selenium_rate)
            return ["Navigated to " + url]

        @tool("fill_text_field")
        def fill_text_field_tool(xpath_indenfifier: str, value: str):
            """
            Fill the text field with the given name with the given value.
            """
            logger.info(f"Filling text field with value: {value}")
            # TODO: keep in mind that this is a very simple implementation, XPath is not always the best way to identify,
            #  it may return muliple elements, or the element may not be found at all, so check edgecases, and improve this
            element = self.cf.driver.find_element(By.XPATH, xpath_indenfifier)
            element.send_keys(value)
            return ["Filled text field with value: " + value]

        @tool("select_option")
        def select_option_tool(xpath_indenfifier: str, visible_value: str):
            """
            Select the option from a select menu.
            """
            logger.info(f"Selecting option with value: {visible_value}")
            element = self.cf.driver.find_element(By.XPATH, xpath_indenfifier)
            select = Select(element)
            select.select_by_visible_text(visible_value)
            return ["Selected option with visible_value: " + visible_value]

        @tool("click_button")
        def click_button_tool(xpath_indenfifier: str):
            """
            Click the button with the given name.
            """
            logger.info(f"Clicking button with name: {xpath_indenfifier}")
            element = self.cf.driver.find_element(By.XPATH, xpath_indenfifier)
            element.click()
            time.sleep(self.cf.selenium_rate)
            return ["Clicked button with name: " + xpath_indenfifier]

        @tool("get_page_soup")
        def get_page_soup_tool():
            """
            Get the page source.
            """
            logger.info("Getting page source")
            return [BeautifulSoup(self.cf.driver.page_source, "html.parser")]

        @tool("get_outgoing_requests")
        def get_outgoing_requests_tool():
            """
            Get the performance logs and parse the outgoing requests, to read the APIs called.
            Will only return requests since the last navigation.
            """
            logger.info("Getting outgoing requests")
            p_logs = get_performance_logs(self.cf.driver)
            p_reqs = parse_page_requests("", "", p_logs)
            self.p_reqs.extend(p_reqs)
            return [json.dumps(p_reqs, indent=4)]

        tools = [
            navigate_tool,
            fill_text_field_tool,
            select_option_tool,
            click_button_tool,
            get_page_soup_tool,
            get_outgoing_requests_tool,
        ]
        return tools

    def initialize_app(self):
        def should_continue(state: MessagesState) -> Literal["tools", END]:  # type: ignore
            logger.debug("Checking if should continue")
            messages = state["messages"]
            last_message = messages[-1]

            if last_message.tool_calls:
                return "tools"
            return END

        def call_model(state: MessagesState):
            messages = state["messages"]
            logger.debug(f"Calling model with messages: {messages}")
            response = self.cf.model.invoke(messages)
            return {"messages": [response]}

        tool_node = ToolNode(self.tools)
        self.cf.model = self.cf.model.bind_tools(self.tools)
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
        return app

    def interact(self, path, interaction):
        self.p_reqs = []
        prompt = interactionagent_inital_prompt_template.format(
            url=f"{self.cf.target}{path}", interaction=interaction
        )
        final_state = self.app.invoke(
            {"messages": [HumanMessage(prompt)]},
            config={"configurable": {"thread_id": 42}},
        )
        last_message = final_state["messages"][-1].content

        # also parse out all the apis called from every time get_outgoing_requests tool is called
        # all_p_reqs = []
        # for message in final_state["messages"]:
        #     if (
        #         hasattr(message, "type")
        #         and message.type == "tool"
        #         and message.name == "get_outgoing_requests"
        #     ):
        #         p_reqs = json.loads(json.loads(message.content)[0])
        #         all_p_reqs.extend(p_reqs)
        # all_p_reqs = json.dumps(all_p_reqs)

        return last_message, self.p_reqs
