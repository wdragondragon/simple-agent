import json
import time
from datetime import timedelta

from core.parser import parse_action
from core.prompt import SYSTEM_PROMPT
from core.state import State
from llm.client import call_llm_with_tools
from tools.ConceptMemory import ConceptMemory
from tools.Memory import Memory
from tools.compressor import compress_memory
from tools.registry import TOOLS
from tools.schemas import TOOL_SCHEMAS


class Agent:
    def __init__(self, client, model):
        self.client = client
        self.model = model
        self.memory = Memory()
        self.concept_memory = ConceptMemory()

    def run(self, goal, max_steps=100):
        state = State.INIT

        step = 0
        last_action = None
        self.last_tool_calls = []
        result_msg = None
        start_time = time.perf_counter()
        while True:
            step += 1
            print(f"\n====== STEP {step} | STATE: {state.name} ======")

            # ===== THINK =====
            if state in (State.INIT, State.THINK):
                self.maybe_compress()
                messages = [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": f"目标：{goal}"}
                ]
                messages += self.concept_memory.dump()
                messages += self.memory.dump()
                print("询问：" + str(messages))
                assistant_msg = call_llm_with_tools(self.client, self.model, messages, tools=TOOL_SCHEMAS)
                print("回答：" + str(assistant_msg))

                # 将assistant的消息添加到内存（可能是content或tool_calls）
                msg_dict = {"role": "assistant"}
                if assistant_msg.content is not None:
                    msg_dict["content"] = assistant_msg.content
                if assistant_msg.tool_calls is not None:
                    # 将tool_calls转换为字典列表
                    try:
                        # 尝试使用 model_dump() (Pydantic v2) 或 dict() (Pydantic v1)
                        if hasattr(assistant_msg.tool_calls[0], 'model_dump'):
                            msg_dict["tool_calls"] = [tc.model_dump() for tc in assistant_msg.tool_calls]
                        else:
                            msg_dict["tool_calls"] = [tc.dict() for tc in assistant_msg.tool_calls]
                    except (AttributeError, IndexError):
                        # 如果转换失败，保持原样
                        msg_dict["tool_calls"] = assistant_msg.tool_calls
                self.memory.add_message(msg_dict)

                if assistant_msg.tool_calls:
                    # 有tool calls，进入ACT状态执行
                    self.last_tool_calls = assistant_msg.tool_calls
                    state = State.ACT
                else:
                    # 没有tool calls，检查是否有content作为最终答案
                    if assistant_msg.content:
                        # 将content作为最终答案（假设模型直接输出答案）
                        result_msg = assistant_msg.content
                        state = State.FINISH
                    else:
                        # 既无tool calls也无content，错误
                        self.memory.add("user", "ERROR: LLM returned empty response")
                        continue

            # ===== ACT =====
            elif state == State.ACT:
                # 执行每个tool call
                for tool_call in self.last_tool_calls:
                    func_name = tool_call.function.name
                    try:
                        func_args = json.loads(tool_call.function.arguments)
                    except json.JSONDecodeError as e:
                        observation = f"ERROR: 参数解析失败: {e}"
                        self.memory.add_message({
                            "role": "tool",
                            "content": observation,
                            "tool_call_id": tool_call.id
                        })
                        continue

                    if func_name not in TOOLS:
                        observation = f"ERROR: 未知工具 {func_name}"
                    else:
                        print(f"正在调用工具[{func_name}]，入参:{func_args}")
                        observation = TOOLS[func_name](**func_args)

                    print("我计算的Observation:", observation)
                    # 添加tool消息
                    self.memory.add_message({
                        "role": "tool",
                        "content": str(observation),
                        "tool_call_id": tool_call.id
                    })

                    if func_name == "finish":
                        result_msg = observation
                        state = State.FINISH
                        break  # 不再执行后续tool calls
                
                if state != State.FINISH:
                    state = State.OBSERVE

            # ===== OBSERVE =====
            elif state == State.OBSERVE:
                state = State.THINK

            # ===== FINISH =====
            elif state == State.FINISH:

                print("\n🎉 Agent 正常结束")
                break

        return {"step": step, "cost_time": str(timedelta(seconds=time.perf_counter() - start_time)),
                "result": result_msg}

    def maybe_compress(self):
        if len(self.memory.messages) < 100:
            return

        messages = self.concept_memory.dump()
        messages += self.memory.dump()
        concepts = compress_memory(self.model, messages)
        self.concept_memory.add(concepts)
        self.memory.clear()
