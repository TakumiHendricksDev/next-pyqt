# main.py
from PyQt6.QtWidgets import QApplication
import sys
from HTMLRenderer import HTMLRenderer
from components import ComponentLoader

def read_html_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    except FileNotFoundError:
        return f"""
        <html><body>
            <label style="color: red;">Error: Could not find HTML file at {file_path}</label>
        </body></html>
        """


if __name__ == "__main__":
    # Initialize component loader
    component_loader = ComponentLoader()

    # Read main HTML file
    main_html = read_html_file('app.html')

    # Process components
    processed_html = component_loader.replace_components(main_html)

    # Create and show the application
    app = QApplication(sys.argv)
    window = HTMLRenderer(processed_html)
    window.show()
    sys.exit(app.exec())