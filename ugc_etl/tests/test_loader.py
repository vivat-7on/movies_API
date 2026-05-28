class FakeClickHouseClient:
    def __init__(self):
        self.queries = []

    def execute(self, query, data=None):
        self.queries.append((query, data))
