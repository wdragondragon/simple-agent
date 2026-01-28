from collections import deque


class Memory:
    def __init__(self, max_len=1000):
        self.messages = deque(maxlen=max_len)

    def add(self, role: str, content: str):
        self.messages.append({
            "role": role,
            "content": content
        })

    def add_message(self, message: dict):
        self.messages.append(message)

    def dump(self):
        return list(self.messages)

    def clear(self):
        self.messages.clear()
