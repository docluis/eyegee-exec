import json
import time
from bs4 import BeautifulSoup

from config import Config
from src.discovery.interactionagent import InteractionAgent
from src.discovery.llm import (
    llm_parse_requests_for_apis,
    llm_rank_interactions,
)
from src.discovery.siteinfo import SiteInfo
from src.discovery.page import Page
from src.discovery.utils import (
    filter_html,
    parse_page_requests,
    parse_links,
)
from src.log import logger
from src.discovery.summarizer import LLM_Summarizer
from src.discovery.interactionparser import LLM_InteractionParser


def discover(cf: Config) -> SiteInfo:
    """
    Discover the given URL.
    """
    logger.info("Starting discovery")
    si = SiteInfo(cf.target, cf.initial_path)

    interaction_agent = InteractionAgent(cf)
    llm_summarizer = LLM_Summarizer(cf)
    llm_interactionparser = LLM_InteractionParser(cf)

    rerank_required = True

    while si.schuedule.paths_todo or si.schuedule.interactions_todo:
        si.schuedule.print_schedule()
        if si.schuedule.paths_todo:
            path = si.schuedule.next_path()
            logger.info(f"Discovering path: {path}")

            cf.driver.get(f"{cf.target}{path}")
            time.sleep(cf.selenium_rate)

            originial_soup = BeautifulSoup(cf.driver.page_source, "html.parser")
            soup = filter_html(originial_soup)

            if si.check_if_visited(soup):
                continue

            p_reqs = parse_page_requests(
                driver=cf.driver, target=cf.target, path=path, filtered=True
            )

            apis_called_passive = (
                si.add_apis(
                    llm_parse_requests_for_apis(cf, json.dumps(p_reqs, indent=4))
                )
                if len(p_reqs) > 0
                else []
            )

            interactions = llm_interactionparser.parse_interactions(soup)
            interaction_names = si.add_interactions(interactions)

            for interaction_name in interaction_names:
                logger.info(f"Found Interaction: {interaction_name}")

            # Create the page object
            page = Page(
                path=path,
                title=soup.title.string if soup.title else None,
                original_soup=originial_soup,
                summary=llm_summarizer.create_summary(soup),
                outlinks=parse_links(originial_soup),
                interaction_names=interaction_names,
                apis_called=apis_called_passive,
            )

            si.schuedule.add_paths_to_todo(page.outlinks)
            si.schuedule.add_interactions_to_todo(page.interaction_names)

            si.add_page(page)

            time.sleep(cf.selenium_rate)

        elif si.schuedule.interactions_todo:
            if rerank_required:
                ranked_interactions = llm_rank_interactions(
                    cf, si.schuedule.interactions_todo
                )
                logger.info(f"Re-Ranked Interactions: {ranked_interactions}")
                si.schuedule.interactions_todo = ranked_interactions
                rerank_required = False

            interaction_name = si.schuedule.next_interaction()
            interaction = si.get_interaction(interaction_name)
            logger.info(f"Discovering interaction: {interaction_name}")

            path = si.get_paths_with_interaction(interaction_name)
            behaviour, all_p_reqs = interaction_agent.interact(
                path=path[0], interaction=json.dumps(interaction.to_dict())
            )

            apis_called_interaction = (
                si.add_apis(
                    llm_parse_requests_for_apis(cf, json.dumps(all_p_reqs, indent=4))
                )
                if len(all_p_reqs) > 0
                else []
            )

            interaction.behaviour = behaviour
            interaction.apis_called = apis_called_interaction
            interaction.tested = True

            # TODO: parse out new interactions/pages here, set rerank_required to True

            time.sleep(cf.selenium_rate)

    logger.info("Discovery complete")

    return si
