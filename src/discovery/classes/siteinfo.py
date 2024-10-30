import json
from src.discovery.llm.model_classes import ApiModel, InteractionModel
from src.discovery.classes.interaction import Interaction
from src.discovery.classes.page import Page
from src.discovery.classes.api import Api
from src.log import logger
from bs4 import BeautifulSoup
from typing import List, Dict, Tuple


class SiteInfo:
    def __init__(self, target: str) -> None:
        self.target = target

        self.pages: List[Page] = []
        self.pages_hashes: List[int] = []

        self.apis: List[Api] = []

        self.interactions: List[Interaction] = []

    def check_if_visited(self, soup: BeautifulSoup) -> bool:
        page_hash = hash(soup)
        if page_hash in self.pages_hashes:
            return True
        else:
            self.pages_hashes.append(page_hash)
            return False

    def add_page(self, page: Page) -> None:
        self.pages.append(page)

    def get_api(self, method: str, path: str) -> Api:
        for api in self.apis:
            if api.method == method and api.path == path:
                return api
        return None

    def add_apis(self, apis_model: List[ApiModel]) -> List[str]:
        """
        Add the given APIs to the site info. If the API already exists, update the parameters.

        Returns a list of the APIs that were added.
        """
        # TODO: simplify this to just add ApiModel to site info
        added_apis = []
        for api in apis_model:
            found = self.get_api(api.method, api.path)
            if found is None:
                api_obj = Api(api.method, api.path)
                self.apis.append(api_obj)
                found = api_obj
            added_apis.append(f"{found.method} {found.path}")
            # Add the url parameters
            logger.debug(f"Adding API: {found.method} {found.path}")
            logger.debug(f"Api: {api}")
            # Adding url parameters
            if (
                api.query_string is not None
                and api.query_string != ""
                and "=" in api.query_string
            ):
                split_qs = api.query_string.split("&")
                for qs in split_qs:
                    key, value = qs.split("=")
                    if key not in found.params:
                        found.add_param(key, "url")
                    found.get_param(key).add_observed_value(value)
            # Adding body parameters (postData)
            if "Content-Type" in api.headers:
                content_type = api.headers["Content-Type"]
                # TODO: make sure this works for url encoded and json and form and etc
                if "application/json" in content_type:
                    if api.postData != "":
                        for key, value in api.postData.items():
                            if key not in found.params:
                                found.add_param(key, "body")
                            found.get_param(key).add_observed_value(value)
            # Adding URL Path Parameters
            if api.url_path_params is not None:
                for key, value in api.url_path_params.items():
                    if key not in found.params:
                        found.add_param(key, "url_path")
                    found.get_param(key).add_observed_value(value)


        return added_apis

    def add_interactions(self, interactions: List[InteractionModel]) -> Tuple[List[str], bool]:
        """
        Add the given list of interactions to the SiteInfo Object.

        Returns a list of the added Interaction Names.
        """
        interaction_names = []
        new_interactions_added = False
        for interaction in interactions:
            interaction_names.append(interaction.name)
            # check if the interaction already exists in self.interactions
            found = False
            for i in self.interactions:
                if i.name == interaction.name:
                    found = True
                    break
            if not found:
                new_interactions_added = True
                interaction_obj = Interaction(
                    interaction.name,
                    interaction.description,
                    interaction.input_fields,
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
