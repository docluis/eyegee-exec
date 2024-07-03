#!/usr/bin/python3
from src.discover import discover_target
import config

config.logger.info("Starting EyeGee")
config.logger.info(f"Target: {config.target}")

# Discover the website
discover_target()
