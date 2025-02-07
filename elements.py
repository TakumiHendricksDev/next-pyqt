# elements.py
from PyQt6.QtCore import QTimer
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QLineEdit, QGroupBox, QCheckBox
)
from PyQt6.QtGui import QFont
import re


class NextPyElement:
    def __init__(self, element):
        self.element = element
        self.listeners = []
        self.widget = None

    def add_listener(self, listener):
        self.listeners.append(listener)

    def attach_callback(self, methods):
        pass

    def create_widget(self):
        raise NotImplementedError()

    @staticmethod
    def parse_method_call(method_call: str):
        match = re.match(r'(\w+)\((.*?)\)', method_call)
        if match:
            method_name = match.group(1)
            params = match.group(2).split(',') if match.group(2) else []
            params = [param.strip() for param in params]  # Remove extra spaces
            return method_name, params
        return None, None

    def apply_styles(self, style_dict):
        """Apply styles to the widget"""
        if not self.widget:
            return

        stylesheet_parts = []
        for key, value in style_dict.items():
            stylesheet_parts.append(f"{key}: {value};")

            # if key == 'background-color':
            #     stylesheet_parts.append(f"background-color: {value};")
            # elif key == 'color':
            #     stylesheet_parts.append(f"color: {value};")
            # elif key == 'font-size':
            #     if value.endswith('px'):
            #         value = f"{int(value[:-2])}pt"
            #     stylesheet_parts.append(f"font-size: {value};")
            # elif key == 'padding':
            #     stylesheet_parts.append(f"padding: {value};")
            # elif key == 'margin':
            #     stylesheet_parts.append(f"margin: {value};")
            # elif key == 'border':
            #     stylesheet_parts.append(f"border: {value};")
            # elif key == 'border-radius':
            #     stylesheet_parts.append(f"border-radius: {value};")
            # elif key == 'font-weight' and value == 'bold':
            #     stylesheet_parts.append("font-weight: bold;")

        if stylesheet_parts:
            self.widget.setStyleSheet(' '.join(stylesheet_parts))


class NextPyButtonElement(NextPyElement):
    def create_widget(self):
        self.widget = QPushButton(self.element.get_text(strip=True) or "Button")

        try:
            # get the func name of the callback
            self.callback_name, self.callback_params = self.parse_method_call(self.element.get("on_click"))
        except AttributeError:
            raise ValueError("Button element must have a 'on_click' attribute")

        self.widget.clicked.connect(lambda: self._on_click(self.callback_params))

        return self.widget

    def attach_callback(self, methods):
        if self.callback_name and self.callback_name in methods:
            self.add_listener(methods[self.callback_name])
        else:
            print(f"Callback {self.callback_name} not found in methods")  # Debug

    def _on_click(self, params):
        for listener in self.listeners:
            listener(*params)


class NextPyLabelElement(NextPyElement):
    def create_widget(self):
        text = self.element.text.strip() if self.element.text else ""
        self.widget = QLabel(text)
        self.widget.setFont(QFont("Arial", 12))
        return self.widget


class NextPyInputElement(NextPyElement):
    def create_widget(self):
        self.widget = QLineEdit()
        if self.element.get('value'):
            self.widget.setText(self.element.get('value'))

        try:
            # get the func name of the callback
            self.callback_name = self.element.get("on_change")
        except AttributeError:
            raise ValueError("Button element must have a 'on_click' attribute")

        self.widget.textChanged.connect(lambda x: self._on_value_changed(x))

        return self.widget

    def _on_value_changed(self, value):
        for listener in self.listeners:
            listener(value)

    def attach_callback(self, methods):
        if self.callback_name and self.callback_name in methods:
            self.add_listener(methods[self.callback_name])
        else:
            print(f"Callback {self.callback_name} not found in methods")  # Debug


class NextPyDivElement(NextPyElement):
    def create_widget(self):
        self.widget = QWidget()

        # Determine layout direction
        if self.element.get('class') and 'horizontal' in self.element.get('class'):
            layout = QHBoxLayout()
        else:
            layout = QVBoxLayout()

        self.widget.setLayout(layout)

        return self.widget

    def add_child(self, child_widget):
        if self.widget:
            self.widget.layout().addWidget(child_widget)

class NextPyComponentElement(NextPyElement):
    def create_widget(self):
        self.widget = QGroupBox()
        return self.widget

class NextPyCheckboxElement(NextPyElement):
    def create_widget(self):
        self.widget = QCheckBox()
        return self.widget