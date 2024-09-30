#!/usr/bin/python3
import os
import threading
import time
from config import Config
from src.graph.backend.app import init_app
from src.discovery.discovery import discover
from src.discovery.utils import output_to_file
from src.log import logger
from src.pretty_log import print_eyegee_exec_banner, print_eyegee_exec_footer
from src.graph.start_graph_frontend import start_graph_frontend
import pickle
import argparse

from rich.text import Text
from rich import print


def start_servers():
    print(Text("Starting eyegee-exec graph servers...", style="bold green"))
    # Start the frontend in a separate thread
    frontend_thread = threading.Thread(target=start_graph_frontend)
    frontend_thread.start()

    # Give the frontend some time to initialize (adjust if needed)
    time.sleep(5)

    print(Text("Starting backend...", style="bold green"))
    # Start the backend in the main thread
    backend_app = init_app()
    backend_app.run(port=9778, debug=False, use_reloader=False)
    # backend_app.run(port=9778, debug=True)

    # Wait for the frontend thread to completed
    frontend_thread.join()


def main():
    print_eyegee_exec_banner()

    parser = argparse.ArgumentParser(description="Autonomous Web Application Discovery Tool", epilog="For more settings, modify the `config.py` file")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("-d", "--discover", help="Discover the target website", action="store_true")
    mode.add_argument(
        "-g",
        "--graph",
        help="Start frontend and backend for visual representation of results",
        action="store_true",
    )
    parser.add_argument("-t", "--target", help="Target website to discover", type=str)
    parser.add_argument("--headless", help="Run selenium in headless mode", action="store_true")
    args = parser.parse_args()
    if args.discover and args.target is None:
        print(Text("Target is required for discovery mode", style="bold red"))
        exit(1)
    if args.discover:
        cf = Config(args=args)

        logger.debug("Starting EyeGee")
        logger.debug(f"Taget: {cf.target}")

        # Discover the website
        si = discover(cf)

        # Save si to file (so it can be imported later)
        with open("siteinfo.pkl", "wb") as f:
            pickle.dump(si, f)
        output_to_file(si)

        logger.debug("EyeGee complete")
        print_eyegee_exec_footer()

        cf.driver.quit()

    if args.graph:
        # check if siteinfo.pkl exists
        if not os.path.exists("siteinfo.pkl"):
            print(Text("siteinfo.pkl file not found, please run discovery first", style="bold red"))
            exit(1)
        start_servers()


if __name__ == "__main__":
    main()
