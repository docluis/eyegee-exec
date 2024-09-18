import json
from src.discovery.interaction import Interaction
from src.discovery.interaction_agent.agent import InteractionAgent
from config import Config

cf = Config()
from src.discovery.interaction import Interaction


interaction = json.dumps(
    Interaction(
        name="Registration Form",
        description="A form to register new users.",
        input_fields={},
    ).to_dict()
)
uri = "/register"
agent = InteractionAgent(cf)

report, p_reqs, observed_uris = agent.interact(uri, interaction, limit="3")
print("*"*100)
print("Final Report:")
print(report)
print("*"*100)
print("Page Requests:")
print(p_reqs)
print("*"*100)
print("Observed URIs:")
print(observed_uris)