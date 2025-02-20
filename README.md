# AutoGen Magentic-One Sample with Security best practices.


This sample demonstrates how to use the [AutoGen Magentic-One]((https://microsoft.github.io/autogen/stable/user-guide/agentchat-user-guide/magentic-one.html)) with security best practices like:

- **Code execution in Docker**: Making sure the AutoGen m1 can only execute code in a Docker container.
- **Safeguard File Access**: Making sure the AutoGen m1 can only access the file from a safe directory, in this sample it's the current directory. It can be changed by modifying the logic of safe directory in [_secured_markdown_file_browser.py](./overwrites/_secured_markdown_file_browser.py) file.
- **Human Oversight for each critical action**: Making sure the AutoGen m1 can only execute code or open a site or access a file after human approval. It can be changed by modifying the description of human agents in [_secured_m1.py](./overwrites/_secured_m1.py) file and in the `next agent` selection prompt in [_secured_m1_orchestrator.py](./overwrites/_secured_m1_orchestrator.py) file.
- **Termination**: Making sure the AutoGen m1 can be terminated by human agents at any time. It can be changed by modifying the termination command in [_secured_m1.py](./overwrites/_secured_m1.py) file.

For more information on how to use this sample, please refer:

- [How to Use Magentic One](https://github.com/microsoft/autogen/tree/main/python/packages/magentic-one-cli)


## Prerequisites

- Python 3.12 or later
- Docker Desktop
- Azure OpenAI Service

## How to run

1. Clone the repository
1. Install the dependencies
   ```bash
   pip install -r requirements.txt
   ```
1. Create a `.env` file in the root directory by copying the `.env.example` file and filling in the required values.
1. Run some of the example with security best practices and see the result
   ```bash
   python secured_m1.py --secure "Find the best restaurant in town"
   python secured_m1.py --secure "Get Microsoft Stock Trend for last 5 years and plot the graph"
   python secured_m1.py --secure "Read the TEST.CSV file from the parent directory and summarize the content"
   ```