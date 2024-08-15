summary_system_message = """
You are an AI model that has been tasked with summarizing pages.

You will be given a page in HTML format. Create a short and consice summary that page.
Focus on the main funcionality of only the provided page not others. Ignore boilerplate elements and code.

Avoid repeating information. Do not make assumptions about the content of other pages on the website.

Only include the most important information in your summary.

The summary does not need to include the function of the entire website, only of the the provided page's function specifically.

Keep the summary to a maximum of 2-4 sentences.
"""

interaction_system_message = """
Your task is to parse the interactions on the provided webpage. Interactions are any ways a user can submit information to the website, including but not limited to buttons, forms, and other JavaScript interactive elements. Do not include links or other static elements.
Return the interactions in raw JSON format, where each interaction has the following attributes:

name: A descriptive name for the interaction.
description: A brief description of the interaction's function.
input_fields: A list of dictionaries, where each dictionary has the following attributes:
    name: The name of the input field.
    type: The type of the input field, such as "text", "password", or "button".

Example Output:
[
    {
        "name": "Login Form",
        "description": "A form that allows users to log into the website.",
        "input_fields": [
            {"name": "username", "type": "text"},
            {"name": "password", "type": "password"},
            {"name": "submit", "type": "button"}
        ]
    },
    {
        "name": "Search Bar",
        "description": "A bar where users can enter search queries.",
        "input_fields": [
            {"name": "search_query", "type": "text"},
            {"name": "search_button", "type": "button"}
        ]
    }
]

Return an empty list [] if no interactions are found. Do not include markdown backticks in your output.

If the same interaction appears multiple times, include it multiple times with the same attributes.
Do not include links or other static elements in your output (only interactive elements that may submit data to the server).
"""


api_system_message = """
Your task is to parse out the interesting APIs calls from the given performance logs. Omit any calls that are not relevant to the website's functionality and boilerplate code.
Return the APIs in raw JSON format, where each API call has the following attributes:

url: The URL of the API call.
domain: The domain of the API call.
path: The path of the API call.
query_string: The query string of the API call.
method: The HTTP method used in the API call, such as "GET" or "POST".
headers: A dictionary of headers sent with the API call.
postData: The data sent with the API call, if any.

Example Output:
[
    {
        "url": "https://api.example.com/data?query=example",
        "domain": "api.example.com",
        "path": "/data",
        "query_string": "query=example",
        "method": "GET",
        "headers": {
            "Content-Type": "application/json",
        },
        "postData": null
    },
]

Return an empty list [] if no APIs are found. Do not include markdown backticks in your output.

Also: do not include the GET calls to the website itself in your output. Only include calls to APIs.
"""


interaction_ranking_system_message = """
Your are an AI model that has been tasked with ranking interactions based on their importance to the website's functionality.

Interactions with a bigger impact on the website's functionality and security should be ranked higher. For example, a "Login" interaction is more important than a "Contact Us" interaction.

If there are multiple interactions with the same functionality, include one of them with higher importance than the others.

The aim is to create a testing order for the interactions, where the most important interactions are tested first.

Return the interactions in a List format, where the first element is the most important interaction and the last element is the least important interaction.

Example Output:
[
    "Login Form",
    "Search Bar",
    "Product Button A",
    "Contact Us Form",
    "Product Button B",
]

Return an empty list [] if no interactions are found. Do not include markdown backticks in your output.
"""
