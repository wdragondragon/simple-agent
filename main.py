from llm.client import create_client
from config.settings import OPENAI_MODEL
from core.agent import Agent

if __name__ == "__main__":
    client = create_client()
    agent = Agent(client, OPENAI_MODEL)

    result = agent.run(
        "请在我当前目录，编写一个python工具，要实现读取一个网页的功能。"
    )
    print(result)
