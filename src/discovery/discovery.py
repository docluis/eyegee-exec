import json
import time
from bs4 import BeautifulSoup

from config import Config
from src.discovery.interactionparser import LLM_InteractionParser
from src.discovery.interactionagent import InteractionAgent
from src.discovery.llm import (
    llm_parse_requests_for_apis,
    llm_rank_interactions,
)
from src.discovery.siteinfo import SiteInfo
from src.discovery.page import Page
from src.discovery.utils import (
    filter_html,
    get_performance_logs,
    parse_page_requests,
    parse_links,
)
from src.log import logger
from src.discovery.summarizer import LLM_Summarizer


def discover(cf: Config) -> SiteInfo:
    """
    Discover the given URL.
    """
    logger.info("Starting discovery")
    si = SiteInfo(cf.target, cf.initial_path)

    interaction_agent = InteractionAgent(cf)
    llm_summarizer = LLM_Summarizer(cf)
    llm_interactionparser = LLM_InteractionParser(cf)

    while si.paths_todo:
        # DEBUG
        # if len(si.paths_visited) > 3:
        #     break

        path = si.paths_todo.pop(0)
        logger.info(f"Discovering path: {path}")

        cf.driver.get(f"{cf.target}{path}")
        time.sleep(cf.selenium_rate)

        originial_soup = BeautifulSoup(cf.driver.page_source, "html.parser")
        soup = filter_html(originial_soup)

        si.paths_visited.append(path)
        if si.check_if_visited(soup):
            continue

        p_logs = get_performance_logs(cf.driver)
        p_reqs = parse_page_requests(
            target=cf.target, path=path, p_logs=p_logs, filtered=True
        )

        if len(p_reqs) > 0:
            apis = llm_parse_requests_for_apis(cf, json.dumps(p_reqs, indent=4))
            apis_called_passive = si.add_apis(apis)
        else:
            apis_called_passive = si.add_apis([])

        interactions = llm_interactionparser.parse_interactions(soup)
        interaction_names = si.add_interactions(interactions)

        for interaction_name in interaction_names:
            logger.info(f"Found Interaction: {interaction_name}")

        # Create the page object
        page = Page(
            path=path,
            title=soup.title.string,
            original_soup=soup,
            summary=llm_summarizer.create_summary(soup),
            outlinks=parse_links(soup),
            interaction_names=interaction_names,
            apis_called=apis_called_passive,
        )

        si.add_paths_to_todo(page.outlinks)
        si.add_page(page)
        time.sleep(cf.selenium_rate)

    logger.info("Testing Interactions")
    logger.info(f"Ranking Interactions, Selecting Top {cf.interaction_test_limit}...")
    ranked_interactions = llm_rank_interactions(cf, si.interactions)
    ranked_interactions = ranked_interactions[: cf.interaction_test_limit]
    logger.info(f"Ranked Interactions: {ranked_interactions}")

    for i in ranked_interactions:
        for interaction in si.interactions:
            if interaction.name == i:
                logger.info(f"Testing Interaction: {interaction.name}")
                path = si.get_paths_with_interaction(interaction.name)
                behaviour, all_p_reqs = interaction_agent.interact(
                    path=path[0], interaction=json.dumps(interaction.to_dict())
                )
                if len(all_p_reqs) > 0:
                    apis = llm_parse_requests_for_apis(
                        cf, json.dumps(all_p_reqs, indent=4)
                    )
                    apis_called_interaction = si.add_apis(apis)
                else:
                    apis_called_interaction = si.add_apis([])
                interaction.behaviour = behaviour
                interaction.apis_called = apis_called_interaction
                interaction.tested = True
                break

    logger.info("Discovery complete")

    return si
