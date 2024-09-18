import json
import time

from bs4 import BeautifulSoup

from config import Config
from src.discovery.schedule import Schedule

# from src.discovery.interactionagent import InteractionAgent
from src.discovery.interaction_agent.agent import InteractionAgent
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
    si = SiteInfo(cf.target)
    schuedule = Schedule(cf.target, cf.initial_path)

    interaction_agent = InteractionAgent(cf)
    llm_summarizer = LLM_Summarizer(cf)
    llm_interactionparser = LLM_InteractionParser(cf)

    rerank_required = True

    while schuedule.uris_todo or schuedule.interactions_todo:
        schuedule.print_schedule()
        if schuedule.uris_todo:
            uri = schuedule.next_uri()
            logger.info(f"Discovering URI: {uri}")

            cf.driver.get(f"{cf.target}{uri}")
            time.sleep(cf.selenium_rate)

            originial_soup = BeautifulSoup(cf.driver.page_source, "html.parser")
            soup = filter_html(originial_soup)

            if si.check_if_visited(soup):
                continue

            p_reqs = parse_page_requests(driver=cf.driver, target=cf.target, uri=uri, filtered=True)

            apis_called_passive = (
                si.add_apis(llm_parse_requests_for_apis(cf, json.dumps(p_reqs, indent=4))) if len(p_reqs) > 0 else []
            )

            interactions = llm_interactionparser.parse_interactions(soup)
            interaction_names = si.add_interactions(interactions)

            for interaction_name in interaction_names:
                logger.info(f"Found Interaction: {interaction_name}")

            # Create the page object
            # path, query_string = uri.split("?") if "?" in uri else (uri, None)
            page = Page(
                uri=uri,
                title=soup.title.string if soup.title else None,
                original_soup=originial_soup,
                summary=llm_summarizer.create_summary(soup),
                outlinks=parse_links(originial_soup),
                interaction_names=interaction_names,
                apis_called=apis_called_passive,
            )

            schuedule.add_uris_to_todo(page.outlinks)
            schuedule.add_interactions_to_todo(page.interaction_names)

            si.add_page(page)

            time.sleep(cf.selenium_rate)

        elif schuedule.interactions_todo:
            if rerank_required:
                ranked_interactions = llm_rank_interactions(cf, schuedule.interactions_todo)
                logger.info(f"Re-Ranked Interactions: {ranked_interactions}")
                schuedule.interactions_todo = ranked_interactions
                rerank_required = False

            interaction_name = schuedule.next_interaction()
            interaction = si.get_interaction(interaction_name)
            logger.info(f"Discovering interaction: {interaction_name}")

            uri = si.get_uris_with_interaction(interaction_name)[0]
            # behaviour, all_p_reqs, all_paths, new_soup = interaction_agent.interact(
            #     uri=uri, interaction=json.dumps(interaction.to_dict())
            # )
            test_report, all_p_reqs, all_paths = interaction_agent.interact(
                uri=uri, interaction=json.dumps(interaction.to_dict()), limit="3"  # TODO: adjust limit
            )

            apis_called_interaction = (
                si.add_apis(llm_parse_requests_for_apis(cf, json.dumps(all_p_reqs, indent=4)))
                if len(all_p_reqs) > 0
                else []
            )

            interaction.test_report = test_report
            interaction.apis_called = apis_called_interaction
            interaction.tested = True

            logger.info(f"All paths: {all_paths}")
            schuedule.add_uris_to_todo(all_paths)  # Add the new paths to the schedule

            # TODO: handle this inside the agent (discover new interactions in same page with new soup)
            # if new_soup:  # Parse interactions if the page has changed
            #     interactions = llm_interactionparser.parse_interactions(soup)
            #     interaction_names = si.add_interactions(interactions)

            #     for interaction_name in interaction_names:
            #         logger.info(f"Found Interaction: {interaction_name}")

            time.sleep(cf.selenium_rate)

    logger.info("Discovery complete")

    return si
