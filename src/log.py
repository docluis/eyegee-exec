import logging

# Write to log and console
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("eyegee.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)
