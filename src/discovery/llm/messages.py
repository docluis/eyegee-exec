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

If no interactions are found on a page, return an empty array [].

Example Output:
[
    InteractionModel(
        name="Login Form",
        description="A form that allows users to log into the website.",
        input_fields=[
            {"name": "username", "type": "text"},
            {"name": "password", "type": "password"},
            {"name": "submit", "type": "button"}
        ]
    ),
    InteractionModel(
        name="Search Bar",
        description="A bar where users can enter search queries.",
        input_fields=[
            {"name": "search_query", "type": "text"},
            {"name": "search_button", "type": "button"}
        ]
    )
]

**Important Notes**:
    - Only include elements that allow users to submit or interact with data.
    - Do not include any Button or Links that just redirect to another page.
    - Do not include any markdown formatting (e.g., backticks) in your output.
"""


api_system_message = """
Your task is to parse out the interesting APIs calls from the given performance logs.

Omit any calls that are not relevant to the website's functionality and boilerplate code, inluing calls such as tracking scripts, analytics, or other third-party services, manifest files, or calls that are not API calls.

Return the APIs in a List of ApiModel, where each API call has the following attributes:

url: The URL of the API call.
domain: The domain of the API call.
path: The path of the API call.
query_string: The query string of the API call.
url_path_params: The URL path parameters of the API call.
method: The HTTP method used in the API call, such as "GET" or "POST".
headers: A dictionary of headers sent with the API call.
postData: The data sent with the API call, if any.

## Examples:

# Example 1:
Input:
A simple GET request to a URL with a query string: https://api.example.com/data?query=example

Output:
[   
    ApiModel(
        url="https://api.example.com/data?query=example",
        domain: "api.example.com",
        path: "/data",
        query_string: "query=example",
        url_path_params: {},
        method: "GET",
        headers: {
            "Content-Type": "application/json",
        },
        postData: null
    },
]

# Example 2:
Input:
GET requests to a URL with URL path parameters: https://api.example.com/data/123, https://api.example.com/data/456

Output:
[
    ApiModel(
        url="https://api.example.com/data/123",
        domain: "api.example.com",
        path: "/data/<id>", # The path is the same for both requests
        query_string: "",
        url_path_params: {"id": "123"},
        method: "GET",
        headers: {
            "Content-Type": "application/json",
        },
        postData: null
    ),
    ApiModel(
        url="https://api.example.com/data/456",
        domain: "api.example.com",
        path: "/data/<id>",
        query_string: "",
        url_path_params: {"id": "456"},
        method: "GET",
        headers: {
            "Content-Type": "application/json",
        },
        postData: null
    ),
]

# Example 3:
Input:
POST request to a URL with a JSON body: https://api.example.com/data

Output:
[
    ApiModel(
        url="https://api.example.com/data",
        domain: "api.example.com",
        path: "/data",
        query_string: "",
        url_path_params: {},
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        postData: {"city": "London"}
    ),
]

Return an empty list [] if no APIs calls are found.

Make sure to stay consistent with the the naming of URL path parameters.
"""


interaction_ranking_system_message = """
You are an AI model that has been tasked with ranking interactions based on their importance to the website's functionality.

Interactions with a bigger impact on the website's functionality and security should be ranked higher. For example, a "Register" interaction is more important than a "Contact Us" interaction.

If there are multiple interactions with the same functionality, include one of them with higher importance than the others.

The aim is to create a testing order for the interactions, where the most important interactions are tested first.

Return the interactions in a List format, where the first element is the most important interaction and the last element is the least important interaction.

Also assign a number to each interaction, which represents the number of approaches to be genereated for the interaction.

If the interaction is very likely to be handled by JavaScript only on the client side, assign a number of 0.
For interactions that likely reveal some information about the website's functionality or may lead to additional pages (such as buttons that likely redirect to another page), assign a number of 1.
For interactions you are unsure about, assign a number of approaches as 1.
For important interactions, that likely submit data to the server, assign a number of approaches as 2 or 3.
"""
