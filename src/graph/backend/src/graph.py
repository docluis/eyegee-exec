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
            if page.uri == "":
                page.uri = "/"
            node = {
                "id": page.uri,
                "label": page.uri,
                "type": "page",
                "summary": page.summary,
                "outlinks": page.outlinks,
                "interaction_names": page.interaction_names,
                "apis_called": page.apis_called,
            }
            nodes.append(node)

        for interaction in si.interactions:
            # Construct a node from an interaction in JSON format
            node = {
                "id": interaction.name,
                "label": interaction.name,
                "type": "interaction",
                "description": interaction.description,
                "input_fields": interaction.input_fields,
                "test_report": interaction.test_report,
                "tested": interaction.tested,
                "apis_called": interaction.apis_called,
            }
            nodes.append(node)

        # add api nodes
        for api in si.apis:
            # Construct a node from an API in JSON format
            params_json = []
            for param in api.params:
                param_json = {
                    "name": param.name,
                    "type": param.param_type,
                    "observed_values": param.observed_values,
                }
                params_json.append(param_json)
            node = {
                "id": f"{api.method} {api.route}",
                "label": f"{api.method} {api.route}",
                "type": "api",
                "params": params_json,
            }
            nodes.append(node)

        return nodes

    def parse_links(self, si: SiteInfo):
        links = []
        # add page links
        for page in si.pages:
            for outlink in page.outlinks:
                # TODO: TEMPFIX, figure out how to handle external links, also make sure to print either path or urlU+
                if outlink == "http://kitchencompany.com/" or outlink == "http://127.0.0.1/":
                    # skip this
                    continue
                edge = {
                    "id": f"{page.uri}->{outlink}",
                    "source": page.uri,
                    "target": outlink,
                }
                links.append(edge)

        # add interaction links
        for page in si.pages:
            for interaction_name in page.interaction_names:
                edge = {
                    "id": f"{page.uri}->{interaction_name}",
                    "source": page.uri,
                    "target": interaction_name,
                }
                links.append(edge)

        # add api links from pages
        for page in si.pages:
            for page_api_called in page.apis_called:  # passive api calls
                edge = {
                    "id": f"{page.uri}->{page_api_called}",
                    "source": page.uri,
                    "target": page_api_called,
                }
                links.append(edge)
        # add api links from interactions
        for interaction in si.interactions:
            for interaction_api_called in interaction.apis_called:  # active api calls
                edge = {
                    "id": f"{interaction.name}->{interaction_api_called}",
                    "source": interaction.name,
                    "target": interaction_api_called,
                }
                links.append(edge)
        return links
