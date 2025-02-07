from bs4 import BeautifulSoup
from PyQt6.QtWidgets import QWidget, QVBoxLayout
from typing import Dict, Any, Optional, List
from dataclasses import dataclass

from jinja2 import Environment, FileSystemLoader

from elements import (
    NextPyButtonElement, NextPyLabelElement,
    NextPyInputElement, NextPyDivElement,
    NextPyCheckboxElement, NextPyComponentElement
)


@dataclass
class ElementState:
    """Represents the state of an element for comparison"""
    element_type: str
    attributes: Dict[str, str]
    content: str
    children: List['ElementState']
    element: dict


class NextPyComponent:
    def __init__(self, template_path=None, template_engine=None, props=None, parent_component=None, **kwargs):
        self.template_path = template_path
        self.template_engine = template_engine
        self._state = {}
        self.computed = {}
        self.methods = {}
        self.components = {}
        self.refs = {}
        self.emits = []
        self.props = props or {}
        self.element_instances = {}  # Store element instances by ID

        # Element mapping
        self.element_classes = {
            'qpushbutton': NextPyButtonElement,
            'qlabel': NextPyLabelElement,
            'qlineedit': NextPyInputElement,
            'qwidget': NextPyDivElement,
            'qcheckbox': NextPyCheckboxElement,
            'component': NextPyComponentElement,
        }

        self.main_widget = None
        self.parent_component = parent_component
        self.child_components = {}  # Store child component instances
        self.window = None

    def set_window(self, window):
        """Set the window reference for this component"""
        self.window = window

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, value):
        old_state = self._state.copy()
        self._state = value
        self._handle_state_change(old_state, self._state)

    def setState(self, new_state: Dict[str, Any], rerender=True):
        """
        Set the state of this component
        :param new_state: the new state to set
        :param rerender: if rerender is False, will not rerender state
        :return:
        """
        old_state = self._state.copy()
        self._state.update(new_state)

        if rerender is True:
            self._handle_state_change(old_state, self._state)

    def _handle_state_change(self, old_state: Dict[str, Any], new_state: Dict[str, Any]):
        """Handle state changes and trigger selective updates"""
        changed_keys = set()
        for key in set(old_state.keys()) | set(new_state.keys()):
            if old_state.get(key) != new_state.get(key):
                changed_keys.add(key)

        if changed_keys:
            self.rerender_component(changed_keys)

    def create_element(self, element_data) -> Optional[QWidget]:
        """Create an element instance based on element data"""
        if not element_data or not hasattr(element_data, 'element_type'):
            return None

        element_type = element_data.name.lower()  # Normalize element type
        element_class = self.element_classes.get(element_type)

        if not element_class:
            print(f"Warning: Unknown element type '{element_type}'")  # Debug
            return None

        # Handle component elements
        if element_type == 'component':
            return self._create_component_element(element_data)

        # Create element instance
        element_instance = element_class(element_data)

        # Store reference if ID exists
        element_id = element_data.get('id', None)
        if element_id:
            self.element_instances[element_id] = element_instance

        # Create and return widget
        widget = element_instance.create_widget()

        # Attach component methods as callbacks
        element_instance.attach_callback(self.methods)

        # Handle children for container elements
        if isinstance(element_instance, NextPyDivElement):
            for child in element_data.children:
                if child.name:  # Skip text nodes
                    child_widget = self.create_element(child)
                    if child_widget:
                        element_instance.add_child(child_widget)

        return widget

    def _create_component_element(self, element_data) -> Optional[QWidget]:
        """Create a child component instance"""
        component_name = element_data.get('name')
        if component_name not in self.components:
            return None

        # Get component class and create instance
        component_class = self.components[component_name]
        props = {
            attr: element_data.get(attr)
            for attr in getattr(component_class, 'props_schema', {}).__annotations__.keys()
        }

        # Create component instance
        component_instance = component_class(
            template_engine=self.template_engine,
            parent_component=self,
            props=props,
        )

        # Store reference if specified
        ref = element_data.get('ref')
        if ref:
            self.refs[ref] = component_instance

        # Store child component
        component_id = element_data.get('id', component_name)
        self.child_components[component_id] = component_instance

        # Render the component
        return component_instance.render()

    def render(self) -> QWidget:
        """Render the component and return its widget"""
        if not (self.template_engine and self.template_path):
            return QWidget()

        # Create main widget if it doesn't exist
        if not self.main_widget:
            self.main_widget = QWidget()
            self.main_widget.setLayout(QVBoxLayout())

        # Render template
        html_content = self.template_engine.render_template(
            self.template_path,
            component=self
        )

        # Parse HTML and update widget tree
        self._update_from_html(html_content)

        return self.main_widget

    def _update_from_html(self, html_content: str):
        """Update widget tree from HTML content"""
        soup = BeautifulSoup(html_content, 'html.parser')

        # Get the first real element (skip document node)
        root_element = next(
            (element for element in soup.children
             if element.name is not None),
            None
        )

        if not root_element:
            return

        # Get current and new element states
        current_state = self._get_element_state(self.main_widget) if self.main_widget else None
        new_state = self._get_element_state_from_soup(root_element)

        # Update widget tree
        self.main_widget = self._update_element_tree(self.main_widget, current_state, new_state)

    def _get_element_state(self, widget: QWidget) -> ElementState:
        """Get element state from widget"""
        if not widget:
            return None

        element_instance = next(
            (inst for inst in self.element_instances.values()
             if inst.widget == widget),
            None
        )

        if not element_instance:
            return None

        return ElementState(
            element_type=type(element_instance).__name__,
            attributes=self._get_element_attributes(element_instance),
            content=self._get_element_content(element_instance),
            element=element_instance,
            children=self._get_child_states(widget)
        )

    def _get_element_state_from_soup(self, element) -> Optional[ElementState]:
        """Get element state from BeautifulSoup element"""
        if not element or not element.name:
            return None

        # Get all non-empty child elements
        children = [
            child for child in element.children
            if child.name is not None
        ]

        return ElementState(
            element_type=element.name,
            attributes=element.attrs,
            element=element,
            content=element.string if element.string else '',
            children=[
                self._get_element_state_from_soup(child)
                for child in children
            ]
        )

    def _update_element_tree(self, widget: QWidget, current_state: ElementState, new_state: ElementState):
        """Update widget tree based on element states"""
        if not current_state or current_state.element_type != new_state.element_type:
            # Replace entire widget
            new_widget = self.create_element(new_state.element)
            if widget and widget.parent():
                layout = widget.parent().layout()
                layout.replaceWidget(widget, new_widget)
                widget.deleteLater()
            return new_widget

        # Update attributes and content
        element_instance = next(
            (inst for inst in self.element_instances.values()
             if inst.widget == widget),
            None
        )
        if element_instance:
            self._update_element_attributes(element_instance, new_state.attributes)
            self._update_element_content(element_instance, new_state.content)

        # Update children
        if isinstance(element_instance, NextPyDivElement):
            self._update_children(widget, current_state.children, new_state.children)

        return widget

    def rerender_component(self, changed_keys: Optional[set] = None):
        """Rerender component, optionally based on changed state keys"""
        if not self.main_widget:
            return

        # If this is the root component, tell the window to rerender
        if self.window:
            self.window.rerender()

        # If this is a child component, update through the parent
        elif self.parent_component:
            self.parent_component._child_updated(self)

        # Get new content and update widget tree
        html_content = self.template_engine.render_template(
            self.template_path,
            component=self
        )
        self._update_from_html(html_content)

    def _child_updated(self, child_component):
        """Handle updates from child components"""
        # Implement if needed - could trigger partial parent update
        pass


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
            raise e