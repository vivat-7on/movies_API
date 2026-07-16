class SortBuilder:
    def __init__(self, allowed_fields: set[str]) -> None:
        self._sort: list[dict] = []
        self._allowed_fields = allowed_fields

    def add(
        self,
        field: str,
        order: str = "asc",
        missing: str = "_last",
    ) -> "SortBuilder":
        if field not in self._allowed_fields:
            raise ValueError(f"Field {field} not in allowed fields")

        if order not in {"asc", "desc"}:
            raise ValueError(f"Order {order} not in allowed orders")

        self._sort.append(
            {
                field: {
                    "order": order,
                    "missing": missing,
                },
            },
        )
        return self

    def build(self) -> list[dict] | None:
        return self._sort if self._sort else None
