import json
import time
from bs4 import BeautifulSoup

from config import Config
from src.discovery.interactionagent import InteractionAgent
from src.discovery.llm import (
    llm_parse_interactions,
    llm_parse_requests_for_apis,
)
from src.discovery.siteinfo import SiteInfo
from src.discovery.page import Page
from src.discovery.utils import get_performance_logs, parse_page_requests, parse_links
from src.log import logger
from src.discovery.summarizer import LLM_Summarizer
from src.discovery.api import Api


def discover(cf: Config) -> SiteInfo:
    """
    Discover the given URL.
    """
    logger.info("Starting discovery")
    si = SiteInfo(cf.target, cf.initial_path)

    interaction_agent = InteractionAgent(cf)
    llm_summarizer = LLM_Summarizer(cf)

    while si.paths_todo:
        # DEBUG
        # if len(si.paths_visited) > 3:
        #     break

        path = si.paths_todo.pop(0)
        logger.info(f"Discovering path: {path}")

        cf.driver.get(f"{cf.target}{path}")
        time.sleep(cf.selenium_rate)

        soup = BeautifulSoup(cf.driver.page_source, "html.parser")

        si.paths_visited.append(path)
        if si.check_if_visited(soup):
            continue

        p_logs = get_performance_logs(cf.driver)
        p_reqs = parse_page_requests(cf.target, path, p_logs)

        apis = llm_parse_requests_for_apis(cf, json.dumps(p_reqs, indent=4))
        apis_called_passive = si.add_apis(apis)

        # Create the page object
        page = Page(
            path=path,
            title=soup.title.string,
            soup=soup,
            summary=llm_summarizer.create_summary(soup),
            outlinks=parse_links(soup),
            interactions=llm_parse_interactions(cf, soup),
            apis_called=apis_called_passive,
        )

        for interaction in page.interactions:
            logger.info(f"Testing Interaction: {interaction.get('name')}")
            behaviour, all_p_reqs = interaction_agent.interact(
                path=path, interaction=interaction
            )
            apis = llm_parse_requests_for_apis(cf, json.dumps(all_p_reqs, indent=4))
            apis_called_interaction = si.add_apis(apis)
            interaction["behaviour"] = behaviour
            interaction["apis_called"] = apis_called_interaction

        si.add_paths_to_todo(page.outlinks)
        si.add_page(page)
        time.sleep(cf.selenium_rate)

    logger.info("Discovery complete")

    return si
