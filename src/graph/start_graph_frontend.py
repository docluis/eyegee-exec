import os
import subprocess
from src.log import logger

graph_frontend_path = "src/graph/frontend"


def start_graph_frontend():
    try:
        # Run npm install silently
        subprocess.run(["npm", "install"], check=True, cwd=graph_frontend_path, 
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        # Start the frontend process
        process = subprocess.Popen(
            ["npm", "run", "dev", "--", "--port", "9777"],
            cwd=graph_frontend_path,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        logger.debug("Graph frontend started")
        return process
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to start frontend: {e}")
        return None
