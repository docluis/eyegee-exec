import time
from typing import Literal

from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select

from langchain_core.messages import HumanMessage, AIMessage
from langgraph.graph import END, StateGraph, MessagesState
from langchain_core.tools import tool
from langgraph.prebuilt import ToolNode
from langgraph.checkpoint import MemorySaver

from src.utils import parse_page_requests
from src.log import logger
from src.templates import interactionagent_inital_prompt_template


class InteractionAgent:
    def __init__(self, cf):
        self.cf = cf
        self.tools = self.initialize_tools()
        self.app = self.initialize_app()

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
        def fill_text_field_tool(xpath_identifier: str, value: str):
            """
            Fill the text field with the given name with the given value.
            """
            logger.info(f"Filling text field with value: {value}")
            element = self.cf.driver.find_element(By.XPATH, xpath_identifier)
            element.send_keys(value)
            return ["Filled text field with value: " + value]

        @tool("select_option")
        def select_option_tool(xpath_identifier: str, visible_value: str):
            """
            Select the option from a select menu.
            """
            logger.info(f"Selecting option with value: {visible_value}")
            element = self.cf.driver.find_element(By.XPATH, xpath_identifier)
            select = Select(element)
            select.select_by_visible_text(visible_value)
            return ["Selected option with visible_value: " + visible_value]

        @tool("click_button")
        def click_button_tool(xpath_identifier: str):
            """
            Click the button with the given name.
            """
            logger.info(f"Clicking button with name: {xpath_identifier}")
            element = self.cf.driver.find_element(By.XPATH, xpath_identifier)
            element.click()
            time.sleep(self.cf.selenium_rate)
            return ["Clicked button with name: " + xpath_identifier]

        @tool("get_page_soup")
        def get_page_soup_tool():
            """
            Get the page source.
            """
            logger.info("Getting page source")
            return [BeautifulSoup(self.cf.driver.page_source, "html.parser")]

        @tool("get_outgoing_requests")
        def get_outgoing_requests():
            """
            Get the performance logs and parse the outgoing requests, to read the APIs called.
            """
            logger.info("Getting outgoing requests")
            performance_logs = self.cf.driver.get_log("performance")
            page_requests = parse_page_requests("", performance_logs)
            return [page_requests]

        tools = [
            navigate_tool,
            fill_text_field_tool,
            select_option_tool,
            click_button_tool,
            get_page_soup_tool,
            get_outgoing_requests,
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
            response = self.cf.model.invoke(messages)
            return {"messages": [response]}

        def confirm_action(state: MessagesState):
            messages = state["messages"]
            last_message = messages[-1]

            if isinstance(last_message, AIMessage) and "Confirmation needed" not in last_message.content:
                return {"messages": [HumanMessage("Confirmation needed: " + last_message.content)]}

            user_response = messages[-1].content.lower()
            if "yes" in user_response or "confirm" in user_response:
                return {"messages": [HumanMessage("Confirmed")]}

            return {"messages": [HumanMessage("Action not confirmed, stopping.")]}

        tool_node = ToolNode(self.tools)
        self.cf.model = self.cf.model.bind_tools(self.tools)
        workflow = StateGraph(MessagesState)

        workflow.add_node("agent", call_model)
        workflow.add_node("confirm", confirm_action)
        workflow.add_node("tools", tool_node)

        workflow.set_entry_point("agent")

        workflow.add_conditional_edges(
            "agent",
            lambda state: "confirm" if not state["messages"][-1].tool_calls else "tools",
        )
        workflow.add_edge("confirm", "agent")
        workflow.add_edge("tools", "agent")

        checkpointer = MemorySaver()

        app = workflow.compile(checkpointer=checkpointer)
        return app

    def interact(self, path, interaction):
        prompt = interactionagent_inital_prompt_template.format(
            url=f"{self.cf.target}{path}", interaction=interaction
        )
        final_state = self.app.invoke(
            {"messages": [HumanMessage(prompt)]},
            config={"configurable": {"thread_id": 42}},
        )
        return final_state["messages"][-1].content
