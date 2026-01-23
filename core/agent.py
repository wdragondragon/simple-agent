import time
from datetime import timedelta
from core.state import State
from core.parser import parse_action
from core.prompt import SYSTEM_PROMPT
from tools.registry import TOOLS


class Agent:
    def __init__(self, client, model):
        self.client = client
        self.model = model

    def run(self, goal, max_steps=100):
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
        return {"step": step, "cost_time": str(timedelta(seconds=time.perf_counter() - start_time)),
                "result": result_msg}
