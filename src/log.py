import logging

# Write to log and console
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("eyegee.log"), logging.StreamHandler()],
)
logger = logging.getLogger(__name__)

# Suppress logging from httpx, httpcore, and urllib3
logging.getLogger('httpx').setLevel(logging.ERROR)
logging.getLogger('httpcore').setLevel(logging.ERROR)
logging.getLogger('urllib3.connectionpool').setLevel(logging.ERROR)