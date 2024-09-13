from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage, SystemMessage

system_high_high_level_planner_prompt = """
You are a professional web tester assigned to evaluate a specific element on a web application page.

Create a high-level plan of different approaches to test an interaction feature.
The goal is to cover the full functionality of this element, including intended use cases as well as identifying possible error messages.

# Example:
Input:
*URI*: /search
*Element*:
{{"name": "Search Field", "description": "A field to search for cards."}}
*Page Soup*:
HTML code of the page

Output:
*Approaches*:
1. Test the search field with a valid search query.
2. Test the search field with an invalid search query.
3. Test the search field with special characters.
4. Test the search field with an empty search query.

Limit your plan to max {limit} approaches. Cover as much functionality as possible with a minimum number of approaches.

"""

human_high_high_level_planner_prompt = """
*URI*: {uri}
*Element*:
{interaction}
*Page Soup*:
{page_soup}

"""

high_high_level_planner_prompt = ChatPromptTemplate(
    [
        ("system", system_high_high_level_planner_prompt),
        ("human", human_high_high_level_planner_prompt),
        ("placeholder", "{messages}"),
    ]
)


system_high_level_planner_prompt = """
You are a professional web tester assigned to evaluate a specific element on a web application page.

Given a specific approach create a plan of individual steps to test an interaction feature.
The goal is to uncover the functionality of the element given the current approach.

This plan should be specific to the element, the page soup and the current approach, however this is just the initial plan, thus it should not be too detailed.

Keep in mind that the page is already loaded and you have access to the page soup.
For interaction that likely send requests, make sure to analyze the outgoing requests and include it in the plan.
Also examine how the page responds to the interaction by analyzing the page soup.

# Example:
Input:
*URI*: /login
*Element*:
{{"name": "Login Form", "description": "A form to login to the application."}}
*Approach*: Test the login form with username and password containing special characters.
*Page Soup*:
HTML code of the page

Output:
*PlanModel*:
approach: Test the login form with username and password containing special characters.
plan: ["Enter a username with special characters.", "Enter a password with special characters.", "Click the login button.", "Check Outgoing Requests for login attempt.", "Check Page Soup for error messages or success messages"]

"""

human_high_level_planner_prompt = """
*URI*: {uri}
*Element*:
{interaction}
*Approach*:
{approach}
*Page Soup*:
{page_soup}

"""

high_level_planner_prompt = ChatPromptTemplate(
    [
        ("system", system_high_level_planner_prompt),
        ("human", human_high_level_planner_prompt),
        ("placeholder", "{messages}"),
    ]
)


system_execute_prompt = """
You are a professional web tester assigned to execute a single step of a plan to test an interaction feature.

This is the current testing approach:

{approach}

This is the entire plan:

{plan}

The feature you are testing is:

{interaction}
Only execute a single step of this plan. The page is already loaded and you have access to the page soup.
Page Soup:
{page_soup}
"""


human_execute_prompt = """
You are currently executing the following step:

{step}

Only finish when you have completed the step successfully.
"""

execute_prompt = ChatPromptTemplate(
    [
        ("system", system_execute_prompt),
        ("human", human_execute_prompt),
        ("placeholder", "{messages}"),
    ]
)

system_execute_summary_prompt = """
Now create a summary of the task attempted to execute. Include all relevant information.
"""
# react_agent_prompt = ChatPromptTemplate.from_template(
#     """
# You are tasked with interacting with a web page to test a specific feature.
# The website source page is:
# ```html
# {page_soup}
# ```
# The feature you are testing is:
# {interaction}
# Your aproach is: {approach}
# Solve the following tasks as best you can. You have access to the following tools:
# {tools}
# Use the following format:
# Question: the input question you must answer
# Thought: you should always think about what to do
# Action: the action to take, should be one of [{tool_names}]
# Action Input: the input to the action
# Observation: the result of the action
# ... (this Thought/Action/Action Input/Observation can repeat N times)
# Thought: I now know the final answer
# Final Answer: the final answer to the original input question
# Begin!
# Task: {task}
# Thought:{agent_scratchpad}
# """
# )
system_react_agent_prompt = """
You are tasked with interacting with a web page to test a specific feature.

The website source page is:
```html
{page_soup}
```

The feature you are testing is:
{interaction}

Your aproach is: {approach}

Respond to the human as helpfully and accurately as possible. You have access to the following tools:
{tools}
Use a json blob to specify a tool by providing an action key (tool name) and an action_input key (tool input).
Valid "action" values: "Final Answer" or {tool_names}
Provide only ONE action per $JSON_BLOB, as shown:

```
{{
  "action": $TOOL_NAME,
  "action_input": $INPUT
}}
```

Follow this format:
Question: input question to answer
Thought: consider previous and subsequent steps
Action:
```
$JSON_BLOB
```
Observation: action result
... (repeat Thought/Action/Observation N times)
Thought: I know what to respond
Action:
```
{{
  "action": "Final Answer",
  "action_input": {{
    "result": "Final response to human, noting any important details",
    "status": "Status of the individiual task (either 'success', 'failure', or 'incomplete')"
  }}
}}
```

Begin! Reminder to ALWAYS respond with a valid json blob of a single action. Use tools if necessary. Respond directly if appropriate. Format is Action:```$JSON_BLOB```then Observation. Never include ```json in your response.
"""

human_react_agent_prompt = """
Task: {task}

Make sure to only move on and provide the final answer, when you have completed the current task.

Try to solve the task carefully and accurately. Attempt multiple times before returning a 'failure' or 'incomplete' status.

Thought: {agent_scratchpad}
(reminder to respond in a JSON blob no matter what)
"""

react_agent_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system_react_agent_prompt),
        ("human", human_react_agent_prompt),
    ]
)
