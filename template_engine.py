from abc import ABC

from jinja2 import Environment, FileSystemLoader

from component import NextPyComponent

class BaseTemplateEngine(ABC):
    def render_template(self, template_path, component: NextPyComponent):
        return NotImplemented

class NextPyTemplate(BaseTemplateEngine):
    """
    A wrapper component for rendering templates with Jinja2 templates
    """
    def __init__(self, template_dir="."):
        self.env = Environment(loader=FileSystemLoader(template_dir))  # Load templates from the current directory

    def render_template(self, template_path, **context):
        try:
            template = self.env.get_template(template_path)
            return template.render(
                **context
            )
        except Exception as e:
            raise e