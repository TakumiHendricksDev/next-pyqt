from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout
from pydantic import BaseModel

from app import TodoApp
from template_engine import NextPyTemplate
from window import NextPyWindow

# Usage example:
if __name__ == "__main__":
    from PyQt6.QtWidgets import QApplication
    import sys

    # Create the application
    app = QApplication(sys.argv)

    # Create root component
    root = TodoApp(
        template_engine=NextPyTemplate("templates"),
        template_path="todo_app.html"
    )

    # Create and show window
    window = NextPyWindow(root, "Todo App")
    window.show()

    # Start the event loop
    sys.exit(app.exec())