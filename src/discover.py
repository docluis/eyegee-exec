import subprocess
import time

from selenium import webdriver
from bs4 import BeautifulSoup
from urllib.parse import urlparse

from src.llm import llm_create_summary, llm_parse_apis, llm_parse_interactions

import config as cf


def discover_target():
    """
    Discover the given URL.
    """
    options = webdriver.FirefoxOptions()
    service = webdriver.FirefoxService(executable_path="/usr/bin/geckodriver")
    driver = webdriver.Firefox(service=service, options=options)

    paths_to_visit = [cf.initial_path]
    paths_visited = []

    sites = []
    sites_hashes = []
    while paths_to_visit:
        # DEBUG
        if len(sites) > 2:
            break
        # DEBUG
        path = paths_to_visit.pop(0)
        cf.logger.debug(f"Discovering path: {path}")

        driver.get(f"{cf.target}{path}")
        # print(driver.get_log("browser"))
        logs = []

        soup = BeautifulSoup(driver.page_source, "html.parser")
        paths_visited.append(path)
        site_hash = hash(soup)
        if site_hash in sites_hashes:  # Already visited this page
            cf.logger.debug(f"Already visited path: {path}")
            continue
        sites_hashes.append(site_hash)
        page = analyze_page(path, soup, logs)
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
        # sleep for a bit
        time.sleep(1)

    cf.logger.info(f"Done discovering website: {cf.website}")

    output_sites_to_file(sites)

    driver.quit()


def analyze_page(path, soup, logs):
    """
    Discover the given path. Create a page object.
    """

    # TODO: Create the page object
    page = {
        "path": path,
        "summary": llm_create_summary(soup),
        "out_links": parse_links(soup),
        "interactions": llm_parse_interactions(soup),
        "apis_called": llm_parse_apis(logs),
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
----------------------------------------\n\n
"""
            file.write(output)
