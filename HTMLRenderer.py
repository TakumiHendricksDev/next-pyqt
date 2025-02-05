# HTMLRenderer.py
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
from bs4 import BeautifulSoup
import re
from elements import (
    ButtonElement, LabelElement,
    InputElement, DivElement
)


class HTMLRenderer(QWidget):
    def __init__(self, html_content):
        super().__init__()

        # Set up the window
        self.setWindowTitle("PyQt Framework Demo")
        self.setGeometry(100, 100, 400, 300)

        # Initialize styles dictionary
        self.styles = {}

        # Element mapping
        self.element_classes = {
            'button': ButtonElement,
            'label': LabelElement,
            'input': InputElement,
            'div': DivElement
        }

        # Create main layout
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        # Render the HTML
        self.render_html(html_content)

    def render_html(self, html_content):
        try:
            soup = BeautifulSoup(html_content, "html.parser")
            self._process_styles(soup)

            body = soup.find('body')
            if body:
                for element in body.children:
                    if element.name:
                        widget = self.create_element(element)
                        if widget:
                            self.layout.addWidget(widget)
        except Exception as e:
            error_label = QLabel(f"Error rendering HTML: {str(e)}")
            error_label.setStyleSheet("color: red;")
            self.layout.addWidget(error_label)

    def _process_styles(self, soup):
        style_tags = soup.find_all('style')
        for style_tag in style_tags:
            if style_tag.string:
                rules = re.findall(r'([^{]+){([^}]+)}', style_tag.string)
                for selector, properties in rules:
                    selector = selector.strip()
                    prop_dict = {}
                    for prop in properties.split(';'):
                        if ':' in prop:
                            key, value = prop.split(':')
                            prop_dict[key.strip()] = value.strip()
                    self.styles[selector] = prop_dict

    def create_element(self, element):
        # Get the appropriate element class
        element_class = self.element_classes.get(element.name)
        if not element_class:
            return None

        # Create the element
        html_element = element_class(element)
        widget = html_element.create_widget()

        # Apply styles
        self._apply_element_styles(html_element, element)

        # Handle children for container elements
        if isinstance(html_element, DivElement):
            for child in element.children:
                if child.name:
                    child_widget = self.create_element(child)
                    if child_widget:
                        html_element.add_child(child_widget)

        return widget

    def _apply_element_styles(self, html_element, element):
        style_rules = {}

        # Element type styles
        if element.name in self.styles:
            style_rules.update(self.styles[element.name])

        # Class styles
        if element.get('class'):
            for class_name in element.get('class'):
                class_selector = f'.{class_name}'
                if class_selector in self.styles:
                    style_rules.update(self.styles[class_selector])

        # ID styles
        if element.get('id'):
            id_selector = f'#{element.get("id")}'
            if id_selector in self.styles:
                style_rules.update(self.styles[id_selector])

        # Inline styles
        if element.get('style'):
            inline_styles = {}
            for prop in element.get('style').split(';'):
                if ':' in prop:
                    key, value = prop.split(':')
                    inline_styles[key.strip()] = value.strip()
            style_rules.update(inline_styles)

        html_element.apply_styles(style_rules)