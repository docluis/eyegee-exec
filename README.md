# eyegee-exec

Autonomous Web Application Discovery Tool

The eyegee-exec tool utilizes large language models (LLMs) to autonomously discover web applications. Its primary goal is to map functionalities and provide an overview of the potential attack surface of the target application.

The application passively crawls websites, noting outgoing web requests and user interactions. It then generates user inputs and submits test data to these interactions to assess the application's behavior.

Results are presented as a graph, illustrating connections between pages, API calls, and interactions.

> Note: Note: While eyegee-exec should be compatible with other vendors or local LLMs, it has been tested only with OpenAI's cloud models to date.

### Getting Started

1. **Install ChromeDriver**

Ensure [ChromeDriver](https://developer.chrome.com/docs/chromedriver/get-started) is installed on your system. This is required for the discovery process.

2. **Install Node.js and npm**

Ensure Node.js and npm are installed on your system and configured in your system's PATH environment variable. This is required for the webserver with the graph interface.

3. **Create and Activate a Python Virtual Environment**

```bash
python -m venv venv
source venv/bin/activate
```

4. **Install the requirements**

```bash
pip install -r requirements.txt
```

5. **Setup the Environment Variables**

```bash
touch .env
vim .env
# Add the following line to the file:
OPENAI_API_KEY=<YOUR_KEY_HERE>
```

6. **Optional: Configure the Application**
   Adjust the configuration in `config.py`:

```bash
vim config.py
# Set llm model other settings such as chromedriver_path
```

7. **Execute the Discovery Module**
   Run the discovery module to start mapping a web application:

```bash
python eyegee-exec.py -d -t http://localhost:80/
```

8. **Visualize the Results**
   To visualize the results as a graph, execute the graph module:

```bash
python eyegee-exec.py -g
```

### Test this tool

An example web application to test this tool can be accessed under: https://github.com/docluis/dentist or https://github.com/docluis/card_market

### Credits & Motivation

This tool was originally inspired by a [Blogpost](https://josephthacker.com/ai/2024/02/21/hackbots.html) by Joseph Thacker. The tool was developed to present an ethical non-intrusive approach to autonomous LLM-based security analysis. 

Development of eyegee-exec was made possible through the Bundesnachrichtendienst’s “Summer of Code” scholarship program, which provided critical resources for this project.