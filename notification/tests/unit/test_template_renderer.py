import pytest
from notification.adapters.templates.template_renderer import TemplateRenderer
from notification.core.exceptions import UnknownTemplateCode


def test_render_welcome_template():
    renderer = TemplateRenderer()

    subject, body = renderer.render(
        template_code="welcome", context={"first_name": "Valerii"}
    )

    assert subject == "Добро пожаловать!"
    assert "Valerii" in body
    assert "Добро пожаловать" in body


def test_render_unknown_template_code_raises_error():
    renderer = TemplateRenderer()

    with pytest.raises(UnknownTemplateCode):
        renderer.render(template_code="unknown", context={"first_name": "Valerii"})
