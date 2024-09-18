from typing import List

from rich.console import Console
from rich.spinner import Spinner
from rich.live import Live
from rich.table import Table
from rich.text import Text
from time import sleep

from src.discovery.interaction_agent.agent_classes import PlanModel, TestModel


def get_status_display(status):
    return {
        "running": (Spinner("dots", text="running"), "bold"),
        # "running": (Text("running...", style="bold green"), "bold dim"),
        "done": (Text("✓ completed", style="bold blue"), "bold dim"),
        "waiting": (Text("waiting...", style="bold yellow"), "bold dim"),
    }.get(status, (Text(status), "bold"))


def get_initial_table():
    table = Table.grid(padding=(0, 5))
    table.add_column("Task", justify="left", overflow="crop")
    table.add_column("Status", justify="left", overflow="crop", no_wrap=True, min_width=15)
    return table


class ExecutorLog:
    def __init__(self, plans: List[PlanModel]):
        self.data = self._init_data(plans)

    def _init_data(self, plans: List[PlanModel]):
        data = []
        for plan in plans:
            this_test = {"approach": plan.approach, "tasks": [], "status": "waiting"}
            for task in plan.plan:
                this_test["tasks"].append({"name": task, "status": "waiting"})
            data.append(this_test)
        return data

    def render_tasks(self) -> Table:
        table = get_initial_table()
        for test in self.data:
            status_display, style = get_status_display(test["status"])
            table.add_row(Text(f"Approach: {test['approach']}", style=style), status_display)

            if test["status"] in ["running", "done"]:
                for task in test["tasks"]:
                    status_display, style = get_status_display(task["status"])
                    table.add_row(Text(f"  • Task: {task['name']}", style=style), status_display)

        return table

    def update_approach(self, approach_index: int, status: str):
        self.data[approach_index]["status"] = status

    def update_task(self, approach_index: int, task_index: int, status: str):
        self.data[approach_index]["tasks"][task_index]["status"] = status


class HighHighLevelPlannerLog:
    def __init__(self):
        self.status = "waiting"

    def update_status(self, status: str):
        self.status = status

    def render(self) -> Table:
        table = get_initial_table()
        status_display, style = get_status_display(self.status)
        table.add_row(Text("Generating Approaches", style=style), status_display)
        return table


class HighLevelPlannerLog:
    def __init__(self, approaches: List[str]):
        self.data = self._init_data(approaches)

    def _init_data(self, approaches: List[str]):
        data = []
        for approach in approaches:
            data.append({"approach": approach, "status": "waiting"})
        return data

    def update_approach(self, approach_index: int, status: str):
        self.data[approach_index]["status"] = status

    def render(self) -> Table:
        table = get_initial_table()
        for approach in self.data:
            status_display, style = get_status_display(approach["status"])
            table.add_row(Text(f"Generating Plan for Approach: {approach['approach']}", style=style), status_display)
        return table


class HighLevelReplannerLog:
    def __init__(self, tests_to_check: List[TestModel]):
        self.data = self._init_data(tests_to_check)

    def _init_data(self, tests_to_check: List[TestModel]):
        data = []
        for test in tests_to_check:
            data.append({"approach": test.approach, "status": "waiting", "result": None})
        return data

    def update_test(self, test_index: int, status: str, result: str | None):
        self.data[test_index]["status"] = status
        self.data[test_index]["result"] = result

    def render(self) -> Table:
        table = get_initial_table()
        for test in self.data:
            status_display, style = get_status_display(test["status"])
            table.add_row(Text(f"Approach: {test['approach']}", style=style), status_display)

            if test["status"] in ["done"] and test["result"] is not None:
                table.add_row(Text(f"  • Result: {test['result']}", style=style), "")

        return table
    

class ReporterLog:
    def __init__(self):
        self.status = "waiting"

    def update_status(self, status: str):
        self.status = status

    def render(self) -> Table:
        table = get_initial_table()
        status_display, style = get_status_display(self.status)
        table.add_row(Text("Generating Report", style=style), status_display)
        return table