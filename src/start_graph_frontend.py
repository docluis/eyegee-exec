import os
import subprocess
from src.log import logger

graph_frontend_path = "src/graph_frontend"


def start_graph_frontend():
    subprocess.run(["npm", "install"], check=True, cwd=graph_frontend_path)
    process = subprocess.Popen(["npm", "start"], cwd=graph_frontend_path)
    logger.info("Graph frontend started")
