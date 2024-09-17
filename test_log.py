import time

from rich.live import Live
from rich.console import Console


from src.pretty_log import FeatureTable
from src.discovery.interaction_agent.agent_classes import PlanModel

console = Console()
example_plans = [
    PlanModel(approach="approach1", plan=["step1", "step2", "step3"]),
    PlanModel(approach="approach2", plan=["step1", "step2"]),
    PlanModel(approach="approach3", plan=["step1", "step2", "step3", "step4"]),
]

with Live(refresh_per_second=10, console=console) as live:
    table = FeatureTable(example_plans, live)
    table.update_approach(0, "running")
    table.update_step(0, 0, "running")
    time.sleep(2)
    table.update_step(0, 0, "success")
    table.update_step(0, 1, "running")
    time.sleep(2)
    table.update_step(0, 1, "success")
    table.update_step(0, 2, "running")
    time.sleep(2)
    table.update_step(0, 2, "success")
    table.update_approach(0, "success")
    table.update_approach(1, "running")
    table.update_step(1, 0, "running")
    time.sleep(2)
    table.update_step(1, 0, "success")
    table.update_step(1, 1, "running")
    time.sleep(2)
    table.update_step(1, 1, "success")
    table.update_approach(1, "success")
    table.update_approach(2, "running")
    table.update_step(2, 0, "running")
    time.sleep(2)
    table.update_step(2, 0, "success")
    table.update_step(2, 1, "running")
    time.sleep(2)
    table.update_step(2, 1, "success")
    table.update_step(2, 2, "running")
    time.sleep(2)
    table.update_step(2, 2, "success")
    table.update_step(2, 3, "running")
    time.sleep(2)
    table.update_step(2, 3, "success")
    table.update_approach(2, "success")
