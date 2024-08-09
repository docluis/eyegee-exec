import time
import json
from typing import Literal

from bs4 import BeautifulSoup
from difflib import unified_diff

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
        self.last_page_soup = None

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

            actual_url = self.cf.driver.current_url

            res = f"Attempted to navigate to: {url}. Actual URL now: {actual_url}"

            logger.debug(res)
            return [res]

        @tool("fill_text_field")
        def fill_text_field_tool(xpath_indenfifier: str, value: str):
            """
            Fill the text field with the given name with the given value.
            """
            logger.info(f"Filling text field with value: {value}")
            # TODO: keep in mind that this is a very simple implementation, XPath is not always the best way to identify,
            #  it may return muliple elements, or the element may not be found at all, so check edgecases, and improve this
            element = self.cf.driver.find_element(By.XPATH, xpath_indenfifier)
            element.clear()  # clear the field first
            element.send_keys(value)

            # now examine how the entered data looks like
            actual_value = element.get_attribute("value")

            if actual_value == value:
                res = f"Attempted to fill text field: {xpath_indenfifier} with value: {value}."
            else:
                soup = BeautifulSoup(
                    self.cf.driver.page_source, "html.parser"
                ).prettify()
                res = f"Error: Attempted to fill text field: {xpath_indenfifier} with value: {value}. Actual value now: {actual_value} does not match the expected value. Adjust the value to match the required format and retry. Page source: \n{soup}"

            logger.debug(res)
            return [res]

        @tool("fill_text_field_date")
        def fill_text_field_date_tool(
            xpath_indenfifier: str, year_value: str, month_value: str, day_value: str
        ):
            """
            Fill the date field with the given name with the given value.
            """
            logger.info(
                f"Filling date field with value: {year_value}-{month_value}-{day_value}"
            )

            entry = f"{month_value}-{day_value}-{year_value}"
            element = self.cf.driver.find_element(By.XPATH, xpath_indenfifier)
            element.clear()  # clear the field first
            element.send_keys(entry)

            # now examine how the entered data looks like
            actual_value = element.get_attribute("value")

            actual_year, actual_month, actual_day = actual_value.split("-")

            if actual_value == entry or (
                actual_year == year_value
                and actual_month == month_value
                and actual_day == day_value
            ):
                res = f"Filled date field: {xpath_indenfifier} with value: {entry}."
            else:
                soup = BeautifulSoup(
                    self.cf.driver.page_source, "html.parser"
                ).prettify()
                res = f"Error: Attempted to fill date field: {xpath_indenfifier} with value: {entry}. Actual value now: {actual_value} does not match the expected value. Adjust the value to match the required format and retry. Page source: \n{soup}"

            logger.debug(res)
            return [res]

        @tool("select_option")
        def select_option_tool(xpath_indenfifier: str, visible_value: str):
            """
            Select the option from a select menu.
            """
            logger.info(f"Selecting option with value: {visible_value}")
            element = self.cf.driver.find_element(By.XPATH, xpath_indenfifier)
            select = Select(element)
            select.select_by_visible_text(visible_value)

            actual_value = select.first_selected_option.text

            res = f"Attempted to select option: {xpath_indenfifier} with value: {visible_value}. Actual value now: {actual_value}"
            logger.debug(res)
            return [res]

        @tool("click_button")
        def click_button_tool(xpath_indenfifier: str):
            """
            Click the button with the given name.
            """
            logger.info(f"Clicking button with name: {xpath_indenfifier}")

            time.sleep(self.cf.selenium_rate)
            soup_before = BeautifulSoup(self.cf.driver.page_source, "html.parser")
            element = self.cf.driver.find_element(By.XPATH, xpath_indenfifier)
            element.click()
            time.sleep(self.cf.selenium_rate)
            soup_after = BeautifulSoup(self.cf.driver.page_source, "html.parser")

            if soup_before == soup_after:
                res = f"Clicked button with name: {xpath_indenfifier}, but soup before and after are the same. Check outgoing requests to see if something happened."
            else:
                diff = unified_diff(
                    soup_before.prettify().splitlines(),
                    soup_after.prettify().splitlines(),
                    lineterm="",
                )
                diff_print = "\n".join(list(diff))
                res = f"Clicked button with name: {xpath_indenfifier}. Page changed. Diff: \n{diff_print}"

            logger.debug(res)
            return [res]

        @tool("get_page_soup")
        def get_page_soup_tool():
            """
            Get the page source.
            """
            logger.info("Getting page source")

            res = BeautifulSoup(self.cf.driver.page_source, "html.parser").prettify()
            self.last_page_soup = res

            logger.debug(res)
            return [res]

        @tool("get_page_soup_diff")
        def get_page_soup_diff_tool():
            """
            Get the only the diff since last get_page_soup or get_page_soup_diff tool call.

            May improve efficiency, by providing fewer token.
            """
            logger.info("Getting page source diff")

            if self.last_page_soup is None:
                return ["No previous page soup found. Use get_page_soup first."]
            else:
                res = BeautifulSoup(
                    self.cf.driver.page_source, "html.parser"
                ).prettify()
                diff = unified_diff(
                    self.last_page_soup.splitlines(),
                    res.splitlines(),
                    lineterm="",
                )
                self.last_page_soup = res
                diff_print = "\n".join(list(diff))
                logger.debug(diff_print)
                return [diff_print]

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

            res = json.dumps(p_reqs, indent=4)

            logger.debug(res)
            return [res]

        tools = [
            navigate_tool,
            fill_text_field_tool,
            fill_text_field_date_tool,
            select_option_tool,
            click_button_tool,
            get_page_soup_tool,
            get_page_soup_diff_tool,
            get_outgoing_requests_tool,
        ]
        return tools

    def initialize_app(self):
        def should_continue(state: MessagesState) -> Literal["tools", END]:  # type: ignore
            logger.debug("Checking if should continue")
            messages = state["messages"]
            last_message = messages[-1]

            if last_message.tool_calls:  # continue if the last message was a tool call
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
        self.p_reqs = []  # reset the page request list
        self.last_page_soup = None  # reset the last page soup
        prompt = interactionagent_inital_prompt_template.format(
            url=f"{self.cf.target}{path}", interaction=interaction
        )
        final_state = self.app.invoke(
            {"messages": [HumanMessage(prompt)]},
            config={"configurable": {"thread_id": 42}},
        )
        last_message = final_state["messages"][-1].content

        return last_message, self.p_reqs
