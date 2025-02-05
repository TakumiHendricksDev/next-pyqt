from PyQt6.QtWidgets import QApplication
import sys

from HTMLRenderer import HTMLRenderer

def read_html_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    except FileNotFoundError:
        return """
        <html>
        <body>
            <label style="color: red;">Error: Could not find HTML file at {}</label>
        </body>
        </html>
        """.format(file_path)
    except Exception as e:
        return """
        <html>
        <body>
            <label style="color: red;">Error reading HTML file: {}</label>
        </body>
        </html>
        """.format(str(e))


if __name__ == "__main__":
    # Read HTML from file
    html_content = read_html_file('app.html')

    app = QApplication(sys.argv)
    window = HTMLRenderer(html_content)
    window.show()
    sys.exit(app.exec())