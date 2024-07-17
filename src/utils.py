import json
import config as cf

def parse_page_requests(path, performance_logs):
    """
    Parse the page requests from the given performance logs.
    """
    page_requests = []
    for log in performance_logs:
        log = json.loads(log["message"])["message"]
        if log["method"] == "Network.requestWillBeSent":
            if (
                log["params"]["request"]["url"] == cf.target + path
                and log["params"]["request"]["method"] == "GET"
            ):  # ignore requests to the same page
                continue
            page_request = {
                "url": log["params"]["request"]["url"],
                "method": log["params"]["request"]["method"],
                "headers": log["params"]["request"]["headers"],
                "postData": log["params"]["request"].get("postData"),
            }
            page_requests.append(page_request)
    # put the page_requests into a llm readable format
    page_requests = json.dumps(page_requests)
    return page_requests