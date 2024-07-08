#!/usr/bin/python3
from src.discover import discover_target
import config as cf

cf.logger.info("Starting EyeGee")
cf.logger.info(f"Target: {cf.target}")

# Discover the website
discover_target()
