from typing import Protocol


class ITemplateRenderer(Protocol):
    def render(
        self,
        template_code: str,
        context: dict,
    ) -> tuple[str, str]: ...
