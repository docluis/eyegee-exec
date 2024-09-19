import json
from src.discovery.interaction import Interaction
from src.discovery.page import Page
from src.discovery.api import Api
from src.log import logger
from bs4 import BeautifulSoup
from typing import List, Dict, Tuple


class SiteInfo:
    def __init__(self, target: str) -> None:
        self.target = target

        self.pages = []
        self.pages_hashes = []

        self.apis = []

        self.interactions = []

    def check_if_visited(self, soup: BeautifulSoup) -> bool:
        page_hash = hash(soup)
        if page_hash in self.pages_hashes:
            return True
        else:
            self.pages_hashes.append(page_hash)
            return False

    def add_page(self, page: Page) -> None:
        self.pages.append(page)

    def get_api(self, method: str, route: str) -> Api:
        for api in self.apis:
            if api.method == method and api.route == route:
                return api
        return None

    def add_apis(self, apis: List[Dict]) -> List[str]:
        """
        Add the given APIs to the site info. If the API already exists, update the parameters.

        Returns a list of the APIs that were added.
        """
        added_apis = []
        for api in apis:
            found = self.get_api(api["method"], api["path"])
            if found is None:
                api_obj = Api(api["method"], api["path"])
                self.apis.append(api_obj)
                found = api_obj
            added_apis.append(f"{found.method} {found.route}")
            # Add the url parameters
            logger.debug(f"Adding API: {found.method} {found.route}")
            logger.debug(f"Api: {api}")
            if (
                api["query_string"] is not None
                and api["query_string"] != ""
                and "=" in api["query_string"]
            ):
                spit_qs = api["query_string"].split("&")
                for qs in spit_qs:
                    key, value = qs.split("=")
                    if key not in found.params:
                        found.add_param(key, "url")
                    found.get_param(key).add_observed_value(value)
            # Add the body parameters (postData)
            if "Content-Type" in api["headers"]:
                content_type = api["headers"]["Content-Type"]
                # TODO: make sure this works for url encoded and json and form and etc
                if "application/json" in content_type:
                    if api["postData"] != "":
                        post_data = json.loads(api["postData"])
                        for key, value in post_data.items():
                            if key not in found.params:
                                found.add_param(key, "body")
                            found.get_param(key).add_observed_value(value)

        return added_apis

    def add_interactions(self, interactions: List[dict]) -> Tuple[List[str], bool]:
        """
        Add the given list of interactions to the SiteInfo Object.

        Returns a list of the added Interaction Names and a boolean indicating if new interactions were added.
        """
        interaction_names = []
        new_interactions_added = False
        for interaction in interactions:
            interaction_names.append(interaction["name"])
            # check if the interaction already exists in self.interactions
            found = False
            for i in self.interactions:
                if i.name == interaction["name"]:
                    found = True
                    break
            if not found:
                new_interactions_added = True
                interaction_obj = Interaction(
                    interaction["name"],
                    interaction["description"],
                    interaction["input_fields"],  # json.loads?
                )
                self.interactions.append(interaction_obj)
        return interaction_names, new_interactions_added
    
    def get_interaction(self, interaction_name: str) -> Interaction:
        for interaction in self.interactions:
            if interaction.name == interaction_name:
                return interaction
        return None

    def get_uris_with_interaction(self, interaction_name: str) -> List[str]:
        uris = []
        for page in self.pages:
            if interaction_name in page.interaction_names:
                uris.append(page.uri)
        return uris
