from fastapi import Query


class PaginationQuery:
    def __init__(
        self,
        page_number: int = Query(1, ge=1),
        page_size: int = Query(50, ge=1, le=100),
    ):
        self.page_number = page_number
        self.page_size = page_size
