import re
import json


def parse_action(text: str):
    if text.count("Action:") != 1:
        raise ValueError("必须且只能有一个 Action")

    tool = re.search(r"Action:\s*(\w+)", text).group(1)

    json_block = re.search(
        r"```json\s*(.*?)\s*```",
        text,
        re.S
    )

    if not json_block:
        raise ValueError("缺少 json block")

    return tool, json.loads(json_block.group(1))
