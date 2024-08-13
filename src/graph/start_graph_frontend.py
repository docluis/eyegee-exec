import os
import subprocess
from src.log import logger

graph_frontend_path = "src/graph/frontend"


def start_graph_frontend():
    try:
        subprocess.run(["npm", "install"], check=True, cwd=graph_frontend_path)
        process = subprocess.Popen(
            # ["npm", "start"],
            # start on port 9777
            ["npm", "run", "dev", "--", "--port", "9777"],
            cwd=graph_frontend_path,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        logger.info("Graph frontend started")
        logger.info("View the frontend at http://localhost:9777")
        return process
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to start frontend: {e}")
        return None
