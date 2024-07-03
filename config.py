import logging
from urllib.parse import urlparse

# Configuration for logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Configuration for the target
website = "http://127.0.0.1:3000"

parsed_url = urlparse(website)
target = f"{parsed_url.scheme}://{parsed_url.netloc}"
initial_path = parsed_url.path