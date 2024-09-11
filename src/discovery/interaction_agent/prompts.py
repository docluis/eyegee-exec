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

Keep in mind that the page is already loaded and you have access to the page soup.

This plan should be specific to the element, the page soup and the current approach, however this is just the initial plan, thus it should not be too detailed.

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
plan: ["Enter a username with special characters.", "Enter a password with special characters.", "Click the login button."]

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


