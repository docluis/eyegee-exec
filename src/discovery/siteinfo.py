import json
from urllib.parse import urlparse
from src.discovery.api import Api
from src.log import logger
from bs4 import BeautifulSoup


class SiteInfo:
    def __init__(self, target: str, initial_path: str) -> None:
        self.target = target
        self.initial_path = initial_path

        self.paths_todo = [initial_path]
        self.paths_visited = []

        self.pages = []
        self.pages_hashes = []

        self.apis = []

    def check_if_visited(self, soup: BeautifulSoup) -> bool:
        page_hash = hash(soup)
        if page_hash in self.pages_hashes:
            return True
        else:
            self.pages_hashes.append(page_hash)
            return False

    def add_paths_to_todo(self, paths: list) -> None:
        for path in paths:
            # if path starts with http:// or https://, make sure its in scope (same domain)
            if path.startswith("http://") or path.startswith("https://"):
                if urlparse(path).netloc != self.target:
                    logger.debug(f"Skipping outlink {path} as it is out of scope")
                    continue

            if path not in self.paths_todo and path not in self.paths_visited:
                self.paths_todo.append(path)

    def add_page(self, page) -> None:
        self.pages.append(page)

    def get_api(self, method: str, route: str) -> Api:
        for api in self.apis:
            if api.method == method and api.route == route:
                return api
        return None

    def add_apis(self, apis: list) -> list:
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
            if api["query_string"] != "" and "=" in api["query_string"]:
                query_string = api["query_string"]
                spit_qs = query_string.split("&")
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
