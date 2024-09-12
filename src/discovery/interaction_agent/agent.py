import operator


import time
from typing import Dict, Literal, TypedDict, List, Annotated, Tuple, Union
from bs4 import BeautifulSoup
from langgraph.graph import StateGraph, START, END

# from pydantic import BaseModel
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain.agents import AgentExecutor, create_react_agent
from langchain.agents.output_parsers import JSONAgentOutputParser

from config import Config
from src.discovery.interaction_agent.tools.click import Click
from src.discovery.interaction_agent.tools.fill_text_field import FillTextField
from src.discovery.interaction_agent.executer import Executer, TaskModel
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


class TestModel(BaseModel):
    """Model for representing a test for a single approach."""

    approach: str = Field(description="The approach for the interaction feature.")
    steps: List[TaskModel] = Field(description="The step-by-step plan for this approach.")


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
    plan: List[PlanModel]
    tests: Annotated[List[TestModel], operator.add]
    # past_steps: Annotated[List[TaskModel], operator.add]
    response: str
    approaches: List[str]


class InteractionAgent:
    def __init__(self, cf: Config) -> None:
        self.cf = cf
        self.tools = self._init_tools()
        self.app = self._init_app()

    def _init_tools(self):
        return [Click(cf=self.cf), FillTextField(cf=self.cf)]

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
        high_level_planner = high_level_planner_prompt | self.cf.model.with_structured_output(PlanModel)
        solver = create_react_agent(
            self.cf.model, tools=self.tools, prompt=react_agent_prompt, output_parser=JSONAgentOutputParser()
        )
        sovler_executor = AgentExecutor(agent=solver, tools=self.tools)

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
            # TODO: Recreate this so that completed tasks are grouped by approach (basically overwrite the PlanModel)
            tests = []
            # executer = Executer(self.cf)
            for plan in state["plan"]:
                logger.info(f"Approach: {plan.approach}")
                test = TestModel(approach=plan.approach, steps=[])
                self.cf.driver.get(f"{self.cf.target}{state['uri']}")
                time.sleep(self.cf.selenium_rate)
                for step in plan.plan:
                    # res = executer.execute(
                    #     approach=plan.approach,
                    #     plan=plan.plan,
                    #     interaction=state["interaction"],
                    #     soup=state["page_soup"],
                    #     step=step,
                    # )
                    # test.steps.append(res)
                    output = sovler_executor.invoke(
                        {
                            "task": step,
                            "interaction": state["interaction"],
                            "page_soup": state["page_soup"],
                            "approach": plan.approach,
                        }
                    )
                    logger.info(f"#### Output:\n"
                                f"approach: {plan.approach}\n"
                                f"task: {output['task']}\n"
                                f"interaction: {output['interaction']}\n"
                                "####\n")
                # tests.append(test)
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

        result = self.app.invoke({"interaction": interaction, "uri": uri, "page_soup": soup, "limit": limit})
        print("\n\n######## DONE ########\n\n")

        # print("Plans:")
        # for plan in result["plan"]:
        #     print(f"Approach: {plan.approach}")
        #     for step in plan.plan:
        #         print(f"\t{step}")
        # print("\n\nPast Steps:")
        # for step in result["past_steps"]:
        #     print(f"Task: {step.task}")

        #     print(f"Status: {step.status}")
        #     print(f"Result: {step.result}")
        # print("\n\nResponse:")
        # print(result["response"])

        # print("Past Steps")
        # for i, approach in enumerate(result["approaches"]):
        #     print(f"{i}. Approach: {approach}")
        #     tasks = result["past_steps"][i]

        # print("Tests:")
        # for test in result["tests"]:
        #     print(f"Approach: {test.approach}")
        #     for step in test.steps:
        #         print(f"\t{step.task}")
        #         print(f"\t\tStatus: {step.status}")
        #         print(f"\t\tResult: {step.result}")
        return result
