summary_system_message = """
Create a short and consice summary of the given webpage.
Focus on the main funcionality of the page.
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

Return an empty list if no interactions are found. Do not include markdown backticks in your output.
Make sure to not make assumptions about the website's functionality. Only include interactions that are present on the page.
"""
