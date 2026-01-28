class ConceptMemory:
    def __init__(self):
        self.concepts = []

    def add(self, new_items):
        for item in new_items:
            if item not in self.concepts:
                self.concepts.append(item)

    def dump(self):
        return [{"role": "system", "content": f"已知事实：{c}"} for c in self.concepts]

    def clear(self):
        self.concepts = []
