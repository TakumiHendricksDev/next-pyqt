from bs4 import BeautifulSoup
from PyQt6.QtWidgets import QWidget, QVBoxLayout
from typing import Dict, Any, Optional, List, get_type_hints
from dataclasses import dataclass

from jinja2 import Environment, FileSystemLoader
from pydantic import BaseModel

from elements import (
    NextPyButtonElement, NextPyLabelElement,
    NextPyInputElement, NextPyDivElement,
    NextPyCheckboxElement
)

import json

from utils import is_value_true, cast_value


@dataclass
class ElementState:
    """Represents the state of an element for comparison"""
    element_type: str
    attributes: Dict[str, str]
    content: str
    children: List['ElementState']
    element: dict


class NextPyComponent:
    def __init__(self, template_path=None, template_engine=None, props=None, parent_component=None, events=None, **kwargs):
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
        self.mapped_events = events

        # Element mapping
        self.element_classes = {
            'qpushbutton': NextPyButtonElement,
            'qlabel': NextPyLabelElement,
            'qlineedit': NextPyInputElement,
            'qwidget': NextPyDivElement,
            'qcheckbox': NextPyCheckboxElement,
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
        :return: void
        """
        old_state = self._state.copy()
        self._state.update(new_state)

        if rerender is True:
            self._handle_state_change(old_state, self._state)

    def emit_event(self, event, *args, **kwargs):
        """
        Emit an event to this component
        :param event: event key
        :return: void
        """
        if event in self.mapped_events:
            self.mapped_events[event](*args, **kwargs)

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

        # Handle component elements
        if element_type == 'component':
            return self._create_component_element(element_data)

        element_class = self.element_classes.get(element_type)

        if not element_class:
            print(f"Warning: Unknown element type '{element_type}'")  # Debug
            return None

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
        props = self.cast_props_from_html(component_class, element_data)

        events = {}
        for event_name in component_class.emits:
            event_call = f"on_{event_name}"
            get_call = element_data.get(event_call)
            if get_call is not None:
                events[event_name] = self.methods.get(get_call, None)

        # Create component instance
        component_instance = component_class(
            template_engine=self.template_engine,
            parent_component=self,
            props=props,
            events=events,
        )

        # Store reference if specified
        ref = element_data.get('ref')
        if ref:
            self.refs[ref] = component_instance

        # Store child component
        component_id = element_data.get('id', component_name)
        self.child_components[component_id] = component_instance

        # Render the component
        component_widget = component_instance.render()

        return component_widget

    def cast_props_from_html(self, component_class, element_data):
        """
        Build and type cast props collection based on component's props schema and HTML data.

        Args:
            component_class: The component class with props_schema
            element_data: Dictionary of raw HTML attribute values

        Returns:
            Dictionary of properly typed props according to schema
        """
        if not hasattr(component_class, 'props_schema'):
            return {}

        schema = component_class.props_schema
        type_hints = get_type_hints(schema)

        props = {}
        for attr, target_type in type_hints.items():
            if hasattr(element_data, attr):
                raw_value = element_data.get(attr)
                props[attr] = cast_value(raw_value, target_type)

        return props


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

    def _update_element_attributes(self, element_instance, new_attributes: dict):
        """
        Update the attributes of a widget element

        Args:
            element_instance: The widget element instance to update
            new_attributes: Dictionary of new attributes to apply
        """
        # Get current attributes
        current_attributes = getattr(element_instance, 'attributes', {})

        # Skip if attributes are identical
        if current_attributes == new_attributes:
            return

        # Update style attributes
        if 'style' in new_attributes:
            stylesheet = self._build_stylesheet(new_attributes['style'])
            element_instance.widget.setStyleSheet(stylesheet)

        # Update enabled state
        if 'disabled' in new_attributes:
            element_instance.widget.setEnabled(not new_attributes['disabled'])

        # Update visibility
        if 'hidden' in new_attributes:
            element_instance.widget.setVisible(not new_attributes['hidden'])

        # Update specific widget type attributes
        widget_type = type(element_instance).__name__

        if widget_type == 'NextPyButtonElement':
            if 'text' in new_attributes:
                element_instance.widget.setText(new_attributes['text'])

        elif widget_type == 'NextPyInputElement':
            if 'placeholder' in new_attributes:
                element_instance.widget.setPlaceholderText(new_attributes['placeholder'])
            if 'value' in new_attributes:
                element_instance.widget.setText(new_attributes['value'])

        elif widget_type == 'NextPyCheckboxElement':
            if 'checked' in new_attributes:
                element_instance.widget.setChecked(new_attributes['checked'])

        # Store new attributes
        element_instance.attributes = new_attributes

    def _update_element_content(self, element_instance, new_content: str):
        """
        Update the content/text of a widget element

        Args:
            element_instance: The widget element instance to update
            new_content: New content string to set
        """
        # Skip if content hasn't changed
        current_content = getattr(element_instance, 'content', '')
        if current_content == new_content:
            return

        # Update based on widget type
        widget_type = type(element_instance).__name__

        if widget_type in ['NextPyButtonElement', 'NextPyLabelElement']:
            element_instance.widget.setText(new_content)
        elif widget_type == 'NextPyInputElement':
            # Only update if the input doesn't have focus to avoid disrupting user typing
            if not element_instance.widget.hasFocus():
                element_instance.widget.setText(new_content)

        # Store new content
        element_instance.content = new_content

    def _update_children(self, parent_widget, current_children: list, new_children: list):
        """
        Update child widgets within a container widget

        Args:
            parent_widget: The parent QWidget containing children
            current_children: List of current child ElementStates
            new_children: List of new child ElementStates
        """
        layout = parent_widget.layout()
        if not layout:
            return

        # Create maps for current and new children using their IDs or content as keys
        current_map = {
            self._get_element_key(child): child
            for child in current_children if child
        }
        new_map = {
            self._get_element_key(child): child
            for child in new_children if child
        }

        # Track processed widgets to handle removals
        processed_widgets = set()

        # Process new children
        for i, new_child in enumerate(new_children):
            if not new_child:
                continue

            key = self._get_element_key(new_child)
            current_child = current_map.get(key)

            if current_child:
                # Update existing child
                widget = layout.itemAt(i).widget() if i < layout.count() else None
                if widget:
                    updated_widget = self._update_element_tree(widget, current_child, new_child)
                    processed_widgets.add(widget)
                    if updated_widget != widget:
                        layout.replaceWidget(widget, updated_widget)
            else:
                # Insert new child
                new_widget = self.create_element(new_child.element)
                if new_widget:
                    layout.insertWidget(i, new_widget)

        # Remove unprocessed widgets (ones that don't exist in new children)
        i = 0
        while i < layout.count():
            widget = layout.itemAt(i).widget()
            if widget and widget not in processed_widgets:
                layout.removeWidget(widget)
                widget.deleteLater()
            else:
                i += 1

    def _get_element_key(self, element_state) -> str:
        """
        Get a unique key for an element state to use in diffing

        Args:
            element_state: ElementState instance

        Returns:
            str: Unique key for the element
        """
        if not element_state:
            return None

        # Try to get ID from attributes
        element_id = element_state.attributes.get('id')
        if element_id:
            return f"id:{element_id}"

        # Fall back to element type + content as key
        return f"{element_state.element_type}:{element_state.content}"

    def _build_stylesheet(self, style_dict: dict) -> str:
        """
        Convert a style dictionary to a Qt stylesheet string

        Args:
            style_dict: Dictionary of style properties

        Returns:
            str: Formatted Qt stylesheet
        """
        if not style_dict:
            return ""

        # Convert style dictionary to Qt stylesheet syntax
        styles = []
        for key, value in style_dict.items():
            # Convert camelCase to kebab-case
            qt_key = ''.join([f'-{c.lower()}' if c.isupper() else c for c in key]).lstrip('-')
            styles.append(f"{qt_key}: {value};")

        return ' '.join(styles)

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