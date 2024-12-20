from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage, SystemMessage

system_high_high_level_planner_prompt = """
You are a professional web tester tasked with evaluating a specific element on a web application. Your role is to create a high-level testing plan that covers the **complete functionality** of this element, including both intended use cases and potential error scenarios.

Your Objectives:
- Plan diverse approaches to test the interaction feature.
- Ensure the approaches cover **real-world usage** and **edge cases**.
- Limit the number of approaches to a maximum of **{limit}**.

Approach Guidelines:
- Each approach should be unique and cover a different aspect of the feature.
- Approaches should only focus on the actions to perform, not the expected outcomes.
- Approaches should not include any assumptions about the feature's behavior.
- All test are analyzed, so approaches should not contain any "verify" or "observe" steps.

Example Approaches:

Example 1:

- **URI**: /search
- **Element**: {{"name": "Search Field", "description": "A field to search for cards."}}
- **Page Soup**: (HTML code of the page that contains the search field)
- **Approaches**:
  - Test the search field with a valid query.
  - Test with special characters.

Example 2:

- **URI**: /login
- **Element**: {{"name": "Login Button", "description": "A button to log in to the application."}}
- **Page Soup**: (HTML code of the page that contains the username field, password field, and a login button)
- **Approaches**:
  - Test with a valid, unique username and password.
  - Test with a common username and weak password.
  - Test with empty username and password fields.

Reminder: You must generate exactly **{limit}** approach(es). Do not exceed this number.
"""



human_high_high_level_planner_prompt = """
*URI*: {uri}
*Element*:
{interaction}
*Page Soup*:
{page_soup}


Reminder: You must generate exactly **{limit}** approach(es). Do not exceed this number.
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
  - Generate **unique, realistic inputs** for each approach—avoid generic placeholders like "valid_username" or "invalid_password."
  - *Focus solely on the actions to perform, without making any assumptions about expected behaviors or outcomes.*
  - All test are analyzed, so any "verify" or "observe" steps are reduntant

Input Generation Guidance:
  - Only generate inputs if you are sure the target element exists on the page, do NOT make assumptions about potential input fields.
  - **Valid Inputs**: Use unique and properly formatted usernames (e.g., "user_test_random32ab") and strong passwords adhering to security best practices (e.g., "SecurePass$123").
  - **Likely-Taken Inputs**: Use common usernames (e.g., "admin", "user") or improperly formatted data that would trigger an error (e.g., no special characters for a password that requires them).
  - **Invalid Inputs**: Test with invalid or improperly formatted data that should lead to an error (e.g., "`~&$#@/password").
  
*Important*:
  - Do not include any steps that involve verifying specific behaviors or outcomes (e.g., avoid steps like "Verify that an error message is displayed").
  - Do not make any assumptions about how web applications should behave.
  - Generate the minimal amount of steps necessary to test the feature.
  - Keep the steps minimal and action-oriented.
  - **Do not include multiple actions that result in navigation** Once a navigation action is performed (e.g., clicking a button that changes the page), the plan should not include further actions on the original page.

Keep in mind that the page is already loaded, and you have access to the page soup.

Examples:

Example 1:

Input:
- URI: /register
- Element:
  {{"name": "Register Form", "description": "A form to register a new user"}}
- Approach: Test the registration form with valid inputs for username and password.
- Page Soup: HTML code of the page
- Context: -

Output:
- PlanModel:
  - approach: Test the registration form with valid inputs for username and password.
  - plan:
    - Fill in the username field with the text "user_test_123"
    - Fill in the password field with the text "SecurePass$123"
    - Check the "agree to terms and conditions" checkbox
    - Click the register button

Example 2:

Input:
- URI: /login
- Element:
  {{"name": "Login Form", "description": "A form to log in to the application"}}
- Approach: Test the login form with valid inputs.
- Page Soup: HTML code of the page
- Context: user_test_123:SecurePass$123 are valid credentials

Output:
- PlanModel:
  - approach: Test the login form with valid inputs.
  - plan:
    - Fill in the username field with the text "user_test_123"
    - Fill in the password field with the text "SecurePass$123"
    - Click the login button

"""

