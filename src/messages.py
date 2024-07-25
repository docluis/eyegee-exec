summary_system_message = """
You are an AI model that has been tasked with summarizing pages.

You will be given a page in HTML format. Create a short and consice summary that page.
Focus on the main funcionality of only the provided page not others. Ignore boilerplate elements and code.

Avoid repeating information. Do not make assumptions about the content of other pages on the website.
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
"""


api_system_message = """
Your task is to parse out the interesting APIs calls from the given performance logs. Omit any calls that are not relevant to the website's functionality and boilerplate code.
Return the APIs in raw JSON format, where each API call has the following attributes:

url: The URL of the API call.
method: The HTTP method used in the API call, such as "GET" or "POST".
headers: A dictionary of headers sent with the API call.
postData: The data sent with the API call, if any.

Example Output:
[
    {
        "url": "https://api.example.com/data",
        "method": "GET",
        "headers": {
            "Content-Type": "application/json",
        },
        "postData": null
    },
]

Return an empty list [] if no APIs are found. Do not include markdown backticks in your output.
"""
