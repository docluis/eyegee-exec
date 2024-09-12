import time
import json

from urllib.parse import urlparse
from typing import List, Literal, Optional, Tuple
from bs4 import BeautifulSoup
from difflib import unified_diff

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys

from langchain_core.messages import HumanMessage
from langgraph.graph import END, StateGraph, MessagesState
from langchain_core.tools import tool
from langgraph.prebuilt import ToolNode
from langgraph.checkpoint.memory import MemorySaver

from src.discovery.utils import filter_html, parse_page_requests
from src.log import logger
from src.discovery.templates import interactionagent_inital_prompt_template


class InteractionAgent:
    def __init__(self, cf):
        self.cf = cf
        self.tools = self.initialize_tools()
        self.app = self.initialize_app()
        self.p_reqs: List[dict] = []
        self.uris: List[str] = []
        self.last_page_soup: Optional[BeautifulSoup] = None
        self.initial_uri: Optional[str] = None
        self.click_in_progress: bool = False

    def note_uri(self) -> str:
        """
        Note the current URI and return it.
        """
        parsed = urlparse(self.cf.driver.current_url)
        path_now = parsed.path
        query_string = parsed.query
        if query_string:
            path_now = f"{path_now}?{query_string}"
        if path_now not in self.uris:
            self.uris.append(path_now)
        return path_now

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

            uri_now = self.note_uri()
            res = f"Attempted to navigate to: {url}. Actual URI now: {uri_now}"
            logger.debug(res)
            return [res]

        @tool("fill_text_field")
        def fill_text_field_tool(xpath_identifier: str, value: str):
            """
            Fill the text field with the given name with the given value.
            """
            logger.info(f"Filling text field with value: {value}")
            # TODO: keep in mind that this is a very simple implementation, XPath is not always the best way to identify,
            #  it may return muliple elements, or the element may not be found at all, so check edgecases, and improve this
            element = self.cf.driver.find_element(By.XPATH, xpath_identifier)

            # clear the field first
            element.clear()
            element.send_keys(Keys.CONTROL + "a")  # select all
            element.send_keys(Keys.DELETE)  # delete
            element.send_keys(50 * Keys.BACKSPACE)

            element.send_keys(value)

            # now examine how the entered data looks like
            actual_value = element.get_attribute("value")

            if actual_value == value:
                res = f"Attempted to fill text field: {xpath_identifier} with value: {value}."
            else:
                soup = BeautifulSoup(self.cf.driver.page_source, "html.parser").prettify()
                res = f"Error: Attempted to fill text field: {xpath_identifier} with value: {value}. Actual value now: {actual_value} does not match the expected value. Adjust the value to match the required format and retry. Page source: \n{soup}"

            self.note_uri()
            logger.debug(res)
            return [res]

        @tool("fill_text_field_date")
        def fill_text_field_date_tool(xpath_identifier: str, year_value: str, month_value: str, day_value: str):
            """
            Fill the date field with the given name with the given value.
            """
            logger.info(f"Filling date field with value: {year_value}-{month_value}-{day_value}")

            entry = f"{month_value}-{day_value}-{year_value}"
            element = self.cf.driver.find_element(By.XPATH, xpath_identifier)
            element.clear()  # clear the field first
            element.send_keys(entry)

            # now examine how the entered data looks like
            actual_value = element.get_attribute("value")

            actual_year, actual_month, actual_day = actual_value.split("-")

            if actual_value == entry or (
                actual_year == year_value and actual_month == month_value and actual_day == day_value
            ):
                res = f"Filled date field: {xpath_identifier} with value: {entry}."
            else:
                soup = BeautifulSoup(self.cf.driver.page_source, "html.parser").prettify()
                res = f"Error: Attempted to fill date field: {xpath_identifier} with value: {entry}. Actual value now: {actual_value} does not match the expected value. Adjust the value to match the required format and retry. Page source: \n{soup}"

            self.note_uri()
            logger.debug(res)
            return [res]

        @tool("select_option")
        def select_option_tool(xpath_identifier: str, visible_value: str):
            """
            Select the option from a select menu.
            """
            logger.info(f"Selecting option with value: {visible_value}")
            element = self.cf.driver.find_element(By.XPATH, xpath_identifier)
            select = Select(element)
            select.select_by_visible_text(visible_value)

            actual_value = select.first_selected_option.text

            self.note_uri()
            res = f"Attempted to select option: {xpath_identifier} with value: {visible_value}. Actual value now: {actual_value}"
            logger.debug(res)
            return [res]

        @tool("click")
        def click_tool(xpath_identifier: str, using_javascript: bool = False):
            """
            Click the element with the given identifier using selenium.

            Set using_javascript to True to force the click using JavaScript.
            If the element is not found, an error will be returned.
            Click only one element at a time, to avoid issues with multiple elements being clicked at the same time.
            """
            if self.click_in_progress:
                logger.info(f"Clicking element with name: {xpath_identifier} blocked")
                res = "Error: Click in progress, please wait for the previous click to finish."
                logger.debug(res)
                return [res]

            self.click_in_progress = True
            try:
                logger.info(f"Clicking element with name: {xpath_identifier}, using JavaScript: {using_javascript}")

                time.sleep(self.cf.selenium_rate)
                soup_before = BeautifulSoup(self.cf.driver.page_source, "html.parser")
                try:
                    element = self.cf.driver.find_element(By.XPATH, xpath_identifier)
                    if using_javascript:
                        self.cf.driver.execute_script("arguments[0].click();", element)
                    else:
                        element.click()
                except Exception as e:
                    res = f"""
                    Error: Attempted to click element with name: {xpath_identifier}.
                    Exception Message:
                    {e}

                    Retry with a different identifier or by clicking (outer) elements,
                    alternatively, use the JavaScript click option to force the click.
                    """
                    logger.debug(res)
                    logger.info(f"Pressing {xpath_identifier} failed...")
                    return [res]
                time.sleep(self.cf.selenium_rate)
                soup_after = BeautifulSoup(self.cf.driver.page_source, "html.parser")

                if soup_before == soup_after:
                    res = f"""
                    Clicked element with name: {xpath_identifier}, but soup before and after are the same.
                    Check outgoing requests to see if something happened.
                    """
                else:
                    diff = unified_diff(
                        soup_before.prettify().splitlines(),
                        soup_after.prettify().splitlines(),
                        lineterm="",
                    )
                    diff_print = "\n".join(list(diff))
                    res = f"""
                    Clicked element with name: {xpath_identifier}.
                    Page changed. Diff:
                    {diff_print}
                    """
            finally:
                self.click_in_progress = False

            self.note_uri()
            logger.debug(res)
            return [res]

        @tool("get_page_soup")
        def get_page_soup_tool(filtered: bool = True):
            """
            Get the page source.

            If filtered is True, the page source will be filtered to remove unnecessary tags and attributes.
            Better for LLM, reduces the number of tokens, however, may remove some important information.
            Use filtered=False to get the raw page source. Only use if necessary.
            Returns the page source as a string.
            """
            logger.info(f"Getting page source with filtered: {'True' if filtered else 'False'}")

            res = BeautifulSoup(self.cf.driver.page_source, "html.parser")
            self.last_page_soup = res

            if filtered:
                res = filter_html(res)

            self.note_uri()
            logger.debug(res.prettify())
            return [res.prettify()]

        @tool("get_page_soup_diff")
        def get_page_soup_diff_tool(filtered: bool = True):
            """
            Get the only the diff since last get_page_soup or get_page_soup_diff tool call.

            May improve efficiency, by providing fewer token.

            If filtered is True, the page source will be filtered to remove unnecessary tags and attributes.
            Better for LLM, reduces the number of tokens, however, may remove some important information.
            Use filtered=False to get the raw page source. Only use if necessary.
            Returns the page source diff as a string.
            """
            logger.info(f"Getting page source diff with filtered: {'True' if filtered else 'False'}")
            before = self.last_page_soup
            now = BeautifulSoup(self.cf.driver.page_source, "html.parser")

            if filtered:
                before = filter_html(before)
                now = filter_html(now)

            self.note_uri()
            if before is None:
                return ["No previous page soup found. Use get_page_soup first."]
            else:
                diff = unified_diff(
                    before.prettify().splitlines(),
                    now.prettify().splitlines(),
                    lineterm="",
                )
                self.last_page_soup = now
                diff_print = "\n".join(list(diff))
                logger.debug(diff_print)
                return [diff_print]

        @tool("get_outgoing_requests")
        def get_outgoing_requests_tool(filtered: bool = True):
            """
            Get the performance logs and parse the outgoing requests, to read the APIs called.
            Will only return requests since the last navigation.

            Use filtered=False to get all outgoing requests. Only use if necessary.
            """
            logger.info(f"Getting outgoing requests with filtered: {filtered}")
            p_reqs = parse_page_requests(
                driver=self.cf.driver,
                target=self.cf.target,
                uri=self.initial_uri,
                filtered=filtered,
            )
            self.p_reqs.extend(p_reqs)

            res = json.dumps(p_reqs, indent=4)

            self.note_uri()
            logger.debug(res)
            return [res]

        tools = [
            navigate_tool,
            fill_text_field_tool,
            fill_text_field_date_tool,
            select_option_tool,
            click_tool,
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

    def interact(self, uri: str, interaction: str) -> Tuple[str, List[dict], List[str], Optional[str]]:
        """
        Interact with the website using the given interaction.

        Args:
            uri (str): The URI to interact with.
            interaction (str): The interaction to perform with the website.

        Returns:
            Tuple:
                A tuple containing the following elements:
                - str: The last message from the interaction (usually a summary or output).
                - List[dict]: The list of page requests made during the interaction.
                - List[str]: A list of URIs observed during the interaction.
                - Optional[str]: The new page soup after the interaction, if the page changed (None if unchanged).
        """

        self.p_reqs = []  # reset the page request list
        self.uris = []
        self.last_page_soup = None  # reset the last page soup
        self.initial_uri = uri
        initial_soup = BeautifulSoup(self.cf.driver.page_source, "html.parser")
        prompt = interactionagent_inital_prompt_template.format(url=f"{self.cf.target}{uri}", interaction=interaction)
        final_state = self.app.invoke(
            {"messages": [HumanMessage(prompt)]},
            config={"configurable": {"thread_id": 42}, "recursion_limit": 50},
        )
        last_message = final_state["messages"][-1].content

        new_soup = None
        soup_now = BeautifulSoup(self.cf.driver.page_source, "html.parser")
        if soup_now.prettify() != initial_soup.prettify():
            logger.debug("Page changed after interaction")
            new_soup = filter_html(soup_now)

        return last_message, self.p_reqs, self.uris, new_soup
