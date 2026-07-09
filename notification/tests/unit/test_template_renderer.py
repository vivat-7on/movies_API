import pytest
from notification.core.exceptions import UnknownTemplateCode
from notification.services.template_renderer import TemplateRenderer


@pytest.mark.asyncio
async def test_render_welcome_template():
    renderer = TemplateRenderer()

    subject, body = renderer.render(
        template_code="welcome", context={"first_name": "Valerii"}
    )

    assert subject == "Добро пожаловать!"
    assert "Valerii" in body
    assert "Добро пожаловать" in body


@pytest.mark.asyncio
async def test_render_unknown_template_code_raises_error():
    renderer = TemplateRenderer()

    with pytest.raises(UnknownTemplateCode):
        renderer.render(template_code="unknown", context={"first_name": "Valerii"})
