import re
from string import Template
import ast
from jinja2 import Environment, FileSystemLoader

class PyComponent:
    def __init__(self, template_path=None, template_engine=None):
        self.template_path = template_path
        self.template_engine = template_engine

        self.state = {}
        self.computed = {}
        self.methods = {}

        self.renderer = None

    def setState(self, new_state):
        self.state.update(new_state)
        self.rerender()
        # Here you would trigger a re-render

    def add_computed(self, name, func):
        self.computed[name] = func

    def add_method(self, name, func):
        self.methods[name] = func

    def set_renderer(self, window):
        self.renderer = window

    def render(self):
        if self.template_engine and self.template_path:
            return self.template_engine.render_template(self.template_path, self)
        return "Error: No template engine or template set"

    def rerender(self):
        """ Triggers a re-render if the renderer exists. """
        if self.renderer:
            self.renderer.rerender()


class JinjaTemplate:
    def __init__(self, template_dir="."):
        self.env = Environment(loader=FileSystemLoader(template_dir))  # Load templates from the current directory

    def render_template(self, template_path, component: PyComponent):
        try:
            template = self.env.get_template(template_path)
            return template.render(
                state=component.state,
                computed={k: v() for k, v in component.computed.items()},
                methods=component.methods
            )
        except Exception as e:
            raise f"Error: {str(e)}"