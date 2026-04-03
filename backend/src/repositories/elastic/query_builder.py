class QueryBuilder:
    def __init__(self):
        self._filters = []
        self._should = []

    def filter_term(self, field: str, value: str) -> "QueryBuilder":
        self._filters.append({"term": {field: value}})
        return self

    def filter_nested(
        self,
        path: str,
        field: str,
        value: str,
        ) -> "QueryBuilder":
        self._filters.append(
            {
                "nested": {
                    "path": path,
                    "query": {
                        "term": {field: value},
                        },
                    },
                },
            )
        return self

    def should_nested(
        self,
        path: str,
        field: str,
        value: str,
        ) -> "QueryBuilder":
        self._should.append(
            {
                "nested": {
                    "path": path,
                    "query": {
                        "term": {field: value},
                        },
                    },
                },
            )
        return self

    def match(
        self,
        field: str,
        value: str,
        operator: str = "and",
        ) -> "QueryBuilder":
        self._filters.append(
            {
                "match": {
                    field: {
                        "query": value,
                        "operator": operator,
                        },
                    },
                }
            )
        return self

    def build(self) -> dict:
        if self._filters and self._should:
            return {
                "bool": {
                    "filter": self._filters,
                    "should": self._should,
                    "minimum_should_match": 1,
                    },
                }
        if self._filters:
            return {
                "bool": {
                    "filter": self._filters,
                    },
                }
        if self._should:
            return {
                "bool": {
                    "should": self._should,
                    "minimum_should_match": 1,
                    },
                }

        return {"match_all": {}}
