import json
import copy
from typing import List
from urllib.parse import urlparse

from bs4 import BeautifulSoup

from src.discovery.llm.model_classes import ApiModel
from src.discovery.interaction_agent.classes import CompletedTask
from src.discovery.classes.siteinfo import SiteInfo
from src.discovery.classes.page import Page
from src.log import logger

remove_file_extensions = [
    ".js",  # TODO: could remove API requests in Edge Cases
    ".css",
    ".png",
    ".jpg",
    ".jpeg",
    ".svg",
    ".gif",
    ".ico",
    ".woff",
    ".woff2",
]

def parse_apis(driver, target: str, uri: str, filtered: bool = True) -> List[dict]:
    """
    Parse the page requests from the driver's performance logs.
    """
    logs = driver.get_log("performance")
    ts = driver.execute_script("return window.performance.timing.navigationStart")
    p_logs = [log for log in logs if log["timestamp"] > ts]

    page_requests = []
    for log in p_logs:
        log = json.loads(log["message"])["message"]
        if log["method"] == "Network.requestWillBeSent":
            if filtered: # Filter out unnecessary requests
                if (
                    log["params"]["request"]["url"] == target + uri
                    and log["params"]["request"]["method"] == "GET"
                ):
                    continue # ignore initial page request
                if any(
                    [
                        log["params"]["request"]["url"].endswith(ext)
                        for ext in remove_file_extensions
                    ]
                ):
                    continue # ignore requests with file extensions
            page_request = {
                "url": log["params"]["request"]["url"],
                "method": log["params"]["request"]["method"],
                "headers": log["params"]["request"]["headers"],
                "postData": log["params"]["request"].get("postData"),
            }
            page_requests.append(page_request)
    return page_requests


def parse_links(soup: BeautifulSoup) -> List[str]:
    """
    Parse the links from the given soup.
    """
    links = []
    for link in soup.find_all("a"):
        links.append(link.get("href"))
    return links

def filter_html(soup: BeautifulSoup) -> BeautifulSoup:
    """
    Experimental: TODO: Make sure no important content is removed.

    Filter the given soup. Remove unnecessary tags and attributes (for LLM).
    
    Returns the filtered soup.
    """
    # Copy the soup to avoid modifying the original
    soup_cpy = copy.deepcopy(soup)
    remove_tags = ["script", "style", "meta", "link", "noscript", "a"]
    keep_attributes = [
            "id",
            "class",
            "aria-",
            "role",
            "href",
            "placeholder",
            "name",
            "type",
            "src",
            "alt",
        ]
    keep_classes = ["btn", "nav", "search", "form", "input"]
    
    for tag in soup_cpy(remove_tags):
        tag.extract()

    # TODO: this seems to be too aggressive, reduce tokens in different ways
    for tag in soup_cpy.find_all(True):
        for attribute in list(tag.attrs):
            if not any(attribute.startswith(prefix) for prefix in keep_attributes):
                del tag.attrs[attribute]
    #         # Remove unnecessary classes, 
    #         elif attribute == "class":
    #             important_classes = [
    #                 cls
    #                 for cls in tag.attrs["class"]
    #                 if any(cls.startswith(prefix) for prefix in keep_classes)
    #             ]
    #             tag.attrs["class"] = important_classes if important_classes else None

    return soup_cpy

def format_steps(steps: List[CompletedTask]) -> str:
    """
    Format the given steps.
    """
    output = ""
    for step in steps:
        output += f"- Step: {step.task}\n"
        output += f"\t- Status: {step.status}\n"
        output += f"\t- Result: {step.result}\n"
        output += f"\t- Tool history: {len(step.tool_history)}\n"
        for tool_call in step.tool_history:
            output += f"\t\t- Tool call: {tool_call[0]}\n"
            output += f"\t\t- Input: {tool_call[1]}\n"
            output += f"\t\t- Output\n"
            output += f"\t\t\t- Success: {tool_call[2].success}\n"
            output += f"\t\t\t- Message: {tool_call[2].message}\n"
            # output += f"\t\t\tError: {tool_call[2].error if tool_call[2].error else 'No error'}\n"
            # dont print page source, outgoing requests
    return output

def extract_uri(url:str) -> str:
    """
    Extract the URI from the given URL.
    """
    parsed = urlparse(url)
    path_now = parsed.path
    query_string = parsed.query
    if query_string:
        path_now = f"{path_now}?{query_string}"
    return path_now

def api_models_to_str(apis: List[ApiModel]) -> str:
    """
    Convert the given API models to a string.
    """
    # url: str = Field(description="The URL of the API call")
    # domain: str = Field(description="The domain of the API call")
    # path: str = Field(description="The path of the API call")
    # query_string: Optional[str] = Field(description="The query string of the API call")
    # url_path_params: Optional[Dict[str, str]] = Field(description="The URL path parameters of the API call")
    # method: str = Field(description="The HTTP method used in the API call, such as 'GET' or 'POST'")
    # headers: Dict[str, str] = Field(description="The headers sent with the API call")
    # postData: Optional[Dict[str, str]] = Field(description="The data sent with the API call, key-value pairs")
    if not apis:
        return "No APIs calls identified."
    output = ""
    for api in apis:
        output += f"API: {api.method} {api.url}\n"
        output += f"Domain: {api.domain}\n"
        output += f"Path: {api.path}\n"
        if api.query_string :
            output += f"Query String: {api.query_string}\n"
        if api.url_path_params :
            output += f"URL Path Params: {api.url_path_params}\n"
        output += f"Headers: {api.headers}\n"
        if api.postData :
            output += f"Post Data: {api.postData}\n"
        output += "\n"
    return output

# pages is list of Page objects
def output_to_file(si: SiteInfo) -> None:
    """
    Output the given pages to a file.
    """
    try:

        with open("output.txt", "w") as file:
            for page in si.pages:
                output = "---------- PAGES ----------\n"
                output += "--------------------------------\n"
                output += f"URI: {page.uri}\n"
                output += f"Title: {page.title}\n"
                output += f"Summary: {page.summary}\n"
                output += f"Interactions: {page.interaction_names}\n"
                output += f"APIs Called: {page.apis_called}\n"
                output += f"Outlinks: {page.outlinks}\n\n"
                file.write(output)
            output = "---------- APIS ----------\n"
            for api in si.apis:
                output = "--------------------------------\n"
                output += f"Method: {api.method}\n"
                output += f"Route: {api.route}\n"
                for param in api.params:
                    output += f"Param: {param.name}\n"
                    output += f"Observed Values: {param.observed_values}\n"
                    output += f"Param Type: {param.param_type}\n"
                file.write(output)
            output = "---------- INTERACTIONS ----------\n"
            for interaction in si.interactions:
                output += "--------------------------------\n"
                output += f"Name: {interaction.name}\n"
                output += f"Description: {interaction.description}\n"
                for input_field in interaction.input_fields:
                    output += f"Input Field Name: {input_field["name"]}\n"
                    output += f"Input Field Type: {input_field["type"]}\n"
                output += f"Tested: {"True" if interaction.tested else "False"}\n"
                output += f"Test Report: {interaction.test_report}\n"
                output += f"APIs Called: {interaction.apis_called}\n"
                file.write(output)
        logger.debug("Output written to output.txt")
    except Exception as e:
        logger.error(f"Error writing output to file: {e}")
