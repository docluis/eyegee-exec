#!/usr/bin/python3
from config import Config
from src.graph_backend.app import init_app
from src.discovery.discovery import discover
from src.discovery.utils import output_to_file
from src.log import logger
from src.start_graph_frontend import start_graph_frontend
import pickle
import argparse

parser = argparse.ArgumentParser(description="EyeGee")
parser.add_argument(
    "-d", "--discover", help="Discover the target website", action="store_true"
)
parser.add_argument(
    "-g",
    "--graph",
    help="Start frontend and backend for visual representation of results",
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
    # Start the graph frontend
    start_graph_frontend()

    # Start the graph backend
    app = init_app()
    app.run(port=9778)
