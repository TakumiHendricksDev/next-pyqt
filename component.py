from typing import Dict, Any

from elements import NextPyButtonElement, NextPyLabelElement, NextPyInputElement, NextPyDivElement, \
    NextPyCheckboxElement
from renderer import NextPyRenderer


class NextPyComponent(NextPyRenderer):
    def __init__(self, template_path=None, template_engine=None, props=None, parent_component=None, events=None, main_widget=None, **kwargs):
        """
        Constructor for NextPyComponent
        :param template_path: the path of the html template
        :param template_engine: the engine of the html template. This allows to override the default engine of the html template
        :param props: the props of the component.
        :param parent_component: the parent component of the component.
        :param events: the events of the component.
        :param main_widget: A reference to the main widget of the component.
        :param kwargs: any other keyword arguments are passed to the parent component.
        """
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

        self.main_widget = main_widget
        self.parent_component = parent_component
        self.child_components = {}  # Store child component instances
        self.window = None

    def set_window(self, window):
        """
        Set the window reference for this component
        :param window: window reference
        :return: void
        """
        self.window = window

    @property
    def state(self):
        """
        Returns the current state of this component
        :return: state object
        """
        return self._state

    @state.setter
    def state(self, value):
        """
        Set the state of this component
        :param value:
        :return:
        """
        old_state = self._state.copy()
        self._state = value
        self._handle_state_change(old_state, self._state)

    def set_state(self, new_state: Dict[str, Any], rerender=True):
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

    def component_did_mount(self) -> None:
        """
        Mount this component
        :return: void
        """
        pass

    def component_did_unmount(self) -> None:
        """
        Unmount this component
        :return: void
        """
        pass