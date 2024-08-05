import os
import subprocess
from src.log import logger

graph_frontend_path = "src/graph_frontend"


def start_graph_frontend():
    try:
        subprocess.run(["npm", "install"], check=True, cwd=graph_frontend_path)
        process = subprocess.Popen(
            ["npm", "start"],
            cwd=graph_frontend_path,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        logger.info("Graph frontend started")
        return process
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to start frontend: {e}")
        return None
