#!/usr/bin/python3
# from src.discover import discover_target
# from src.agent import test
from config import Config
from src.discovery import discover
from src.utils import output_to_file
from src.logging import logger

cf = Config()

logger.info("Starting EyeGee")
logger.info(f"Taget: {cf.target}")

# Discover the website
si = discover(cf)

output_to_file(si.pages)
logger.info("EyeGee complete")

cf.driver.quit()
