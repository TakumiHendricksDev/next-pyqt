from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QLineEdit
)
from PyQt6.QtGui import QFont, QColor
from bs4 import BeautifulSoup
import re


class HTMLRenderer(QWidget):
    def __init__(self, html_content):
        super().__init__()

        # Set up the window
        self.setWindowTitle("PyQt Framework Demo")
        self.setGeometry(100, 100, 400, 300)

        # Initialize styles dictionary
        self.styles = {}

        # Create main layout
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        # Render the HTML
        self.render_html(html_content)

    def render_html(self, html_content):
        try:
            soup = BeautifulSoup(html_content, "html.parser")

            # Process styles first
            self._process_styles(soup)

            body = soup.find('body')
            if body:
                for element in body.children:
                    if element.name:  # Skip empty text nodes
                        widget = self.create_widget(element)
                        if widget:
                            self.layout.addWidget(widget)
        except Exception as e:
            error_label = QLabel(f"Error rendering HTML: {str(e)}")
            error_label.setStyleSheet("color: red;")
            self.layout.addWidget(error_label)

    def _process_styles(self, soup):
        # Find all style tags
        style_tags = soup.find_all('style')
        for style_tag in style_tags:
            if style_tag.string:
                # Parse CSS rules
                rules = re.findall(r'([^{]+){([^}]+)}', style_tag.string)
                for selector, properties in rules:
                    selector = selector.strip()
                    # Parse properties into dictionary
                    prop_dict = {}
                    for prop in properties.split(';'):
                        if ':' in prop:
                            key, value = prop.split(':')
                            prop_dict[key.strip()] = value.strip()
                    self.styles[selector] = prop_dict

    def _apply_styles(self, widget, element):
        style_rules = {}

        # Apply CSS styles based on element type
        if element.name in self.styles:
            style_rules.update(self.styles[element.name])

        # Apply CSS styles based on class
        if element.get('class'):
            for class_name in element.get('class'):
                class_selector = f'.{class_name}'
                if class_selector in self.styles:
                    style_rules.update(self.styles[class_selector])

        # Apply CSS styles based on ID
        if element.get('id'):
            id_selector = f'#{element.get("id")}'
            if id_selector in self.styles:
                style_rules.update(self.styles[id_selector])

        # Apply inline styles (these take precedence)
        if element.get('style'):
            inline_styles = {}
            for prop in element.get('style').split(';'):
                if ':' in prop:
                    key, value = prop.split(':')
                    inline_styles[key.strip()] = value.strip()
            style_rules.update(inline_styles)

        # Convert style rules to Qt stylesheet
        if style_rules:
            stylesheet_parts = []
            for key, value in style_rules.items():
                if key == 'background-color':
                    stylesheet_parts.append(f"background-color: {value};")
                elif key == 'color':
                    stylesheet_parts.append(f"color: {value};")
                elif key == 'font-size':
                    # Convert px to pt if needed
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
                widget.setStyleSheet(' '.join(stylesheet_parts))

    def create_widget(self, element):
        widget = None

        if element.name == "button":
            widget = QPushButton(element.text.strip() if element.text else "Button")

        elif element.name == "label":
            widget = QLabel(element.text.strip() if element.text else "")
            widget.setFont(QFont("Arial", 12))

        elif element.name == "input":
            widget = QLineEdit()
            if element.get('value'):
                widget.setText(element.get('value'))

        elif element.name == "div":
            widget = QWidget()
            container_layout = QVBoxLayout()
            widget.setLayout(container_layout)

            # Handle horizontal layout
            if element.get('class') and 'horizontal' in element.get('class'):
                container_layout = QHBoxLayout()
                widget.setLayout(container_layout)

            for child in element.children:
                if child.name:
                    child_widget = self.create_widget(child)
                    if child_widget:
                        container_layout.addWidget(child_widget)

        # Apply styles to the widget if it was created
        if widget:
            self._apply_styles(widget, element)

        return widget