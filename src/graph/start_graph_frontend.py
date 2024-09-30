import os
import subprocess
from src.log import logger
from rich.text import Text
from rich import print

graph_frontend_path = "src/graph/frontend"


def start_graph_frontend():
    try:
        print(Text("Installing frontend dependencies...", style="bold green"))
        print(Text("This may take a few minutes the first time you run it", style="yellow"))
        # Run npm install silently, ensuring it completes before moving on
        install_result = subprocess.run(
            ["npm", "install"],
            check=True,
            cwd=graph_frontend_path,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        print(Text("Starting frontend...", style="bold green"))
        # Check if npm install succeeded
        if install_result.returncode == 0:
            # Start the frontend process after install is successful
            process = subprocess.Popen(
                ["npm", "run", "dev", "--", "--port", "9777"],
                cwd=graph_frontend_path,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            logger.debug("Graph frontend started")
            print(Text("Frontend started, view at http://localhost:9777", style="bold green"))
            return process
        else:
            logger.error("npm install failed")
            return None
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to start frontend: {e}")
        return None
