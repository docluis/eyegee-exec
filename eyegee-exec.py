#!/usr/bin/python3
# from src.discover import discover_target
# from src.agent import test
from config import Config
from src.discovery import discover
from src.utils import output_to_file
from src.log import logger
import pickle
from src.vizualizer_backend.app import app

# cf = Config()

# logger.info("Starting EyeGee")
# logger.info(f"Taget: {cf.target}")

# # Discover the website
# si = discover(cf)

# output_to_file(si.pages)
# # Save si to file (so it can be imported later, maybe pickled)
# with open("siteinfo.pkl", "wb") as f:
#     pickle.dump(si, f)


# logger.info("EyeGee complete")

# cf.driver.quit()

app.run(debug=True)