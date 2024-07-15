import logging
from urllib.parse import urlparse
from dotenv import load_dotenv # type: ignore
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options as ChromeOptions



load_dotenv()

####### Selenium #######
# options = webdriver.FirefoxOptions()
# service = webdriver.FirefoxService(executable_path="/usr/bin/geckodriver")
# driver = webdriver.Firefox(service=service, options=options)
service = ChromeService(executable_path="/usr/bin/chromedriver")
options = ChromeOptions()
options.add_experimental_option("perfLoggingPrefs", {"enableNetwork": True})
options.set_capability("goog:loggingPrefs", {"performance": "ALL"})
driver = webdriver.Chrome(service=service, options=options)


####### Model #######
model = ChatOpenAI(model="gpt-4o")
parser = StrOutputParser()


####### Target #######
website = "http://127.0.0.1:3000"

parsed_url = urlparse(website)
target = f"{parsed_url.scheme}://{parsed_url.netloc}"
initial_path = parsed_url.path


####### Logging #######
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)