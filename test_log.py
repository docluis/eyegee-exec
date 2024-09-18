from typing import List

from rich.console import Console
from rich.spinner import Spinner
from rich.live import Live
from rich.table import Table
from rich.text import Text
from time import sleep

from src.discovery.interaction_agent.agent_classes import PlanModel

console = Console()

class TestLog():
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
        table = Table.grid(padding=(0, 5))
        table.add_column("Task", justify="left", overflow="crop", no_wrap=True)
        table.add_column("Status", justify="left", overflow="crop", no_wrap=True, min_width=15)

        def get_status_display(status):
            return {
                "running": (Spinner("dots", text="running"), "bold"),
                # "running": (Text("running...", style="bold green"), "bold dim"),
                "done": (Text("✓ completed", style="bold blue"), "bold dim"),
                "waiting": (Text("waiting...", style="bold yellow"), "bold dim")
            }.get(status, (Text(status), "bold"))

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



test_plans = [
    PlanModel(approach="approach1 very long text blablablablablablabalbalbalblablabalbalbalbalbalbalbalablbalabalb", plan=["step1", "step2", "step3", "step4", "step5", "step6", "step7", "step8", "step9", "step10"]),
    PlanModel(approach="approach2", plan=["step1", "step2", "step3", "step4", "step5", "step6", "step7", "step8", "step9", "step10"]),
    PlanModel(approach="approach3", plan=["step1", "step2", "step3", "step4", "step5", "step6", "step7", "step8", "step9", "step10"]),
]

test_log = TestLog(test_plans)



with Live(test_log.render_tasks(), refresh_per_second=10, console=console) as live:
    for i, plan in enumerate(test_plans):
        # Update the status of the current task
        test_log.update_approach(i, "running")
        live.update(test_log.render_tasks())

        # Simulate something before the tasks
        for _ in range(10):
            sleep(0.1)
        
        for j, task in enumerate(plan.plan):
            test_log.update_task(i, j, "running")
            live.update(test_log.render_tasks())
            sleep(0.5)
            test_log.update_task(i, j, "done")
            live.update(test_log.render_tasks())

        # Simulate something after the tasks
        for _ in range(10):
            sleep(0.1)

        # Mark the task as completed
        test_log.update_approach(i, "done")
        live.update(test_log.render_tasks())
