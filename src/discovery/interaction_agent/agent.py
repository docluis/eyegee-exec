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
from src.discovery.interaction_agent.tool_context import ToolContext
from src.discovery.interaction_agent.tools.click import Click
from src.discovery.interaction_agent.tools.fill_text_field import FillTextField
from src.discovery.interaction_agent.tools.navigate import Navigate
from src.discovery.interaction_agent.tools.get_page_soup import GetPageSoup
from src.discovery.interaction_agent.tools.get_outgoing_requests import GetOutgoingRequests
from src.discovery.interaction_agent.tools.select_option import SelectOption
from src.log import logger
from src.discovery.utils import filter_html
from src.discovery.interaction_agent.prompts import (
    high_high_level_planner_prompt,
    high_level_planner_prompt,
    react_agent_prompt,
)


class HighHighLevelPlan(BaseModel):
    """High-level plan for testing an interaction feature."""

    approaches: List[str] = Field(
        description="Different approaches to test an interaction feature, should be in sorted order"
    )


class PlanModel(BaseModel):
    """Model for representing the plan for a single approach."""

    approach: str = Field(description="The approach for the interaction feature.")
    plan: List[str] = Field(description="The step-by-step plan for this approach.")


class CompletedTask(BaseModel):
    """Model for representing a completed step of a plan for a single approach."""

    task: str = Field(description="The task that was executed.")
    status: str = Field(default="pending", description="The status of the task.")
    result: str = Field(default="", description="The result of the task.")


class TestModel(BaseModel):
    """Model for representing a test for a single approach."""

    approach: str = Field(description="The approach for the interaction feature.")
    steps: List[CompletedTask] = Field(description="The steps executed for this approach.")


class HighLevelPlan(BaseModel):
    """High-level plan for each approach."""

    plan: List[PlanModel] = Field(description="Detailed plans for each approach")


class Response(BaseModel):
    """Response to user."""

    response: str


class Act(BaseModel):
    """Action to perform."""

    action: Union[Response, HighLevelPlan] = Field(
        description="Action to perform. If you want to respond to user, use Response. "
        "If you need to further use tools to get the answer, use HighLevelPlan."
    )


class PlanExecute(TypedDict):
    uri: str
    interaction: str
    page_soup: str
    limit: str
    approaches: List[str]
    plan: List[PlanModel]
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
            GetOutgoingRequests(cf=self.cf, context=context),
            SelectOption(cf=self.cf, context=context),
        ]

    def _init_app(self):
        def should_end(state: PlanExecute) -> Literal["executer", "__end__"]:
            if "response" in state and state["response"]:
                return "__end__"
            else:
                return "executer"

        print_and_return = lambda x: print(x) or x

        high_high_level_planner = high_high_level_planner_prompt | self.cf.model.with_structured_output(
            HighHighLevelPlan
        )
        # TODO: add tool info to the prompt?
        high_level_planner = high_level_planner_prompt | self.cf.model.with_structured_output(PlanModel)

        def high_level_plan_step(state: PlanExecute) -> HighLevelPlan:
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

            return HighLevelPlan(plan=plans)

        def execute_step(state: PlanExecute):
            tests = []
            uri = state["uri"]
            for plan in state["plan"]:
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

                context = ToolContext(cf=self.cf, initial_uri=uri) # Create a new context for each test
                tools = self._init_tools(context)
                solver = create_react_agent(
                    self.cf.model, tools=tools, prompt=react_agent_prompt, output_parser=JSONAgentOutputParser()
                )
                solver_executor = AgentExecutor(agent=solver, tools=tools)
                logger.info(f"Approach: {plan.approach}")
                test = TestModel(approach=plan.approach, steps=[])
                self.cf.driver.get(f"{self.cf.target}{uri}")
                time.sleep(self.cf.selenium_rate)
                for task in plan.plan:
                    completed_task = CompletedTask(task=task)
                    solved_state = solver_executor.invoke(
                        {
                            "task": task,
                            "interaction": state["interaction"],
                            "page_soup": state["page_soup"],
                            "approach": plan.approach,
                        }
                    )
                    print(f"solved state keys: {solved_state.keys()}")
                    completed_task.status = solved_state["output"]["status"]
                    completed_task.result = solved_state["output"]["result"]
                    # TODO: get outgoing requests + diff page soup here?
                    # maybe statically parse the page soup here and compare with the original soup
                    # same for outgoing requests, maybe its better to just statically parse the requests here,
                    # instead of letting the agent use the tool
                    # we could pass to the reporter (and replanner):
                    #   - approach
                    #   - plan
                    #   - state.steps
                    #   - tool_histories
                    #   - the soup changes
                    #   - the outgoing requests change
                    #   - the links change (absolute?)
                    test.steps.append(completed_task)
                tests.append(test)
                logger.info(f"Tool history: {context.tool_history}")
            return {"tests": state["tests"] + tests}

        def high_level_replan_step(state: PlanExecute) -> PlanExecute:
            # look at the current state and decide if we need to replan
            descision = Act(action=Response(response="Dummy Response"))  # TODO: Implement this, for now dummy code
            if isinstance(descision.action, Response):
                return {"response": descision.action.response}
            else:
                return {"plan": descision.action.plan}

        workflow = StateGraph(PlanExecute)
        workflow.add_node("high_high_level_planner", high_high_level_planner)
        workflow.add_node("high_level_planner", high_level_plan_step)
        workflow.add_node("executer", execute_step)
        workflow.add_node("high_level_replanner", high_level_replan_step)

        workflow.add_edge(START, "high_high_level_planner")

        workflow.add_edge("high_high_level_planner", "high_level_planner")
        workflow.add_edge("high_level_planner", "executer")
        workflow.add_edge("executer", "high_level_replanner")
        workflow.add_conditional_edges("high_level_replanner", should_end)

        # workflow.add_edge("high_level_planner", END)

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
            for step in test.steps:
                print(f"Task: {step.task}")
                print(f"Status: {step.status}")
                print(f"Result: {step.result}")
                print("\n")
            print("\n\n")

        return result
