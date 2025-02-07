# NextPyHTMLRenderer.py
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
from bs4 import BeautifulSoup
import re
from elements import (
    NextPyButtonElement, NextPyLabelElement,
    NextPyInputElement, NextPyDivElement, NextPyComponentElement, NextPyCheckboxElement
)


class NextPyHTMLRenderer(QWidget):
    def __init__(self, component):
        super().__init__()

        # Set up the window
        self.setWindowTitle("PyQt Framework Demo")
        self.setGeometry(100, 100, 400, 300)

        # Initialize styles dictionary
        self.styles = {}

        # Element mapping
        self.element_classes = {
            'qpushbutton': NextPyButtonElement,
            'qlabel': NextPyLabelElement,
            'qlineedit': NextPyInputElement,
            'qwidget': NextPyDivElement,
            'qcheckbox': NextPyCheckboxElement,

            'component': NextPyComponentElement,
        }

        # Create main layout
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.component = component

        # Render the HTML
        self.render_html(component.render())

    def rerender(self):
        self.render_html(self.component.render())

    def render_html(self, html_content):
        try:
            # Clear the existing layout before re-rendering
            while self.layout.count():
                item = self.layout.takeAt(0)
                if item.widget():
                    item.widget().deleteLater()

            soup = BeautifulSoup(html_content, "html.parser")
            self._process_styles(soup)

            for element in soup.find_all(recursive=False):
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

        """
        
        We have a widget but we need to know what listeners to add to the method
        
        If it is a button we need to call the button attached to the on_click func
        If it is an input element we need to call the listener function for the state of that input
            
        """
        methods = self.component.methods
        html_element.attach_callback(methods)

        # Apply styles
        self._apply_element_styles(html_element, element)

        # Handle children for container elements
        if isinstance(html_element, NextPyDivElement):
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