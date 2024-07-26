import pickle
import json
from src.page import Page
from src.siteinfo import SiteInfo


class Graph:
    def __init__(self, siteinfo_file):
        self.siteinfo = self.import_si(siteinfo_file)

        self.site_nodes = self.parse_site_nodes(self.siteinfo)
        self.site_links = self.parse_site_links(self.siteinfo)
        self.api_nodes = self.parse_api_nodes(self.siteinfo)
        self.api_links = self.parse_api_links(self.siteinfo)

    def import_si(self, siteinfo_file):
        with open(siteinfo_file, "rb") as f:
            si = pickle.load(f)
        return si

    def parse_site_nodes(self, si: SiteInfo):
        site_nodes = []
        for page in si.pages:
            # Construct a node from a page in JSON format
            # TODO: TEMPFIX, match same sites with different paths
            if page.path == "":
                page.path = "/"
            node = {
                "id": page.path,
                "label": page.path,
                "type": "page",
            }
            site_nodes.append(node)
        return site_nodes

    def parse_api_nodes(self, si: SiteInfo):
        api_nodes = []
        for page in si.pages:
            for api in page.apis_called:
                # Construct a node from an API in JSON format
                node = {"id": api["url"], "label": api["url"], "type": "api"}
                api_nodes.append(node)
        return api_nodes

    def parse_site_links(self, si: SiteInfo):
        site_links = []
        for page in si.pages:
            for outlink in page.outlinks:
                # TODO: TEMPFIX, figure out how to handle external links, also make sure to print either path or urlU+
                if outlink == "http://kitchencompany.com/":
                    # skip this
                    continue
                edge = {
                    "id": f"{page.path}->{outlink}",
                    "source": page.path,
                    "target": outlink,
                }
                site_links.append(edge)
        return site_links

    def parse_api_links(self, si: SiteInfo):
        api_links = []
        for page in si.pages:
            for api in page.apis_called:
                edge = {
                    "id": f"{page.path}->{api['url']}",
                    "source": page.path,
                    "target": api["url"],
                }
                api_links.append(edge)
        return api_links
