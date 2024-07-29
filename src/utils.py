import json
from typing import List

from bs4 import BeautifulSoup

from src.page import Page
from src.log import logger


def parse_page_requests(target: str, path: str, p_logs: List[dict]) -> str:
    """
    Parse the page requests from the given performance logs.
    """
    page_requests = []
    for log in p_logs:
        log = json.loads(log["message"])["message"]
        if log["method"] == "Network.requestWillBeSent":
            if (
                log["params"]["request"]["url"] == target + path
                and log["params"]["request"]["method"] == "GET"
            ):  # ignore requests to the same page
                continue
            page_request = {
                "url": log["params"]["request"]["url"],
                "method": log["params"]["request"]["method"],
                "headers": log["params"]["request"]["headers"],
                "postData": log["params"]["request"].get("postData"),
            }
            page_requests.append(page_request)
    # put the page_requests into a llm readable format
    page_requests = json.dumps(page_requests)
    return page_requests


def parse_links(soup: BeautifulSoup) -> List[str]:
    """
    Parse the links from the given soup.
    """
    links = []
    for link in soup.find_all("a"):
        links.append(link.get("href"))
    return links


# pages is list of Page objects
def output_to_file(pages: List[Page]) -> None:
    """
    Output the given pages to a file.
    """
    with open("output.txt", "w") as file:
        for page in pages:
            output = "--------------------------------\n"
            output += f"Path: {page.path}\n"
            output += f"Title: {page.title}\n"
            output += f"Summary: {page.summary}\n"
            output += f"Interactions: {page.interactions}\n"
            output += f"APIs Called: {page.apis_called}\n"
            output += f"Outlinks: {page.outlinks}\n\n"
            file.write(output)
    logger.info("Output written to output.txt")
