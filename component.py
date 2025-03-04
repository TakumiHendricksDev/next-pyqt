from typing import Dict, Any

from lifecycle import NextPyComponentLifecycle
from renderer import NextPyRenderer


class NextPyComponent(NextPyComponentLifecycle):
    template_path = None

    def __init__(
        self,
        template_path=None,
        template_engine=None,
        props=None,
        parent_component=None,
        events=None,
        main_widget=None,
        name=None,
        **kwargs,
    ):
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
        self.template_path = template_path or self.template_path
        self._state = {}
        self.name = name
        self.computed = {}
        self.methods = {}
        self.components = {}
        self.refs = {}
        self.emits = []
        self.props = props or {}
        self.mapped_events = events
        self.template_engine = template_engine
        self.window = None

        self.main_widget = main_widget
        self.parent_component = parent_component

        # Initialize the renderer
        self.renderer = NextPyRenderer(
            template_engine=self.template_engine,
            template_path=self.template_path,
            main_widget=main_widget,
            window=self.window,
        )

        self.renderer.methods = self.get_methods
        self.renderer.computed = self.get_computed
        self.renderer.props = self.get_props
        self.renderer.state = self.get_state

        self.renderer.component_did_mount = self.component_did_mount
        self.renderer.components = self.get_components

    def get_methods(self):
        """
        Get the methods of this component
        :return: the methods of this component
        """
        return self.methods

    def get_computed(self):
        """
        Get the computed properties of this component
        :return: the computed properties of this component
        """
        return self.computed

    def get_props(self):
        """
        Get the props of this component
        :return: the props of this component
        """
        return self.props

    def get_state(self):
        """
        Get the state of this component
        :return: the state of this component
        """
        return self.state

    def get_components(self):
        """
        Get the components of this component
        :return: the components of this component
        """
        return self.components

    def set_window(self, window):
        """
        Set the window reference for this component
        :param window: window reference
        :return: void
        """
        self.window = window
        self.renderer.window = self.window

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

    def render(self):
        """
        Render the component
        :return: void
        """
        return self.renderer.render()

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

    def _handle_state_change(
        self, old_state: Dict[str, Any], new_state: Dict[str, Any]
    ):
        """Handle state changes and trigger selective updates"""
        changed_keys = set()
        for key in set(old_state.keys()) | set(new_state.keys()):
            if old_state.get(key) != new_state.get(key):
                changed_keys.add(key)

        if changed_keys:
            self.renderer.rerender_component(changed_keys)

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

    def __str__(self):
        """
        return a string representation of this component
        :return: return the name of the component
        """
        return f"{self.name}"
