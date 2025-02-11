# elements.py
from PyQt6.QtCore import QTimer, Qt
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QLineEdit, QCheckBox
)
from PyQt6.QtGui import QFont, QPalette
import re

from utils import is_value_true
import logging


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
        if hasattr(self.element, 'style'):
            self.apply_styles(self.element.get('style'))

        return self.widget

    @staticmethod
    def parse_method_call(method_call: str):
        match = re.match(r'(\w+)\((.*?)\)', method_call)
        if match:
            method_name = match.group(1)
            params = match.group(2).split(',') if match.group(2) else []
            params = [param.strip() for param in params]  # Remove extra spaces
            return method_name, params
        return None, None

    def apply_styles(self, styles):
        """Apply styles to the widget"""
        if not self.widget:
            return

        if styles is None:
            return

        style_dict = {}

        styles = styles.split(';')
        for style in styles:
            if style:
                key, value = style.split(':')
                style_dict[key.strip()] = value.strip()

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

        return super().create_widget()

    def attach_callback(self, methods):
        if self.callback_name and self.callback_name in methods:
            self.add_listener(methods[self.callback_name])
        else:
            logging.error(f"Button element callback method {methods} not found in methods list")

    def _on_click(self, params):
        for listener in self.listeners:
            listener(*params)


class NextPyLabelElement(NextPyElement):
    def create_widget(self):
        text = self.element.text.strip() if self.element.text else ""
        self.widget = QLabel(text)
        self.widget.setFont(QFont("Arial", 12))
        return super().create_widget()


class NextPyInputElement(NextPyElement):
    def create_widget(self):
        self.widget = QLineEdit()
        self.palette = QPalette()

        self.widget.setPalette(self.palette)

        try:
            # get the func name of the callback
            self.callback_name = self.element.get("on_change")
        except AttributeError as e:
            raise ValueError(
                f"{self.__class__.__name__} element is missing required attribute. "
                f"Expected 'on_click', got: {self.element.attrs}"
            ) from e

        if self.element.get('value'):
            self.widget.setText(self.element.get('value'))

        if self.element.get('placeholder'):
            self.widget.setPlaceholderText(self.element.get('placeholder'))

        self.widget.textChanged.connect(lambda x: self._on_value_changed(x))

        return super().create_widget()

    def _on_value_changed(self, value):
        for listener in self.listeners:
            listener(value)

    def attach_callback(self, methods):
        if self.callback_name and self.callback_name in methods:
            self.add_listener(methods[self.callback_name])
        else:
            logging.error(f"Button element callback method {methods} not found in methods list")


class NextPyDivElement(NextPyElement):
    ALIGNMENT_TYPES = {
        "left": Qt.AlignmentFlag.AlignLeft,
        "right": Qt.AlignmentFlag.AlignRight,
        "center": Qt.AlignmentFlag.AlignCenter,
        "top": Qt.AlignmentFlag.AlignTop,
        "bottom": Qt.AlignmentFlag.AlignBottom,
    }
    MARGIN_LEFT = "margin-left"
    MARGIN_RIGHT = "margin-right"
    MARGIN_TOP = "margin-top"
    MARGIN_BOTTOM = "margin-bottom"

    def create_widget(self):
        self.widget = QWidget()

        layout = self._assign_container_attributes()

        self.widget.setLayout(layout)

        return super().create_widget()

    def add_child(self, child_widget):
        if self.widget:
            self.widget.layout().addWidget(child_widget)

    def _assign_container_attributes(self):
        # Determine layout direction
        if self.element.get('class') and 'horizontal' in self.element.get('class'):
            layout = QHBoxLayout()
        else:
            layout = QVBoxLayout()


        # Get margin on object
        # e.g. <qwidget margin-left='20' > ... </qwidget>
        margin = self.element.get('margin') or 0 # defaults to margin unless overwritten
        margin_left = self.element.get(self.MARGIN_LEFT) or margin
        margin_top = self.element.get(self.MARGIN_TOP) or margin
        margin_right = self.element.get(self.MARGIN_RIGHT) or margin
        margin_bottom = self.element.get(self.MARGIN_BOTTOM) or margin
        try:
            # Cast to int as we are grabbing it from html
            layout.setContentsMargins(int(margin_left), int(margin_top), int(margin_right), int(margin_bottom))
        except TypeError:
            logging.error(f"Bad margins {margin_left, margin_top, margin_right, margin_bottom}")


        # Check if a 'spacing' attribute is defined in the HTML
        # <QWidget spacing='20' />
        spacing = self.element.get('spacing')
        if spacing is not None:
            try:
                layout.setSpacing(int(spacing))
            except ValueError:
                logging.error(f"Button element spacing {spacing} not an integer")

        # get alignment type
        # <QWidget alignment='top' />
        alignment = self.element.get('alignment')
        if alignment is not None and alignment in self.ALIGNMENT_TYPES:
            try:
                layout.setAlignment(self.ALIGNMENT_TYPES[alignment])
            except Exception as e:
                logging.error(e)
        else:
            layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        return layout

class NextPyCheckboxElement(NextPyElement):
    def create_widget(self):
        self.widget = QCheckBox()

        try:
            # get the func name of the callback
            self.callback_name, self.callback_params = self.parse_method_call(self.element.get("on_checked"))
        except AttributeError:
            raise ValueError("Button element must have a 'on_checked' attribute")

        if self.element.get("checked"):
            self.widget.setChecked(is_value_true(self.element.get("checked")))

        self.widget.clicked.connect(lambda: self._on_checked(self.callback_params))

        return super().create_widget()

    def attach_callback(self, methods):
        if self.callback_name and self.callback_name in methods:
            self.add_listener(methods[self.callback_name])
        else:
            logging.error(f"Button element callback method {methods} not found in methods list")

    def _on_checked(self, params):
        for listener in self.listeners:
            listener(*params)