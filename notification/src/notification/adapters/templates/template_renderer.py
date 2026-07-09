from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

from notification.core.exceptions import UnknownTemplateCode
from notification.interfaces.jinja_renderer import ITemplateRenderer

BASE_DIR = Path(__file__).resolve().parents[2]
TEMPLATE_DIR = BASE_DIR / "templates" / "email"

EMAIL_SUBJECTS = {
    "welcome": "Добро пожаловать!",
    "new_movie": "Новый фильм уже доступен!",
}

TEMPLATE_CODES = {
    "welcome": "welcome.html",
    "new_movie": "new_movie.html",
}


class TemplateRenderer(ITemplateRenderer):
    def __init__(self) -> None:
        self.env = Environment(
            loader=FileSystemLoader(TEMPLATE_DIR),
            autoescape=select_autoescape(["html"]),
        )

    def render(  # noqa: WPS210
        self,
        template_code: str,
        context: dict,
    ) -> tuple[str, str]:
        if template_code not in EMAIL_SUBJECTS or template_code not in TEMPLATE_CODES:
            raise UnknownTemplateCode(f"Unknown template code: {template_code}")

        template = self.env.get_template(TEMPLATE_CODES[template_code])

        return EMAIL_SUBJECTS[template_code], template.render(**context)
