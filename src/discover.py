import json
import time

from bs4 import BeautifulSoup
from urllib.parse import urlparse

from src.llm import (
    llm_create_summary,
    llm_parse_interactions,
    llm_parse_requests_for_apis,
)

import config as cf


def discover_target():
    """
    Discover the given URL.
    """

    paths_to_visit = [cf.initial_path]
    paths_visited = []

    sites = []
    sites_hashes = []
    while paths_to_visit:
        # # DEBUG START
        # if len(sites) > 2:
        #     break
        # # DEBUG END
        path = paths_to_visit.pop(0)
        cf.logger.debug(f"Discovering path: {path}")

        cf.driver.get(f"{cf.target}{path}")
        time.sleep(cf.selenium_rate)
        performance_logs = cf.driver.get_log(
            "performance"
        )  # Get logs, contain network requests

        soup = BeautifulSoup(cf.driver.page_source, "html.parser")
        paths_visited.append(path)
        site_hash = hash(soup)
        if site_hash in sites_hashes:  # Already visited this page
            cf.logger.debug(f"Already visited path: {path}")
            continue
        sites_hashes.append(site_hash)
        page = analyze_page(path, soup, performance_logs)
        for link in page["out_links"]:
            if link is None:
                continue
            parsed_link = urlparse(link)
            if (
                parsed_link.path not in paths_to_visit
                and parsed_link.path not in paths_visited
            ):
                paths_to_visit.append(parsed_link.path)

        sites.append(page)
        time.sleep(cf.selenium_rate)

    cf.logger.info(f"Done discovering website: {cf.website}")

    output_sites_to_file(sites)

    cf.driver.quit()


def analyze_page(path, soup, performance_logs):
    """
    Discover the given path. Create a page object.
    """
    # TODO: Move this to analyze the pages after discovering?/ alternatively summarize again after this
    page = { # TODO: Create the page object
        "path": path,
        "summary": llm_create_summary(soup),
        "out_links": parse_links(soup),
        "interactions": llm_parse_interactions(soup),
        "apis_called": parse_apis(path, performance_logs),
    }
    return page


def parse_links(soup):
    """
    Parse the links from the given soup.
    """
    links = []
    for link in soup.find_all("a"):
        links.append(link.get("href"))
    return links


def parse_apis(path, performance_logs):
    """
    Parse the APIs called from the given performance_logs.
    """
    page_requests = []
    for log in performance_logs:
        log = json.loads(log["message"])["message"]
        if log["method"] == "Network.requestWillBeSent":
            print("compare")
            print(log["params"]["request"]["url"])
            print(cf.target + path)
            if (
                log["params"]["request"]["url"] == cf.target + path
                and log["params"]["request"]["method"] == "GET"
            ):  # ignore requests to the same page
                continue
            page_request = {
                "url": log["params"]["request"]["url"],
                "method": log["params"]["request"]["method"],
                "headers": log["params"]["request"]["headers"],
                "postData": log["params"]["request"].get("postData"),
            }
            print(page_request)
            page_requests.append(page_request)
    # put the page_requests into a llm readable format
    page_requests = json.dumps(page_requests)

    apis = llm_parse_requests_for_apis(page_requests)
    return apis


def output_sites_to_file(sites):
    """
    Output the given sites to a file.
    """
    with open("output.txt", "w") as file:
        for page in sites:
            output = f"""
Path: {page['path']}
Out Links: {page['out_links']}
Summary: {page['summary']}
Interactions: {page['interactions']}
APIs Called: {page['apis_called']}
----------------------------------------\n\n
"""
            file.write(output)
