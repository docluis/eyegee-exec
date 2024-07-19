from urllib.parse import urlparse
from venv import logger
from bs4 import BeautifulSoup


class SiteInfo:
    def __init__(self, target: str, initial_path: str) -> None:
        self.target = target
        self.initial_path = initial_path

        self.paths_todo = [initial_path]
        self.paths_visited = []

        self.pages = []
        self.pages_hashes = []

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
                        
