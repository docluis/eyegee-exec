from difflib import unified_diff
import json
import operator


import time
from typing import Dict, Literal, TypedDict, List, Annotated, Tuple, Union
from bs4 import BeautifulSoup
from langgraph.graph import StateGraph, START, END

# from pydantic import BaseModel
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain.agents import create_react_agent, AgentExecutor
from langchain.agents.output_parsers import JSONAgentOutputParser

from config import Config
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
    response: str


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
        def should_report(state: PlanExecute) -> Literal["executer", "__end__"]:
            if "plans" in state and state["plans"] == []:
                return "__end__"
            else:
                return "executer"

        print_and_return = lambda x: print(x) or x

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
            for plan in state["plans"]:
                # we want to save the tool data for each plan
                # create a new context for each plan?
                # this would mean each plan needs its own tool
                # moving solver and solver_executor here is no problem
                # we could also create new tools here, with a new context
                # this context would passively store additional data
                # such as each tool call, with inputs and outputs
                # we can also track additional uris and so on here
                # old interactionagent returns p_requests, links, and soup (if new)
                # we could pass all the gathered data to the reporter

                context = ToolContext(cf=self.cf, initial_uri=uri)  # Create a new context for each test
                tools = self._init_tools(context)
                solver = create_react_agent(
                    self.cf.model, tools=tools, prompt=react_agent_prompt, output_parser=JSONAgentOutputParser()
                )
                solver_executor = AgentExecutor(agent=solver, tools=tools)
                logger.info("")
                logger.info(f"#### Next Approach: {plan.approach}")
                soup_before = BeautifulSoup(self.cf.driver.page_source, "html.parser")
                soup_before = filter_html(soup_before)
                test = TestModel(approach=plan.approach, steps=[], soup_before_str=soup_before.prettify(), plan=plan)
                self.cf.driver.get(f"{self.cf.target}{uri}")
                time.sleep(self.cf.selenium_rate)
                plan_str = "\n".join(plan.plan)
                for task in plan.plan:
                    logger.info(f"# Executing task: {task}")
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

                tests.append(test)
            return {"tests": state["tests"] + tests, "plans": []}

        def high_level_replan_step(state: PlanExecute):
            """
            Loops over all tests in current state and decides if a new plan is needed for each test.
            """
            new_plans = []
            logger.info(f"Replanner step")
            for test in state["tests"]:
                logger.info(f"Replanning for approach: {test.approach}")
                logger.info(f"State keys: {state.keys()}")
                uri = state["uri"]
                interaction = state["interaction"]
                # check if new plan is needed
                # i need to pass interaction, approach, previous_plan, previous_steps, outgoing_requests, page_soup_before, page_soup_after
                # print this list test.plan.plan in newlines
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
                    "previous_steps": format_steps(test.steps),
                    "outgoing_requests": json.dumps(test.outgoing_requests_after, indent=4),
                    "page_source_diff": page_source_diff,
                }

                descision = high_level_replanner.invoke(input=input)
                if isinstance(descision.action, PlanModel):
                    logger.info(f"Descision: New plan is needed")
                    logger.info(f"New Plan: {descision.action.plan}")
                    new_plans.append(descision.action)
                elif isinstance(descision.action, Response):
                    logger.info(f"Descision: No new plan is needed")
                    logger.info(f"Response: {descision.action.text}")

            return {"plans": []}  # currently dummy, so that no replanner is called
            # TODO: make sure only create new plans, if nessecary (more input fields), then pass the new plans to the executer
            # return {"plans": new_plans}

        workflow = StateGraph(PlanExecute)
        workflow.add_node("high_high_level_planner", high_high_level_planner)
        workflow.add_node("high_level_planner", high_level_plan_step)
        workflow.add_node("executer", execute_step)
        workflow.add_node("high_level_replanner", high_level_replan_step)

        workflow.add_edge(START, "high_high_level_planner")

        workflow.add_edge("high_high_level_planner", "high_level_planner")
        workflow.add_edge("high_level_planner", "executer")
        workflow.add_edge("executer", "high_level_replanner")
        workflow.add_conditional_edges("high_level_replanner", should_report)

        app = workflow.compile()

        mermaid = app.get_graph().draw_mermaid()
        print(f"mermaid:\n{mermaid}\n")
        return app

    def interact(self, uri: str, interaction: str, limit: str = "3") -> str:
        # initial steps: navigate and get soup
        self.cf.driver.get(f"{self.cf.target}{uri}")
        time.sleep(self.cf.selenium_rate)
        originial_soup = BeautifulSoup(self.cf.driver.page_source, "html.parser")
        soup = filter_html(originial_soup).prettify()

        result = self.app.invoke(input={"interaction": interaction, "uri": uri, "page_soup": soup, "limit": limit})

        print("\n\n######## DONE ########\n\n")

        # print the tests
        for test in result["tests"]:
            print(f"###Approach: {test.approach}")
            print(f"###Steps: {len(test.steps)}")
            for step in test.steps:
                print(f"Task: {step.task}")
                print(f"\tStatus: {step.status}")
                print(f"\tResult: {step.result}")
                # print(f"\tTool history: {step.tool_history}")
                print(f"\tTool history: {len(step.tool_history)}")
                for tool_call in step.tool_history:
                    print(f"\t\tTool call: {tool_call[0]}")
                    print(f"\t\tInput: {tool_call[1]}")
                    print(f"\t\tOutput")
                    print(f"\t\t\tSuccess: {tool_call[2].success}")
                    print(f"\t\t\tMessage: {tool_call[2].message}")
                    # print(f"\t\t\tError: {tool_call[2].error[:20] if tool_call[2].error else 'No error'}")
                    # (
                    #     print(f"\t\t\tOutgoing requests: {tool_call[2].outgoing_requests[:20]}")
                    #     if tool_call[2].outgoing_requests
                    #     else None
                    # )
                    # print(f"\t\t\tPage source: {tool_call[2].page_source[:20]}") if tool_call[2].page_source else None
                print("\n")
            print(f"Soup before: {test.soup_before_str[:20]}")
            print(f"Soup after: {test.soup_after_str[:20]}")
            print(f"Outgoing requests after: {test.outgoing_requests_after[:20]}")
            print("\n\n")

        return result
