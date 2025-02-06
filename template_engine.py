from bs4 import BeautifulSoup
from jinja2 import Environment, FileSystemLoader
from pydantic import BaseModel, ValidationError


class NextPyProps(BaseModel):
    """Base class for defining component props."""
    pass

class NextPyComponent:
    """
    Class representing a NextPyComponent
    """
    props_schema = None

    def __init__(self, template_path=None, template_engine=None, **kwargs):
        self.template_path = template_path
        self.template_engine = template_engine

        self.state = {}
        self.computed = {}
        self.methods = {}
        self.components = {}

        """
            'ref_name': 'reference variable'
        """
        self.refs = {}

        """
            'prop_name': {}
        """
        self.props = {}
        self.build_props(**kwargs)

        self.renderer = None

    def build_props(self, **kwargs):
        """Validates props using Pydantic model."""
        if self.props_schema:
            try:
                validated_props = self.props_schema(**kwargs)
                self.props = validated_props.dict()
            except ValidationError as e:
                raise TypeError(f"Invalid props: {e}")

    def setState(self, new_state):
        """Set state for components and rerender."""
        self.state.update(new_state)
        self.rerender()

    def add_computed(self, name, func):
        """Add a computed property."""
        self.computed[name] = func

    def add_method(self, name, func):
        """Add a method property."""
        self.methods[name] = func

    def set_renderer(self, window):
        """Set the renderer."""
        self.renderer = window

    def render(self):
        """Renders the component, replacing component tags with actual rendered HTML from registered components."""
        if not (self.template_engine and self.template_path):
            return "Error: No template engine or template set"

        # Render the base template
        rendered_html = self.template_engine.render_template(self.template_path, self)

        # Process and replace components
        return self._process_components(rendered_html)

    def _process_components(self, html):
        """Uses BeautifulSoup to find and replace component tags with rendered HTML."""
        soup = BeautifulSoup(html, 'html.parser')

        # Find all <component> tags
        for component_tag in soup.find_all("component"):
            # get required attributes on element
            component_name = component_tag.get("name")

            # get props:


            if component_name in self.components:
                # Create an instance of the component and render it
                component_class = self.components[component_name]

                # get props if it exists
                prop_data = {attr: component_tag.get(attr) for attr in component_class.props_schema.__annotations__.keys()}

                component_instance = component_class(template_engine=self.template_engine, **prop_data)

                # get ref name if it exists
                ref = component_tag.get("ref", None)
                if ref is not None:
                    self.refs[ref] = component_instance

                rendered_component = component_instance.render()

                # Replace the component tag with the rendered HTML
                new_soup = BeautifulSoup(rendered_component, 'html.parser')
                component_tag.replace_with(new_soup)
            else:
                # If the component is not found, replace with an error comment
                component_tag.replace_with(soup.new_string(f"<!-- Error: Component '{component_name}' not found -->"))

        return str(soup)

    def rerender(self):
        """ Triggers a re-render if the renderer exists. """
        if self.renderer:
            self.renderer.rerender()


class NextPyTemplate:
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
            raise f"Error: {str(e)}"