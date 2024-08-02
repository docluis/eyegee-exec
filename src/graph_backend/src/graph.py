import pickle
from src.discovery.siteinfo import SiteInfo


class Graph:
    def __init__(self, siteinfo_file):
        self.siteinfo = self.import_si(siteinfo_file)

        self.nodes = self.parse_nodes(self.siteinfo)
        self.links = self.parse_links(self.siteinfo)

    def import_si(self, siteinfo_file):
        with open(siteinfo_file, "rb") as f:
            si = pickle.load(f)
        return si

    def parse_nodes(self, si: SiteInfo):
        nodes = []
        # add page nodes
        for page in si.pages:
            # Construct a node from a page in JSON format
            # TODO: TEMPFIX, match same sites with different paths
            if page.path == "":
                page.path = "/"
            node = {
                "id": page.path,
                "label": page.path,
                "type": "page",
                "summary": page.summary,
                "outlinks": page.outlinks,
            }
            nodes.append(node)

        # add API nodes from the pages
        for page in si.pages:
            for api in page.apis_called:
                # Construct a node from an API in JSON format
                node = {
                    "id": f"{api["method"]} {api["path"]}",
                    "label": f"{api["method"]} {api["path"]}",
                    "type": "api",
                    "from": page.path,
                }
                nodes.append(node)

        # add interaction nodes
        for page in si.pages:
            for interaction in page.interactions:
                # Construct a node from an interaction in JSON format
                node = {
                    "id": interaction["name"],
                    "label": interaction["name"],
                    "type": "interaction",
                    "description": interaction["description"],
                    "input_fields": interaction["input_fields"],
                    "behaviour": interaction["behaviour"],
                }
                nodes.append(node)

        # add api nodes from the interactions
        for page in si.pages:
            for interaction in page.interactions:
                for api in interaction["apis_called"]:
                    # Construct a node from an API in JSON format
                    node = {
                        "id": f"{api["method"]} {api["path"]}",
                        "label": f"{api["method"]} {api["path"]}",
                        "type": "api",
                        "from": interaction["name"],
                    }
                    nodes.append(node)
        return nodes

    def parse_links(self, si: SiteInfo):
        links = []
        # add page links
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
                links.append(edge)
        # add API links
        for page in si.pages:
            for api in page.apis_called:
                edge = {
                    "id": f"{page.path}->{api["method"]} {api["path"]}",
                    "source": page.path,
                    "target": f"{api["method"]} {api["path"]}",
                }
                links.append(edge)
        # add interaction links
        for page in si.pages:
            for interaction in page.interactions:
                edge = {
                    "id": f"{page.path}->{interaction['name']}",
                    "source": page.path,
                    "target": interaction["name"],
                }
                links.append(edge)

        # add interaction to API links
        for page in si.pages:
            for interaction in page.interactions:
                for api in interaction["apis_called"]:
                    edge = {
                        "id": f"{interaction['name']}->{api['method']} {api['path']}",
                        "source": interaction["name"],
                        "target": f"{api['method']} {api['path']}",
                    }
                    links.append(edge)
        return links
