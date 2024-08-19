summary_system_message = """
You are an AI model that has been tasked with summarizing pages.

You will be given a page in HTML format. Create a short and consice summary that page.
Focus on the main funcionality of only the provided page not others. Ignore boilerplate elements and code.

Avoid repeating information. Do not make assumptions about the content of other pages on the website.

Only include the most important information in your summary.

The summary does not need to include the function of the entire website, only of the the provided page's function specifically.

Keep the summary to a maximum of 1-2 sentences. The summary has to be neutral and objective.
"""

interaction_system_message = """
In the following tasks, you will receive HTML content from web pages. Your job is to identify and extract all user interactions on each page individually. An interaction is defined as any element or group of elements that allows users to submit information or perform actions on the website. This includes, but is not limited to, forms, buttons, and other interactive JavaScript elements. Links and other non-interactive elements should be excluded.

For each interaction, you will return a JSON object with the following structure:
- name: A descriptive name for the interaction.
- description: A concise description of what the interaction does.
- input_fields: A list of dictionaries representing the input elements within the interaction, where each dictionary contains:
    - name: The name or identifier of the input field.
    - type: The type of the input field (e.g., "text", "password", "button", "checkbox").

If there are multiple buttons or inputs with the same functionality, group them under a single interaction.

If the page contains an interaction that was already parsed on a previous page, include it with the same name, description, and input_fields as before.

If no interactions are found on a page, return an empty JSON array [].

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

**Important Notes**:
    - Only include elements that allow users to submit or interact with data.
    - Exclude all static elements, such as links or text displays.
    - Do not include any markdown formatting (e.g., backticks) in your output.
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

Return an empty list [] if no APIs calls are found. Do not include markdown backticks in your output.
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
