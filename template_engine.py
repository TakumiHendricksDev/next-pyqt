from jinja2 import Environment, FileSystemLoader

from component import NextPyComponent


class NextPyTemplate:
    """
    A wrapper component for rendering templates with Jinja2 templates
    """
    def __init__(self, template_dir="."):
        self.env = Environment(loader=FileSystemLoader(template_dir))  # Load templates from the current directory

    def render_template(self, template_path, component: NextPyComponent):
        try:
            template = self.env.get_template(template_path)
            return template.render(
                state=component.state,
                computed={k: v() for k, v in component.computed.items()},
                methods=component.methods,
                props=component.props,
            )
        except Exception as e:
            raise e