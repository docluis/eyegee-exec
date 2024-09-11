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

res = agent.interact(uri, interaction)
# print(res)