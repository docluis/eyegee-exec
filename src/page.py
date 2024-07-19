from bs4 import BeautifulSoup


class Page:
    def __init__(
        self,
        path: str,
        title: str,
        soup: BeautifulSoup,
        summary: str,
        outlinks: list,
        interactions: str, # TODO: change to list[Interaction] ?
        apis_called: str, # TODO: change to list[API] ?
    ) -> None:
        self.path = path
        self.title = title
        self.soup = soup
        self.summary = summary
        self.outlinks = outlinks
        self.interactions = interactions
        self.apis_called = apis_called
