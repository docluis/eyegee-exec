import time
from bs4 import BeautifulSoup

from config import Config
from src.llm import llm_create_summary, llm_parse_interactions, llm_parse_requests_for_apis
from src.siteinfo import SiteInfo
from src.page import Page
from src.utils import parse_page_requests, parse_links
from src.logging import logger


def discover(cf: Config) -> SiteInfo:
    """
    Discover the given URL.
    """
    logger.info("Starting discovery")
    si = SiteInfo(cf.target, cf.initial_path)

    while si.paths_todo:
        path = si.paths_todo.pop(0)
        logger.info(f"Discovering path: {path}")

        cf.driver.get(f"{cf.target}{path}")
        time.sleep(cf.selenium_rate)

        soup = BeautifulSoup(cf.driver.page_source, "html.parser")

        si.paths_visited.append(path)
        if si.check_if_visited(soup):
            continue

        p_logs = cf.driver.get_log("performance")
        p_reqs = parse_page_requests(cf.target, path, p_logs)

        # Create the page object
        page = Page(
            path=path,
            title=soup.title.string,
            soup=soup,
            summary=llm_create_summary(cf, soup),
            outlinks=parse_links(soup),
            interactions=llm_parse_interactions(cf, soup),
            apis_called=llm_parse_requests_for_apis(cf, p_reqs),
        )

        si.add_paths_to_todo(page.outlinks)
        si.pages.append(page)
        time.sleep(cf.selenium_rate)
    
    logger.info("Discovery complete")

    return si
