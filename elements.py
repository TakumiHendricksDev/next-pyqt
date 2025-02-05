# elements.py
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QLineEdit
)
from PyQt6.QtGui import QFont


class HTMLElement:
    def __init__(self, element):
        self.element = element
        self.widget = None

    def create_widget(self):
        """Create and return the PyQt widget"""
        raise NotImplementedError

    def apply_styles(self, style_dict):
        """Apply styles to the widget"""
        if not self.widget:
            return

        stylesheet_parts = []
        for key, value in style_dict.items():
            if key == 'background-color':
                stylesheet_parts.append(f"background-color: {value};")
            elif key == 'color':
                stylesheet_parts.append(f"color: {value};")
            elif key == 'font-size':
                if value.endswith('px'):
                    value = f"{int(value[:-2])}pt"
                stylesheet_parts.append(f"font-size: {value};")
            elif key == 'padding':
                stylesheet_parts.append(f"padding: {value};")
            elif key == 'margin':
                stylesheet_parts.append(f"margin: {value};")
            elif key == 'border':
                stylesheet_parts.append(f"border: {value};")
            elif key == 'border-radius':
                stylesheet_parts.append(f"border-radius: {value};")
            elif key == 'font-weight' and value == 'bold':
                stylesheet_parts.append("font-weight: bold;")

        if stylesheet_parts:
            self.widget.setStyleSheet(' '.join(stylesheet_parts))


class ButtonElement(HTMLElement):
    def create_widget(self):
        text = self.element.text.strip() if self.element.text else "Button"
        self.widget = QPushButton(text)
        return self.widget


class LabelElement(HTMLElement):
    def create_widget(self):
        text = self.element.text.strip() if self.element.text else ""
        self.widget = QLabel(text)
        self.widget.setFont(QFont("Arial", 12))
        return self.widget


class InputElement(HTMLElement):
    def create_widget(self):
        self.widget = QLineEdit()
        if self.element.get('value'):
            self.widget.setText(self.element.get('value'))
        return self.widget


class DivElement(HTMLElement):
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