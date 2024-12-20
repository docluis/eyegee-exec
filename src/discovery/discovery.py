import json
import time

from bs4 import BeautifulSoup

from config import Config
from src.pretty_log import DiscoveryLog, RankerLog
from src.discovery.classes.schedule import Schedule

from src.discovery.interaction_agent.agent import InteractionAgent
from src.discovery.llm.ranker import llm_rank_interactions
from src.discovery.classes.siteinfo import SiteInfo
from src.discovery.classes.page import Page
from src.discovery.utils import (
    filter_html,
    parse_apis,
    parse_links,
)
from src.log import logger
from src.discovery.llm.summarizer import LLM_Summarizer
from src.discovery.llm.interaction_parser import LLM_InteractionParser
from src.discovery.llm.api_parser import LLM_ApiParser
from rich import print
from rich.text import Text
from rich.live import Live


def discover(cf: Config) -> SiteInfo:
    """
    Discover the given URL.
    """
    print(Text("Starting discovery", style="bold green"))
    logger.debug("Starting discovery")
    si = SiteInfo(cf.target)
    schedule = Schedule(cf.target, cf.initial_path)

    llm_summarizer = LLM_Summarizer(cf)
    llm_interactionparser = LLM_InteractionParser(cf)
    llm_page_request_parser = LLM_ApiParser(cf)

    interaction_agent = InteractionAgent(cf, llm_page_request_parser)

    rerank_required = True
    interaction_context = []

    while schedule.uris_todo or schedule.interactions_todo:
        schedule.debug_print_schedule()
        if schedule.uris_todo:
            uri = schedule.next_uri()
            logger.debug(f"Discovering URI: {uri}")
            print(Text(f"\nDiscovering URI: {uri}", style="bold green"))
            discovery_log = DiscoveryLog()
            with Live(refresh_per_second=10) as live:
                # Load the page
                discovery_log.update_status("Loading Page", "running")
                live.update(discovery_log.render())
                try:
                    cf.driver.get(f"{cf.target}{uri}")
                except Exception as e:
                    logger.error(f"Error loading page: {e}")
                    discovery_log.update_status("Loading Page", "skipped")
                    live.update(discovery_log.render())
                    print(Text(f"Error loading page: {uri}", style="bold red"))
                    continue
                time.sleep(cf.selenium_rate)

                original_soup = BeautifulSoup(cf.driver.page_source, "html.parser")
                soup = filter_html(original_soup)
                discovery_log.update_status("Loading Page", "done")
                if si.check_if_visited(soup):
                    discovery_log.update_status("Discovering APIs", "skipped")
                    discovery_log.update_status("Discovering Interactions", "skipped")
                    discovery_log.update_status("Summarizing Page", "skipped")
                    live.update(discovery_log.render())
                    continue

                # Parse the page requests
                discovery_log.update_status("Discovering APIs", "running")
                live.update(discovery_log.render())
                p_reqs = parse_apis(driver=cf.driver, target=cf.target, uri=uri, filtered=True)

                apis_called_passive = (
                    si.add_apis(llm_page_request_parser.parse_apis(json.dumps(p_reqs, indent=4)))
                    if len(p_reqs) > 0
                    else []
                )
                discovery_log.update_status("Discovering APIs", "done")

                # Parse the interactions
                discovery_log.update_status("Discovering Interactions", "running")
                live.update(discovery_log.render())
                interactions = llm_interactionparser.parse_interactions(soup)
                interaction_names, new_interactions_added = si.add_interactions(interactions)
                if new_interactions_added:
                    rerank_required = True

                logger.debug(f"Found Interactions: {", ".join(interaction_names)}")
                discovery_log.update_status("Discovering Interactions", "done")

                # Create the summary
                discovery_log.update_status("Summarizing Page", "running")
                live.update(discovery_log.render())
                summary = llm_summarizer.create_summary(soup)
                discovery_log.update_status("Summarizing Page", "done")
                live.update(discovery_log.render())

                # Create the page object
                # path, query_string = uri.split("?") if "?" in uri else (uri, None)
                page = Page(
                    uri=uri,
                    title=soup.title.string if soup.title else None,
                    original_soup=original_soup,
                    summary=summary,
                    outlinks=parse_links(original_soup),
                    interaction_names=interaction_names,
                    apis_called=apis_called_passive,
                )

                schedule.add_uris_to_todo(page.outlinks)
                schedule.add_interactions_to_todo(page.interaction_names)

                si.add_page(page)
                time.sleep(cf.selenium_rate)
            print(Text(f"Found Interactions: {", ".join(interaction_names)}"))

        elif schedule.interactions_todo:
            if rerank_required:
                ranker_log = RankerLog()
                with Live(refresh_per_second=10) as live:
                    print(Text("\nRanking Interactions", style="bold green"))
                    ranker_log.update_status("running")
                    live.update(ranker_log.render())
                    interaction_names = [interaction for interaction, _ in schedule.interactions_todo]
                    ranked_interactions = llm_rank_interactions(cf, interaction_names)
                    logger.debug(f"Re-Ranked Interactions: {ranked_interactions}")
                    schedule.interactions_todo = ranked_interactions
                    rerank_required = False
                    ranker_log.update_status("done")
                    live.update(ranker_log.render())
            interaction_name, interaction_limit = schedule.next_interaction()
            if interaction_limit <= 0:
                logger.debug(f"Skipping interaction {interaction_name} as limit is 0")
                continue

            interaction = si.get_interaction(interaction_name)
            logger.debug(f"Discovering interaction: {interaction_name}")
            print(Text(f"\nDiscovering interaction: {interaction_name}", style="bold green"))
            uri = si.get_uris_with_interaction(interaction_name)[0]
            # behaviour, all_p_reqs, all_paths, new_soup = interaction_agent.interact(
            #     uri=uri, interaction=json.dumps(interaction.to_dict())
            # )
            test_report, all_p_reqs_parsed, all_paths, new_interaction_context = interaction_agent.interact(
                uri=uri,
                interaction=json.dumps(interaction.to_dict()),
                limit=str(interaction_limit),
                interaction_context=interaction_context,
            )
            interaction_context += new_interaction_context

            apis_called_interaction = si.add_apis(all_p_reqs_parsed) if len(all_p_reqs_parsed) > 0 else []
            si.add_apis(all_p_reqs_parsed)

            interaction.test_report = test_report
            interaction.apis_called = apis_called_interaction
            interaction.tested = True

            logger.debug(f"All paths: {all_paths}")
            schedule.add_uris_to_todo(all_paths)  # Add the new paths to the schedule

            # TODO: handle this inside the agent (discover new interactions in same page with new soup)
            # if new_soup:  # Parse interactions if the page has changed
            #     interactions = llm_interactionparser.parse_interactions(soup) # signature has changed
            #     interaction_names = si.add_interactions(interactions)

            #     for interaction_name in interaction_names:
            #         logger.debug(f"Found Interaction: {interaction_name}")

            time.sleep(cf.selenium_rate)

    logger.debug("Discovery complete")

    return si
