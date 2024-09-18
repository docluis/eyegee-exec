from src.log import logger
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
        self.chromedriver_path = "/usr/bin/chromedriver"
        self.service = ChromeService(executable_path=self.chromedriver_path)
        self.options = ChromeOptions()
        self.options.add_argument("--lang=en")
        self.options.add_experimental_option("perfLoggingPrefs", {"enableNetwork": True})
        self.options.set_capability("goog:loggingPrefs", {"performance": "ALL"})
        self.driver = webdriver.Chrome(service=self.service, options=self.options)
        self.selenium_rate = 0.5

        ####### Model #######
        self.model = ChatOpenAI(model="gpt-4o-mini", temperature=0.2)
        # self.advanced_model= ChatOpenAI(model="gpt-4o", temperature=0.2)
        self.advanced_model = ChatOpenAI(model="gpt-4o-mini", temperature=0.2)
        self.parser = StrOutputParser()


        ####### Target #######
        # website = "http://127.0.0.1:3000"
        website = "http://localhost:80/"

        parsed_url = urlparse(website)
        self.target = f"{parsed_url.scheme}://{parsed_url.netloc}"
        self.initial_path = parsed_url.path

        ####### Interactions #######
        self.interaction_test_limit = 10 # the maximum number of interactions to test

        ####### Check Config #######
        self.check_config()

    def check_config(self) -> None:
        logger.info("Checking Config")
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