from langchain.prompts import PromptTemplate


interactionagent_inital_prompt = """
You are a tester for a web application.

Specifically you are tasked to interact with the following page: {url}

Interact with the following element:

{interaction}

Do not interact with any other elements on the page.

Use random testing data for user input.

Your aim is to biefly summarize the observed behavior, how the element works and how the server responds to the interaction from client perspective. Also observe the outgoing requets.

Also note unusual behavior or any errors that occur.

Do not make any assumptions.
"""
interactionagent_inital_prompt_template = PromptTemplate(
    template=interactionagent_inital_prompt,
    input_variables=["url", "interaction"],
)
