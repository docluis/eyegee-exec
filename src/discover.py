from selenium import webdriver
from bs4 import BeautifulSoup
from urllib.parse import urlparse

import config


def discover_target():
    """
    Discover the given URL.
    """
    service = webdriver.FirefoxService(executable_path="/usr/bin/geckodriver")
    driver = webdriver.Firefox(service=service)

    paths = [config.initial_path]
    paths_visited = []

    sites = []
    while paths:
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

    config.logger.info(f"Done discovering website: {config.website}")
    
    for site in sites:
        print(f"Site: {site}")

    driver.quit()


def discover_path(driver, path):
    """
    Discover the given path.
    """
    config.logger.debug(f"Discovering path: {path}")
    driver.get(f"{config.target}/{path}")
    soup = BeautifulSoup(driver.page_source, "html.parser")

    site = {"path": path, "out_links": parse_links(soup), "interactions": []}
    return site


def parse_links(soup):
    """
    Parse the links from the given soup.
    """
    links = []
    for link in soup.find_all("a"):
        links.append(link.get("href"))
    return links
