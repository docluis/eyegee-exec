import json
from typing import List
from bs4 import BeautifulSoup


class Page:
    def __init__(
        self,
        path: str,
        title: str,
        soup: BeautifulSoup,
        summary: str,
        outlinks: list,
        interactions: json, # TODO: change to list[Interaction] ?
        apis_called: json, # TODO: change to list[API] ?
    ) -> None:
        self.path = path
        self.title = title
        self.soup = soup
        self.summary = summary
        self.outlinks = outlinks
        self.interactions = interactions
        self.interactions_behaviour = List
        self.apis_called = apis_called
