from pathlib import Path

from jinja2 import Template

BASE_DIR = Path(__file__).resolve().parents[1]

EMAIL_SUBJECTS = {
    "welcome": "Добро пожаловать!",
    "new_movie": "Новый фильм уже доступен!",
}

TEMPLATE_CODES = {
    "welcome": "welcome.html",
    "new_movie": "new_movie.html",
}


class TemplateRenderer:
    async def render(
        self,
        template_code: str,
        context: dict,
    ) -> tuple[str, str]:
        template_filename = TEMPLATE_CODES[template_code]
        template_path = BASE_DIR / "templates" / "email" / template_filename

        template_text = template_path.read_text(encoding="utf-8")

        template = Template(template_text)
        rendered_html = template.render(**context)

        subject = EMAIL_SUBJECTS[template_code]

        return subject, rendered_html
