import logging
from urllib.parse import urlparse
from dotenv import load_dotenv # type: ignore
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser



load_dotenv()


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