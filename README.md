# eyegee-exec

Autonomous Web Application Discovery Tool

The eyegee-exec tool utilizes large language models (LLMs) to autonomously discover web applications. Its primary goal is to map functionalities and provide an overview of the potential attack surface of the target application.

The application passively crawls websites, noting outgoing web requests and user interactions. It then generates user inputs and submits test data to these interactions to assess the application's behavior.

Results are presented as a graph, illustrating connections between pages, API calls, and interactions.

> Note: Note: While eyegee-exec should be compatible with other vendors or local LLMs, it has been tested only with OpenAI's cloud models to date.

## How to Run

This tool requires the installation of the `ChromeDriver` application. On Arch Linux-based operating systems, it can be installed using AUR package managers. Please refer to the official [ChromeDriver documentation](https://developer.chrome.com/docs/chromedriver/get-started) for installation instructions on other operating systems.

1. **Install ChromeDriver**

Ensure ChromeDriver is installed on your system.

2. **Create and Activate a Python Virtual Environment**
```bash
python -m venv venv
source venv/bin/activate
```
3. **Install the requirements**
```bash
pip install -r requirements.txt
```
4. **Setup the Environment Variables**
Create a .env file and add your Open AI Key:
```bash
touch .env
vim .env
# Add the following line to the file:
OPENAI_API_KEY=<YOUR_KEY_HERE>
```
5. **Configure the Application**
Adjust the configuration in `config.py`:
```bash
vim config.py
# Set the target website and other settings such as chromedriver_path
```
6. **Execute the Discovery Module**
Run the discovery module to start mapping the web application:
```bash
python eyegee-exec.py -d
```
7. **Visualize the Results**
To visualize the results as a graph, execute the graph module:
```bash
python eyegee-exec.py -g
```
