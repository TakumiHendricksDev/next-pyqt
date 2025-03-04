"""main.py"""
from app import TodoApp
from components.hello_world import HelloWorldApp
from router import NextPyRouter
from template_engine import NextPyTemplate
from window import NextPyWindow

def hello_world_component_factory(*kwargs):
    """
    Factory function for creating the HelloWorldApp component
    :param kwargs: kwargs to pass to the component
    :return: A NextPYQT component
    """
    return HelloWorldApp(template_engine=NextPyTemplate("templates"), *kwargs)

def root_component_factory(*kwargs):
    """
    Factory function for creating the TodoApp component
    :param kwargs: kwargs to pass to the component
    :return: A NextPYQT component
    """
    return TodoApp(
        template_engine=NextPyTemplate("templates"),
        *kwargs
    )

# Usage example:
if __name__ == "__main__":
    from PyQt6.QtWidgets import QApplication
    import sys

    # Create the application
    app = QApplication(sys.argv)

    # Create router instance
    router = NextPyRouter()

    router.register_route("todo_app", root_component_factory)
    router.register_route("hello_world", hello_world_component_factory)

    # Create and show window
    window = NextPyWindow(hello_world_component_factory(), router, title="Todo App")
    window.show()

    # Start the event loop
    sys.exit(app.exec())
