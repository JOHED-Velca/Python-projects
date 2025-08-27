from jinja2 import Environment, FileSystemLoader, select_autoescape
from pathlib import Path


TEMPLATES_DIR = Path(__file__).parent / "templates"


_env = Environment(
loader=FileSystemLoader(str(TEMPLATES_DIR)),
autoescape=select_autoescape(["html", "xml"]),
)


DEFAULT_TEMPLATE = "cover_letter.html"


def render_cover_letter(context: dict, template_name: str = DEFAULT_TEMPLATE) -> str:
    template = _env.get_template(template_name)
    return template.render(**context)


# For PDFs: consider WeasyPrint later
# from weasyprint import HTML
# def html_to_pdf(html: str, output_path: str):
# HTML(string=html).write_pdf(output_path)