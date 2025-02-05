# components.py
import os
from bs4 import BeautifulSoup


class ComponentLoader:
    def __init__(self, components_dir="components"):
        self.components_dir = components_dir
        self.components = {}
        self.load_components()

    def load_components(self):
        """Load all HTML components from the components directory"""
        if not os.path.exists(self.components_dir):
            os.makedirs(self.components_dir)

        for filename in os.listdir(self.components_dir):
            if filename.endswith('.html'):
                component_name = filename[:-5]  # Remove .html extension
                filepath = os.path.join(self.components_dir, filename)
                with open(filepath, 'r', encoding='utf-8') as file:
                    self.components[component_name] = file.read()

    def get_component(self, name):
        """Get a component by name"""
        return self.components.get(name, "")

    def replace_components(self, html_content):
        """Replace component tags with actual component content"""
        soup = BeautifulSoup(html_content, 'html.parser')

        # Find all component includes
        component_tags = soup.find_all('component')

        for comp_tag in component_tags:
            name = comp_tag.get('name')
            if name in self.components:
                # Parse the component HTML
                component_html = self.components[name]
                component_soup = BeautifulSoup(component_html, 'html.parser')

                # Get the content from inside the body tag
                component_content = component_soup.body.contents if component_soup.body else []

                # Replace the component tag with the component content
                comp_tag.replace_with(*component_content)

        return str(soup)