from difflib import unified_diff
import json
import operator


import time
from typing import Dict, Literal, TypedDict, List, Annotated, Tuple, Union
from bs4 import BeautifulSoup
from langgraph.graph import StateGraph, START, END
from rich.console import Console
from rich.live import Live

# from pydantic import BaseModel
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate
from langchain.agents import create_react_agent, AgentExecutor
from langchain.agents.output_parsers import JSONAgentOutputParser

from config import Config
from src.pretty_log import TestLog
from src.discovery.interaction_agent.tool_input_output_classes import AnyInput, AnyOutput
from src.discovery.llm import llm_parse_requests_for_apis
from src.discovery.interaction_agent.tool_context import ToolContext
from src.discovery.interaction_agent.tools.click import Click
from src.discovery.interaction_agent.tools.fill_text_field import FillTextField
from src.discovery.interaction_agent.tools.navigate import Navigate
from src.discovery.interaction_agent.tools.get_page_soup import GetPageSoup
from src.discovery.interaction_agent.tools.get_outgoing_requests import GetOutgoingRequests
from src.discovery.interaction_agent.tools.select_option import SelectOption
from src.log import logger
from src.discovery.utils import filter_html, format_steps, parse_page_requests
from src.discovery.interaction_agent.prompts import (
    high_high_level_planner_prompt,
    high_level_planner_prompt,
    react_agent_prompt,
    high_level_replanner_prompt,
    system_reporter_prompt,
    human_reporter_prompt,
)
from src.discovery.interaction_agent.agent_classes import (
    HighHighLevelPlan,
    # HighLevelPlan,
    PlanModel,
    Response,
    TestModel,
    CompletedTask,
    Act,
)

class PlanExecute(TypedDict):
    uri: str
    interaction: str
    page_soup: str
    limit: str
    approaches: List[str]
    plans: List[PlanModel]
    tests: Annotated[List[TestModel], operator.add]
    report: str


