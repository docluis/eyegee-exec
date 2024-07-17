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
from src.utils import parse_page_requests


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
    page_requests = parse_page_requests(path, performance_logs)
    page = { # TODO: Create the page object
        "path": path,
        "summary": llm_create_summary(soup),
        "out_links": parse_links(soup),
        "interactions": llm_parse_interactions(soup),
        "apis_called": llm_parse_requests_for_apis(page_requests),
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
