#!/usr/bin/python3
# from src.discover import discover_target
# from src.agent import test
from config import Config
from src.discovery import discover
from src.utils import output_to_file
from src.log import logger
import pickle
from src.vizualizer_backend.app import init_app
import argparse

parser = argparse.ArgumentParser(description="EyeGee")
parser.add_argument(
    "-d", "--discover", help="Discover the target website", action="store_true"
)
parser.add_argument(
    "-g",
    "--graph",
    help="Start backendserver for visual representation of results",
    action="store_true",
)
args = parser.parse_args()

if args.discover:
    cf = Config()

    logger.info("Starting EyeGee")
    logger.info(f"Taget: {cf.target}")

    # Discover the website
    si = discover(cf)

    # Save si to file (so it can be imported later)
    with open("siteinfo.pkl", "wb") as f:
        pickle.dump(si, f)
    output_to_file(si.pages)

    logger.info("EyeGee complete")

    cf.driver.quit()

if args.graph:
    app = init_app()
    app.run(debug=True)
