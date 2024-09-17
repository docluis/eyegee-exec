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

Given a specific approach, create a plan of individual steps to test an interaction feature. The goal is to uncover the functionality of the element using the current approach.

This plan should:
  - Be specific to the element, the page soup, and the current approach.
  - Be minimal and not overly detailed, as it is just the initial plan.
  - *Focus solely on the actions to perform, without making any assumptions about expected behaviors or outcomes.*

*Important*:
  - Do not include any steps that involve verifying specific behaviors or outcomes (e.g., avoid steps like "Verify that an error message is displayed").
  - Do not make any assumptions about how web applications should behave.
  - Keep the steps minimal and action-oriented.

Keep in mind that the page is already loaded, and you have access to the page soup.

Example:

Input:
- URI: /login
- Element:
  {{"name": "Login Button", "description": "A button to login to the application"}}
- Approach: Test the login form with username and password containing special characters.
- Page Soup: HTML code of the page

Output:
- PlanModel:
  - approach: Test the login form with username and password containing special characters.
  - plan:
    - Fill in the username field with a special character
    - Fill in the password field with a special character
    - Click the login button

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

system_react_agent_prompt = """
You are tasked with interacting with a web page to test a specific feature.

Report to the human as helpfully and accurately as possible. You have access to the following tools:
{tools}

*Important*: When specifying tool actions, the input must always be structured in a nested JSON object. Avoid placing the tool input directly as a string. Instead, include any required parameters (such as identifiers, methods, etc.) inside a key-value format, as shown below. This ensures that tools receive the correct inputs.

You must use a JSON blob to specify a tool by providing an `action` key (tool name) and an `action_input` key (tool input). Always ensure the input fields are organized correctly within the `action_input`.

Valid "action" values: "Final Answer" or {tool_names}

Format:

```
{{
  "action": $TOOL_NAME,
  "action_input": {{
    "key_1": "value_1",
    "key_2": "value_2",
    ...
  }}
}}
```

*Provide only ONE action per $JSON_BLOB*. Example format:

```
{{
  "action": $TOOL_NAME,
  "action_input": {{
    "xpath_identifier": "//input[@aria-label='Submit']",
    "using_javascript": true
  }}
}}
```

Follow this format:

Task: input task to complete
Thought: consider previous and subsequent steps
Action:
```
$JSON_BLOB
```
Observation: action result
Thought: consider previous and subsequent steps
Action:
```
$JSON_BLOB
```
Observation: action result
... (repeat Thought/Action/Observation N times)
Thought: I have completed the current task / I was unable to complete the current task
Action:
```
{{
  "action": "Final Answer",
  "action_input": {{
    "result": "I have completed the current task (add details as to what was done) / I was unable to complete the current task (add details as to why if applicable)",
    "status": "Status of the individiual task (either 'success', 'failure', or 'incomplete')"
  }}
}}
```
Never include ```json in your response.

Begin! *Reminder to ALWAYS respond with a valid json blob* of a single action. Use tools if necessary.
If you have completed the task, respond with the final answer directly.
"""

human_react_agent_prompt = """
Website source page:
```
{page_soup}
```

The feature you are testing is:
{interaction}

The approach you are using is:
{approach}

Your plan is:
{plan_str}

The specific task you are now executing is: *{task}*

IMPORTANT: ONLY EXECUTE THIS SPECIFIC TASK. DO NOT DEVIATE FROM IT AND DO NOT SOLVE OTHER TASKS.

Try to solve the task carefully and accurately. If you are unsuccessful after 5 attempts, respond with the status 'failure' and provide a detailed explanation of the steps you have taken.

Thought: {agent_scratchpad}
(reminder to respond in a JSON blob no matter what)
"""

react_agent_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system_react_agent_prompt),
        ("human", human_react_agent_prompt),
    ]
)

system_high_level_replanner_prompt = """
You are a professional web tester assigned to evaluate a specific element on a web application page.

Given a specific approach, the previous plan, and the observed steps, the goal is to further test the functionality of the element using the current approach.

You are tasked with evaluating the following feature of a web application:
{interaction}

Your approach is:
{approach}

*Important*:
- Only return a new plan if the previous plan did not fully test the feature.
- Keep the steps minimal and action-oriented, without assumptions about how the feature should behave.
- Do not include any steps that verify specific behaviors or outcomes.
- If no further interaction is needed and the plan is complete, respond to the user indicating the test is finished.

This plan should focus solely on actions to perform, based on what was observed, without assuming any specific outcome.
"""

human_high_level_replanner_prompt = """
Your previous plan was:
{previous_plan}

You performed the following steps:
{previous_steps}

Keep in mind that the specific output of the tools has been shortened for the sake of readability. For generating the final output for the user, this data will be provided in full.

You observed these outgoing requests:
{outgoing_requests}

The page source difference before and after interaction:
{page_source_diff}

Based on this, determine if a new plan is necessary, and if so, provide a minimal new plan focused on interaction actions only.
New plans should contain all necessary steps to test the feature.

*Important*: Only return a new plan if the previous plan did not fully test the feature.

If you are satisfied with the previous plan and the observed steps, you can return a Response to the user stating that the test is complete.
"""


high_level_replanner_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system_high_level_replanner_prompt),
        ("human", human_high_level_replanner_prompt),
    ]
)
