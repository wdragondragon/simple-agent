import time
from datetime import timedelta

from core.parser import parse_action
from core.prompt import SYSTEM_PROMPT
from core.state import State
from tools.ConceptMemory import ConceptMemory
from tools.Memory import Memory
from tools.compressor import compress_memory
from tools.registry import TOOLS


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
                resp = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=0
                )
                content = resp.choices[0].message.content
                print("回答：" + content)

                try:
                    action_name, action_input = parse_action(content)
                except Exception as e:
                    self.memory.add("user", f"ERROR: {e}，请重新严格按格式输出")
                    continue

                last_action = (action_name, action_input)
                self.memory.add("assistant", content)
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
                self.memory.add("user", f"Observation: {observation}")

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
