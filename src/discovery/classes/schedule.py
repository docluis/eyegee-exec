from typing import List, Tuple
from urllib.parse import urlparse
from src.log import logger


class Schedule:
    def __init__(self, target: str, initial_path: str) -> None:
        self.target = target

        self.uris_todo: List[str] = [initial_path]
        self.uris_visited: List[str] = []

        self.interactions_todo: List[Tuple[str, int]] = []
        self.interactions_visited: List[Tuple[str, int]] = []

    def next_uri(self) -> str:
        if self.uris_todo:
            next_path = self.uris_todo.pop(0)
            self.uris_visited.append(next_path)
            return next_path
        else:
            return None

    def add_uris_to_todo(self, paths: List[str]) -> None:
        for path in paths:
            # if path starts with http:// or https://, make sure its in scope (same domain)
            if path.startswith("http://") or path.startswith("https://"):
                if urlparse(path).netloc != self.target:
                    logger.debug(f"Skipping outlink {path} as it is out of scope")
                    continue

            if path not in self.uris_todo and path not in self.uris_visited:
                self.uris_todo.append(path)

    def next_interaction(self) -> Tuple[str, int]:
        if self.interactions_todo:
            next_interaction = self.interactions_todo.pop(0)
            self.interactions_visited.append(next_interaction)
            return next_interaction
        else:
            return None

    def add_interactions_to_todo(self, interactions: List[str]) -> None:
        for interaction in interactions:
            if (
                interaction not in self.interactions_todo
                and interaction not in self.interactions_visited
            ):
                self.interactions_todo.append((interaction, 0))

    def debug_print_schedule(self) -> None:
        logger.debug(f"URIs Todo: {self.uris_todo}")
        logger.debug(f"URIs Visited: {self.uris_visited}")
        logger.debug(f"Interactions Todo: {self.interactions_todo}")
        logger.debug(f"Interactions Visited: {self.interactions_visited}")