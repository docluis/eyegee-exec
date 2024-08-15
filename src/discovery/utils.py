import json
from typing import List

from bs4 import BeautifulSoup

from src.discovery.siteinfo import SiteInfo
from src.discovery.page import Page
from src.log import logger


def parse_page_requests(target: str, path: str, p_logs: List[dict]) -> List[dict]:
    """
    Parse the page requests from the given performance logs.
    """
    page_requests = []
    for log in p_logs:
        log = json.loads(log["message"])["message"]
        if log["method"] == "Network.requestWillBeSent":
            # TODO: check if this is necessary, otherwise remove also params
            # if (
            #     log["params"]["request"]["url"] == target + path
            #     and log["params"]["request"]["method"] == "GET"
            # ):  # ignore requests to the same page
            #     continue
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


def get_performance_logs(driver) -> List[dict]:
    """
    Get the performance logs from the given driver since the last navigation.
    """
    logs = driver.get_log("performance")
    ts = driver.execute_script("return window.performance.timing.navigationStart")
    logs = [log for log in logs if log["timestamp"] > ts]
    return logs

def filter_html(soup: BeautifulSoup) -> BeautifulSoup:
    """
    Experimental: TODO: Make sure no important content is removed.

    Filter the given soup. Remove unnecessary tags and attributes (for LLM).
    
    Returns the filtered soup.
    """
    soup_cpy = soup
    remove_tags = ["script", "style", "meta", "link", "noscript"]
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

    for tag in soup_cpy.find_all(True):
        for attribute in list(tag.attrs):
            if not any(attribute.startswith(prefix) for prefix in keep_attributes):
                del tag.attrs[attribute]
            # Remove unnecessary classes, TODO: this seems to be too aggressive
            # elif attribute == "class":
            #     important_classes = [
            #         cls
            #         for cls in tag.attrs["class"]
            #         if any(cls.startswith(prefix) for prefix in keep_classes)
            #     ]
            #     tag.attrs["class"] = important_classes if important_classes else None

    return soup_cpy

# pages is list of Page objects
def output_to_file(si: SiteInfo) -> None:
    """
    Output the given pages to a file.
    """
    with open("output.txt", "w") as file:
        for page in si.pages:
            output = "---------- PAGES ----------\n"
            output += "--------------------------------\n"
            output += f"Path: {page.path}\n"
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
            output += f"Behaviour: {interaction.behaviour}\n"
            output += f"APIs Called: {interaction.apis_called}\n"
            file.write(output)
    logger.info("Output written to output.txt")
