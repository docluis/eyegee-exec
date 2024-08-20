from typing import List, Dict
from bs4 import BeautifulSoup


class Page:
    def __init__(
        self,
        path: str | None,
        title: str | None,
        original_soup: BeautifulSoup,
        summary: str,
        outlinks: List[str],
        interaction_names: List[str],
        apis_called: List[str],
    ) -> None:
        self.path = path
        self.title = title
        self.original_soup = original_soup
        self.summary = summary
        self.outlinks = outlinks
        self.interaction_names = interaction_names
        self.apis_called = apis_called
