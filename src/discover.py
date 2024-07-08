import time

from selenium import webdriver
from bs4 import BeautifulSoup
from urllib.parse import urlparse

from src.llm import llm_create_summary, llm_parse_interactions

import config as cf


def discover_target():
    """
    Discover the given URL.
    """
    service = webdriver.FirefoxService(executable_path="/usr/bin/geckodriver")
    driver = webdriver.Firefox(service=service)

    paths = [cf.initial_path]
    paths_visited = []

    sites = []
    while paths:
        # DEBUG
        if len(sites) > 2:
            break
        # DEBUG
        path = paths.pop(0)
        paths_visited.append(path)

        site = discover_path(driver, path)
        for link in site["out_links"]:
            if link is None:
                continue
            parsed_link = urlparse(link)
            if parsed_link.path not in paths and parsed_link.path not in paths_visited:
                paths.append(parsed_link.path)

        sites.append(site)
        # sleep for a bit
        time.sleep(1)

    cf.logger.info(f"Done discovering website: {cf.website}")

    # for site in sites:
    #     print(f"Site: {site}")
    output_sites_to_file(sites)

    driver.quit()


def discover_path(driver, path):
    """
    Discover the given path. Create a site object.
    """
    cf.logger.debug(f"Discovering path: {path}")
    driver.get(f"{cf.target}{path}")
    soup = BeautifulSoup(driver.page_source, "html.parser")

    # TODO: Create the site object
    site = {
        "path": path,
        "summary": llm_create_summary(soup),
        "out_links": parse_links(soup),
        "interactions": llm_parse_interactions(soup),
    }
    return site


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
        for site in sites:
            output = f"""
Path: {site['path']}
Out Links: {site['out_links']}
Summary: {site['summary']}
Interactions: {site['interactions']}
----------------------------------------\n\n
"""
            file.write(output)
