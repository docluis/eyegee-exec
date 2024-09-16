import logging

# Write to log and console
logging.basicConfig(
    level=logging.INFO,
    # format="%(name)s - %(asctime)s - %(levelname)s - %(message)s",
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("eyegee.log"), logging.StreamHandler()],
)
logger = logging.getLogger(__name__)

# Suppress logging from httpx, httpcore, urllib3, and openai
logging.getLogger('httpx').setLevel(logging.ERROR)
logging.getLogger('httpcore').setLevel(logging.ERROR)
logging.getLogger('urllib3.connectionpool').setLevel(logging.ERROR)
logging.getLogger('openai._base_client').setLevel(logging.ERROR)