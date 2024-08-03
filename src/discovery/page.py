from typing import List, Dict
from bs4 import BeautifulSoup


class Page:
    def __init__(
        self,
        path: str,
        title: str,
        soup: BeautifulSoup,
        summary: str,
        outlinks: List[str],
        interactions: List[Dict],  # TODO: change to list[Interaction] ?
        apis_called: List[Dict],  # TODO: change to list[API] ?
    ) -> None:
        self.path = path
        self.title = title
        self.soup = soup
        self.summary = summary
        self.outlinks = outlinks
        self.interactions = interactions
        self.apis_called = apis_called
