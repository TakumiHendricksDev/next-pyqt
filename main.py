# main.py
from PyQt6.QtWidgets import QApplication
import sys
from HTMLRenderer import HTMLRenderer
from app import App
from components import ComponentLoader
from template_engine import JinjaTemplate

if __name__ == "__main__":
    # Process HTML
    template = JinjaTemplate()
    app = App(template_engine=template)

    # Create and show the application
    q_app = QApplication(sys.argv)

    window = HTMLRenderer(app)

    # Link App to HTMLRenderer
    app.set_renderer(window)

    window.show()

    sys.exit(q_app.exec())