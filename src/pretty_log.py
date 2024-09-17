import time

from typing import List, Literal, Tuple

from rich.live import Live
from rich.table import Table
from rich.console import Console
from rich.spinner import Spinner
from rich.text import Text

from src.discovery.interaction_agent.agent_classes import PlanModel

Status = Literal["error", "success", "failure", "incomplete", "running", "pending"]


class FeatureTable:
    def __init__(self, plans: List[PlanModel], live: Live):
        self.live = live
        self.approaches, self.steps = self._init_data(plans)

    def _init_data(self, plans: List[PlanModel]):
        approaches = []
        steps = []
        for plan in plans:
            these_steps = []
            approaches.append((plan.approach, "pending"))
            for step in plan.plan:
                these_steps.append((step, "pending"))
            steps.append(these_steps)
        return approaches, steps

    def update_approach(self, approach_index: int, status: Status):
        self.approaches[approach_index] = (self.approaches[approach_index][0], status)
        self.live.update(self.render())

    def update_step(self, approach_index: int, step_index: int, status: Status):
        self.steps[approach_index][step_index] = (self.steps[approach_index][step_index][0], status)
        self.live.update(self.render())

    def finish_all_approaches(self):
        for i in range(len(self.approaches)):
            self.live.update(self.render())

    def render(self):
        # TODO: handle fewer lines
        table = Table.grid(expand=False)
        table.add_column()
        table.add_column()

        for approach, plan in zip(self.approaches, self.steps):
            if approach[1] == "running":
                table.add_row(Text(approach[0], style="bold"), Text(""))
                for step in plan:
                    if step[1] == "running":
                        table.add_row(Text(f"  - {step[0]}"), Spinner("dots"))
                    elif step[1] == "success":
                        table.add_row(Text(f"  - {step[0]}", style="dim"), Text("✔", style="dim"))
                    elif step[1] == "failure" or step[1] == "error":
                        table.add_row(Text(f"  - {step[0]}", style="dim"), Text("❌", style="dim"))
                    elif step[1] == "incomplete":
                        table.add_row(Text(f"  - {step[0]}", style="dim"), Text("❓", style="dim"))
                    else:
                        table.add_row(Text(f"  - {step[0]}", style="dim"), Text(""))
            elif approach[1] == "pending":
                table.add_row(Text(approach[0], style="bold dim"), Text(""))
            else:
                table.add_row(Text(approach[0], style="bold dim"), Text("✔", style="dim"))
        return table
