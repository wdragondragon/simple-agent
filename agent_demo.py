import os
import re
import json
import subprocess
import time
from enum import Enum
from dotenv import load_dotenv
from openai import OpenAI
from datetime import timedelta

load_dotenv("environment.env")
# =====================
# 1. LLM 初始化
# =====================
client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url=os.getenv("OPENAI_BASE_URL")
)

MODEL = os.getenv("OPENAI_MODEL")  # 或 qwen / deepseek-chat 等


# =====================
# 2. Agent 状态定义
# =====================

class State(Enum):
    INIT = 0
    THINK = 1
    ACT = 2
    OBSERVE = 3
    FINISH = 4


# =====================
# 3. 工具定义
# =====================

def calculator(expression: str):
    """安全计算工具"""
    try:
        return eval(expression, {"__builtins__": {}})
    except Exception as e:
        return f"计算错误: {e}"


def finish(answer: str):
    """结束工具"""
    return f"FINAL ANSWER: {answer}"


def list_folder(path):
    """
    遍历指定文件夹，返回文件和文件夹列表
    出参为字符串，每行格式：
    <全路径> <类型：文件/文件夹>
    """
    if not os.path.exists(path):
        return ""  # 文件夹不存在，返回空字符串

    lines = []
    for entry in os.listdir(path):
        full_path = os.path.join(path, entry)
        if os.path.isfile(full_path):
            lines.append(f"{full_path} 文件")
        elif os.path.isdir(full_path):
            lines.append(f"{full_path} 文件夹")
        else:
            lines.append(f"{full_path} 其他")

    return "\n".join(lines)


def read_file_safe(path):
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return "文件不存在"
    except Exception as e:
        return str(e)


def write_file_safe(path, mode, content):
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, mode, encoding='utf-8') as f:
            f.write(content)
        return "创建成功"
    except Exception as e:
        return str(e)


def tail_file(file_path: str, n: int):
    with open(file_path, 'rb') as f:
        f.seek(0, os.SEEK_END)  # 定位到文件末尾
        filesize = f.tell()
        buffer = bytearray()
        lines = []

        pointer = filesize - 1
        while pointer >= 0 and len(lines) < n:
            f.seek(pointer)
            char = f.read(1)
            if char == b'\n':
                lines.append(buffer[::-1].decode('utf-8', errors='ignore'))
                buffer = bytearray()
            else:
                buffer.append(char[0])
            pointer -= 1

        # 添加最后一行（文件第一行）
        if buffer:
            lines.append(buffer[::-1].decode('utf-8', errors='ignore'))

        return lines[::-1]  # 反转顺序，保证原来的顺序


def run_command(cmd, capture_output=True, text=True, shell=True):
    """
    通用执行系统命令的方法
    参数:
        cmd: str 或 list, 要执行的命令
        capture_output: 是否捕获输出
        text: 输出是否解码为字符串
        shell: 是否通过 shell 执行 (Windows 下某些命令需要 True)
    返回:
        dict:
            stdout: 标准输出
            stderr: 错误输出
            returncode: 返回码
    """
    try:
        result = subprocess.run(
            cmd,
            capture_output=capture_output,
            text=text,
            shell=shell,
            encoding='utf-8',
            errors='ignore'
        )
        return {
            "stdout": result.stdout.strip() if result.stdout else "",
            "stderr": result.stderr.strip() if result.stderr else "",
            "returncode": result.returncode
        }
    except Exception as e:
        return {
            "stdout": "",
            "stderr": str(e),
            "returncode": -1
        }


TOOLS = {
    "calculator": calculator,
    "finish": finish,
    "read_file": read_file_safe,
    "write_file_safe": write_file_safe,
    "tail_file": tail_file,
    "run_command": run_command,
    "list_folder": list_folder,
}

# =====================
# 4. Prompt 模板
# =====================

SYSTEM_PROMPT = """
你是一个严格的 ReAct Agent，你必须通过 Thought / Action / Observation 的方式逐步推理。

规则：
1. 每一步必须输出 Thought
2. 如果需要工具，必须输出 Action
3. Action 格式必须严格如下：

Action: tool_name
Action Input: 
```json
JSON
```

4. 工具执行后，你会收到 Observation
5. 你不能在 Thought 中直接给出最终答案，按照你认为合理的方式拆分 Action
6. 每次你只能输出一个Action，并由我给你输出一次Observation
7. 当你认为我给你的Observation为最终结果时，调用 finish 工具
8. 请考虑涉及到较大内容的Observation，这会较快的消耗token，
    如非必须，请尽量避免将未知大小的文件全部内容作为 Observation 返回，
    不到万不得已时，不要使用系统命令，若使用系统命令，请慎用会占用大量计算时间的命令。
    我当前的系统为windows11，如果你执行了涉及系统的命令，请使用适合windows系统的命令
    酌情基于以上情况，深度思考来使用你认为最优的工具。
9. 在执行finish时，只传入与目标强相关的内容。

可用工具（出参皆为str，请根据所支持的入参进行调用（基于python））：
- calculator(expression: str) 根据计算公式计算数值
- read_file(path: str) 读取文件全部内容，请尽量使用绝对路径
- write_file_safe(path: str, mode: char, content: str) 写入文件，请尽量使用绝对路径
- list_folder(path: str) 获取该路径的所有文件，并且输出他的全路径 和 他属于文件或文件夹
- tail_file(file_path: str, n: int) tail文件
- run_command(cmd: str) 执行系统命令
- finish(answer: str) 结束时调用该工具输出信息
"""


# =====================
# 5. Action 解析（强校验）
# =====================

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


# =====================
# 6. 状态机 Agent
# =====================


def run_agent(goal: str, max_steps=100):
    state = State.INIT
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": f"目标：{goal}"}
    ]

    step = 0
    last_action = None
    result_msg = None
    start_time = time.perf_counter()
    while step < max_steps:
        step += 1
        print(f"\n====== STEP {step} | STATE: {state.name} ======")

        # ===== THINK =====
        if state in (State.INIT, State.THINK):
            resp = client.chat.completions.create(
                model=MODEL,
                messages=messages,
                temperature=0
            )
            content = resp.choices[0].message.content
            print("回答：" + content)

            try:
                action_name, action_input = parse_action(content)
            except Exception as e:
                messages.append({
                    "role": "user",
                    "content": f"ERROR: {e}，请重新严格按格式输出"
                })
                continue

            last_action = (action_name, action_input)
            messages.append({"role": "assistant", "content": content})
            state = State.ACT

        # ===== ACT =====
        elif state == State.ACT:
            tool, params = last_action

            if tool not in TOOLS:
                observation = f"ERROR: 未知工具 {tool}"
            else:
                print(f"正在调用工具[{tool}]，入参:{params}")
                observation = TOOLS[tool](**params)

            print("我计算的Observation:", observation)

            messages.append({
                "role": "user",
                "content": f"Observation: {observation}"
            })

            if tool == "finish":
                result_msg = observation
                state = State.FINISH
            else:
                state = State.OBSERVE

        # ===== OBSERVE =====
        elif state == State.OBSERVE:
            state = State.THINK

        # ===== FINISH =====
        elif state == State.FINISH:

            print("\n🎉 Agent 正常结束")
            break

    else:
        print("⚠️ 达到最大步数，强制终止")
    return {"step": step, "cost_time": str(timedelta(seconds=time.perf_counter() - start_time)), "result": result_msg}


# =====================
# 5. 运行
# =====================

if __name__ == "__main__":
    goal = "请在我当前目录，编写一个python工具，要实现读取一个网页的功能。"
    result = run_agent(goal)
    print(result)
