import logging
from urllib.parse import urlparse
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options as ChromeOptions


class Config:
    def __init__(self) -> None:
        load_dotenv()

        ####### Selenium #######
        service = ChromeService(executable_path="/usr/bin/chromedriver")
        options = ChromeOptions()
        options.add_experimental_option("perfLoggingPrefs", {"enableNetwork": True})
        options.set_capability("goog:loggingPrefs", {"performance": "ALL"})
        self.driver = webdriver.Chrome(service=service, options=options)
        self.selenium_rate = 0.5

        ####### Model #######
        self.model = ChatOpenAI(model="gpt-4o")
        self.parser = StrOutputParser()


        ####### Target #######
        website = "http://127.0.0.1:3000"

        parsed_url = urlparse(website)
        self.target = f"{parsed_url.scheme}://{parsed_url.netloc}"
        self.initial_path = parsed_url.path

        self.check_config()

    def check_config(self) -> None:
        print("Checking Config")
        # TODO: Check if all required attributes are set/working
        if not hasattr(self, "driver"):
            raise ValueError("Driver not set")
        if not hasattr(self, "selenium_rate"):
            raise ValueError("Selenium Rate not set")
        if not hasattr(self, "model"):
            raise ValueError("Model not set")
        if not hasattr(self, "parser"):
            raise ValueError("Parser not set")
        if not hasattr(self, "target"):
            raise ValueError("Target not set")
        if not hasattr(self, "initial_path"):
            raise ValueError("Initial Path not set")