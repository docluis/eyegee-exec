#!/usr/bin/python3
from src.discover import discover_target
from src.agent import test
import config as cf

cf.logger.info("Starting EyeGee")
cf.logger.info(f"Target: {cf.target}")

# Discover the website
# discover_target()
test()
