# main.py
from PyQt6.QtWidgets import QApplication
import sys
from html_renderer import NextPyHTMLRenderer
from app import App
from template_engine import JinjaTemplate

if __name__ == "__main__":
    # Process HTML
    template = JinjaTemplate()
    app = App(template_engine=template)

    # Create and show the application
    q_app = QApplication(sys.argv)

    window = NextPyHTMLRenderer(app)

    # Link App to NextPyHTMLRenderer
    app.set_renderer(window)

    window.show()

    sys.exit(q_app.exec())