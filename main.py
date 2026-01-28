from llm.client import create_client
from config.settings import OPENAI_MODEL
from core.agent import Agent

if __name__ == "__main__":
    client = create_client()
    agent = Agent(client, OPENAI_MODEL)

    result = agent.run(
        "请在我的电脑上，找到data-unify-query-platform应用最后一天的日志，并把最后一行打印给我"
    )
    print(result)