class InteractionAgent:
    def __init__(self, cf: Config) -> None:
        self.cf = cf
        # self.tools = self._init_tools()
        self.app = self._init_app()

    def _init_tools(self, context: ToolContext):
        return [
            Navigate(cf=self.cf, context=context),
            Click(cf=self.cf, context=context),
            FillTextField(cf=self.cf, context=context),
            GetPageSoup(cf=self.cf, context=context),
            # GetOutgoingRequests(cf=self.cf, context=context),
            SelectOption(cf=self.cf, context=context),
        ]

    def _init_app(self):
        def should_report(state: PlanExecute) -> Literal["executer", "reporter"]:
            if "plans" in state and state["plans"] == []:
                return "reporter"
            else:
                return "executer"

        high_high_level_planner = high_high_level_planner_prompt | self.cf.model.with_structured_output(
            HighHighLevelPlan
        )
        # TODO: add tool info to the prompt?
        high_level_planner = high_level_planner_prompt | self.cf.model.with_structured_output(PlanModel)
        high_level_replanner = high_level_replanner_prompt | self.cf.model.with_structured_output(Act)

        def high_level_plan_step(state: PlanExecute):
            plans = []
            for approach in state["approaches"]:
                plan = high_level_planner.invoke(
                    {
                        "uri": state["uri"],
                        "interaction": state["interaction"],
                        "page_soup": state["page_soup"],
                        "approach": approach,
                    }
                )
                plans.append(plan)

            return {"plans": plans}

        def execute_step(state: PlanExecute):
            tests = []
            uri = state["uri"]
            plans = state["plans"]
            test_log = TestLog(plans)
            with Live(refresh_per_second=10) as live:
                for i, plan in enumerate(state["plans"]):
                    context = ToolContext(cf=self.cf, initial_uri=uri)  # Create a new context for each test
                    tools = self._init_tools(context)
                    solver = create_react_agent(
                        self.cf.model, tools=tools, prompt=react_agent_prompt, output_parser=JSONAgentOutputParser()
                    )
                    solver_executor = AgentExecutor(agent=solver, tools=tools)
                    # logger.info("")
                    # logger.info(f"#### Next Approach: {plan.approach}")
                    test_log.update_approach(i, "running")
                    live.update(test_log.render_tasks())
                    soup_before = BeautifulSoup(self.cf.driver.page_source, "html.parser")
                    soup_before = filter_html(soup_before)
                    test = TestModel(approach=plan.approach, steps=[], soup_before_str=soup_before.prettify(), plan=plan)
                    self.cf.driver.get(f"{self.cf.target}{uri}")
                    time.sleep(self.cf.selenium_rate)
                    plan_str = "\n".join(plan.plan)
                    for j, task in enumerate(plan.plan):
                        test_log.update_task(i, j, "running")
                        live.update(test_log.render_tasks())
                        # logger.info(f"# Executing task: {task}")
                        completed_task = CompletedTask(task=task)
                        try:
                            solved_state = solver_executor.invoke(
                                {
                                    "task": task,
                                    "interaction": state["interaction"],
                                    "page_soup": state["page_soup"],
                                    "approach": plan.approach,
                                    "plan_str": plan_str,
                                }
                            )
                            completed_task.status = solved_state["output"]["status"]
                            completed_task.result = solved_state["output"]["result"]
                        except Exception as e:
                            completed_task.status = "error"
                            completed_task.result = str(e)
                        completed_task.tool_history = context.get_tool_history_reset()
                        test.steps.append(completed_task)
                        test_log.update_task(i, j, "done")
                        live.update(test_log.render_tasks())
                    # getting page source:
                    originial_soup = BeautifulSoup(self.cf.driver.page_source, "html.parser")
                    soup_after = filter_html(originial_soup)
                    test.soup_after_str = soup_after.prettify()
                    # parsing page requests and filtering them with LLM
                    p_reqs = parse_page_requests(driver=self.cf.driver, target=self.cf.target, uri=uri, filtered=True)
                    p_reqs_llm = llm_parse_requests_for_apis(
                        self.cf, json.dumps(p_reqs, indent=4)
                    )  # maybe dont parse with LLM? let that do the reporter?
                    test.outgoing_requests_after = p_reqs_llm
                    test_log.update_approach(i, "done")
                    live.update(test_log.render_tasks())

                    tests.append(test)
            return {"tests": state["tests"] + tests, "plans": []}

        def high_level_replan_step(state: PlanExecute):
            """
            Loops over all tests in current state and decides if a new plan is needed for each test.
            """
            new_plans = []
            tests = state["tests"]
            tests_to_check = [test for test in tests if not test.checked]
            tests_checked = [test for test in tests if test.checked]
            logger.info(f"Replanner step")
            for test in tests_to_check:
                logger.info(f"Replanning for approach: {test.approach}")
                logger.info(f"State keys: {state.keys()}")
                uri = state["uri"]
                interaction = state["interaction"]
                page_source_diff = unified_diff(
                    test.soup_before_str.splitlines(),
                    test.soup_after_str.splitlines(),
                    lineterm="",
                )
                page_source_diff = "\n".join(list(page_source_diff)).strip()
                input = {
                    "uri": uri,
                    "interaction": interaction,
                    "approach": test.approach,
                    "previous_plan": "\n".join(test.plan.plan),
                    "steps": format_steps(test.steps),
                    "outgoing_requests": json.dumps(test.outgoing_requests_after, indent=4),
                    "page_source_diff": page_source_diff,
                }

                descision = high_level_replanner.invoke(input=input)
                if isinstance(descision.action, PlanModel):
                    logger.info(f"Descision: New plan is needed")
                    logger.info(f"New Plan: {descision.action.plan}")
                    # remove the old test from state["tests"]
                    test.checked = True
                    test.in_report = False
                    tests_checked.append(test)
                    new_plans.append(descision.action)
                elif isinstance(descision.action, Response):
                    logger.info(f"Descision: No new plan is needed")
                    logger.info(f"Response: {descision.action.text}")
                    test.checked = True
                    test.in_report = True
                    tests_checked.append(test)
            return {"tests": tests_checked, "plans": new_plans}

        def report_step(state: PlanExecute):
            logger.info(f"Report step")
            interaction = json.dumps(state["interaction"], indent=4)
            uri = state["uri"]
            messages = [
                (
                    "system",
                    system_reporter_prompt.format(interaction=interaction, uri=uri)
                    .replace("{", "{{")
                    .replace("}", "}}"),
                )
            ]
            tests_to_report = [test for test in state["tests"] if test.in_report]
            for test in tests_to_report:
                steps = format_steps(test.steps)
                page_source_diff = unified_diff(
                    test.soup_before_str.splitlines(),
                    test.soup_after_str.splitlines(),
                    lineterm="",
                )
                page_source_diff = "\n".join(list(page_source_diff)).strip()
                this_human_reporter_prompt = human_reporter_prompt.format(
                    approach=test.approach,
                    plan="\n".join(test.plan.plan),
                    outgoing_requests=json.dumps(test.outgoing_requests_after, indent=4),
                    page_source_diff=page_source_diff,
                    steps=steps,
                )
                messages.append(("user", this_human_reporter_prompt.replace("{", "{{").replace("}", "}}")))
            messages.append(("placeholder", "{messages}"))

            reporter_prompt = ChatPromptTemplate.from_messages(messages)
            reporter = reporter_prompt | self.cf.advanced_model | self.cf.parser

            report = reporter.invoke(input={})
            logger.info(f"Report:\n{report}")
            return {"report": "final dummy report"}

        workflow = StateGraph(PlanExecute)
        workflow.add_node("high_high_level_planner", high_high_level_planner)
        workflow.add_node("high_level_planner", high_level_plan_step)
        workflow.add_node("executer", execute_step)
        workflow.add_node("high_level_replanner", high_level_replan_step)
        workflow.add_node("reporter", report_step)

        workflow.add_edge(START, "high_high_level_planner")
        workflow.add_edge("high_high_level_planner", "high_level_planner")
        workflow.add_edge("high_level_planner", "executer")
        workflow.add_edge("executer", "high_level_replanner")
        workflow.add_conditional_edges("high_level_replanner", should_report)
        workflow.add_edge("reporter", END)
        app = workflow.compile()

        return app

    def interact(self, uri: str, interaction: str, limit: str = "3") -> str:
        # initial steps: navigate and get soup
        self.cf.driver.get(f"{self.cf.target}{uri}")
        time.sleep(self.cf.selenium_rate)
        originial_soup = BeautifulSoup(self.cf.driver.page_source, "html.parser")
        soup = filter_html(originial_soup).prettify()

        result = self.app.invoke(input={"interaction": interaction, "uri": uri, "page_soup": soup, "limit": limit})

        return result["report"]
