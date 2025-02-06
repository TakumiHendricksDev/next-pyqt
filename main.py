# main.py
from PyQt6.QtWidgets import QApplication
import sys
from HTMLRenderer import HTMLRenderer
from app import App
from components import ComponentLoader
from template_engine import HTMLTemplate


if __name__ == "__main__":
    # Initialize component loader
    # component_loader = ComponentLoader()
    #
    # # Read main HTML file
    # main_html = read_html_file('app.html')

    # Process components
    # processed_html = component_loader.replace_components(main_html)

    # Process HTML
    app = App()
    template = HTMLTemplate(app)

    # Create and show the application
    q_app = QApplication(sys.argv)

    window = HTMLRenderer(template)

    # Link App to HTMLRenderer
    app.set_renderer(window)

    window.show()

    sys.exit(q_app.exec())