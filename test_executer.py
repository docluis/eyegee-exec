import json
import time

from bs4 import BeautifulSoup
from src.discovery.utils import filter_html
from src.discovery.interaction_agent.executer import Executer
from src.discovery.interaction import Interaction
from config import Config

cf = Config()
from src.discovery.interaction import Interaction


approach = "Test the registration form with valid inputs for email, username, and password, ensuring the user can successfully register."
plan = [
    "Enter a valid email address in the email input field.",
    "Enter a valid username in the username input field.",
    "Enter a valid password in the password input field.",
    "Check the 'I agree to the terms and conditions' checkbox.",
    "Click the 'Register' button.",
]
formated_plan = json.dumps(plan)
step = "Check the 'I agree to the terms and conditions' checkbox."
# step = "Click the 'Register' button."
interaction = json.dumps(
    Interaction(
        name="Registration Form",
        description="A form to register new users.",
        input_fields={},
    ).to_dict()
)
uri = "/register"





cf.driver.get(f"{cf.target}{uri}")
time.sleep(2)
originial_soup = BeautifulSoup(cf.driver.page_source, "html.parser")
soup = filter_html(originial_soup).prettify()


executer = Executer(cf)

res = executer.execute(approach=approach, plan=plan, interaction=interaction, soup=soup, step=step)
print(res)