human_high_level_planner_prompt = """
*URI*: {uri}
*Element*:
{interaction}
*Approach*:
{approach}
*Page Soup*:
```
{page_soup}
```

*Context*:
{interaction_context}

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

*Important*:
- Consider any new elements or changes in the page source difference that indicate further interaction is needed to fully test the feature.
- Include interactions with these new elements in your new plan if necessary.
- Only return a new plan if the previous plan did not fully test the feature.
- If no further interaction is needed and the plan is complete, respond to the user indicating the test is finished.
- Keep in mind that the target interaction may not be fully functional or the current approach may not be applicable to fully interact with the element. In such cases, do not generate a new plan and inform the user that the test is complete.

Any new plans should:
  - Be specific to the element, the page soup, and the current approach.
  - Be minimal and not overly detailed, as it is just the initial plan.
  - Only provide additional steps, that the previous plan should be followed up with.
  - Generate **unique, realistic inputs** for each approach—avoid generic placeholders like "valid_username" or "invalid_password."
  - *Focus solely on the actions to perform, without making any assumptions about expected behaviors or outcomes.*
  - All test are analyzed, so any "verify" or "observe" steps are reduntant

Input Generation Guidance:
  - Only generate inputs if you are sure the target element exists on the page, do NOT make assumptions about potential input fields.
  - **Valid Inputs**: Use unique and properly formatted usernames (e.g., "user_test_random32ab") and strong passwords adhering to security best practices (e.g., "SecurePass$123").
  - **Likely-Taken Inputs**: Use common usernames (e.g., "admin", "user") or improperly formatted data that would trigger an error (e.g., no special characters for a password that requires them).
  - **Invalid Inputs**: Test with invalid or improperly formatted data that should lead to an error (e.g., "`~&$#@/password").
  - The type of input should be based on the given approach
"""

human_high_level_replanner_prompt = """
Your approach is:
{approach}

Your previous plan was:
{previous_plan}

You performed the following steps:
{steps}

Keep in mind that the specific output of the tools has been shortened for the sake of readability. For generating the final output for the user, this data will be provided in full.

You observed these outgoing requests:
{outgoing_requests}

The page source difference before and after interaction:
```
{page_source_diff}
```

Reminder: Generate a new plan if new inputs fields or elements have been discovered in the page source that require interaction to sufficiently test the feature.
If no further interaction is needed, inform the user that the test is complete.
"""


high_level_replanner_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system_high_level_replanner_prompt),
        ("human", human_high_level_replanner_prompt),
    ]
)

system_reporter_prompt = """
You are a professional web tester assigned to evaluate a specific feature on a web application page.

Your task is to create a detailed, aggregated report of the feature's performance, highlighting key behavior and any issues found during testing.
Additionally you must decide what information should be passed to future interaction tests. Include this information in the new_interaction_context field.

**Important**:
  - Summarize how the feature behaves across different tests and describe how the element functions and the server's response from the client side.
  - Pay attention to any outgoing requests, including their details, and document any differences or patterns observed.
  - Report unusual behaviors or errors found during testing.
  - Keep the report brief and focused on key findings and issues.
  - Only return important and *complete* context information that will be useful for future interactions.
  - For example, if a registration successfully completes, the context information should include the username and password used for the registration: "Valid user credentials: username: user_test_123, password: SecurePass$123"

The tested feature is: **{interaction}**

URI: **{uri}**

This report consolidates multiple tests that assess different aspects of the feature, combining their observations into one cohesive document.
"""

human_reporter_prompt = """
## Test Approach Overview
This test used the following approach: **{approach}**

### Test Plan
The test followed this plan:
{plan}

### Steps Performed:
Here are the steps that were taken during this test:
{steps}

### Outgoing Requests:
The following outgoing requests were observed during this interaction:
{outgoing_requests}

### Page Source Changes:
Comparing the page source before and after the interaction, the following differences were noted:
{page_source_diff}

"""
