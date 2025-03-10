from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPalette, QColor
from PyQt6.QtWidgets import QVBoxLayout, QWidget, QMainWindow


class NextPyWindow(QMainWindow):
    """Main window that hosts the root component"""

    def __init__(self, root_component, router, title="NextPy App", width=800, height=600, background_color="#222222", text_color="#d2d1d0"):
        super().__init__()

        # setup router
        self.router = router

        # Set up the window
        self.setWindowTitle(title)
        self.setGeometry(50, 50, width, height)

        # Create a central widget
        self.central_widget = QWidget(self)  # Create a QWidget
        self.setCentralWidget(self.central_widget)  # Set it as the central widget

        self.palette = QPalette()

        if background_color is not None:
            self.palette.setColor(QPalette.ColorRole.Window, QColor(background_color))
            self.palette.setColor(QPalette.ColorRole.WindowText, QColor(text_color))
            self.palette.setColor(QPalette.ColorRole.ButtonText, QColor(text_color))

        self.central_widget.setAutoFillBackground(True)
        self.central_widget.setPalette(self.palette)

        # Create a layout and set it on the central widget
        self.layout = QVBoxLayout(self.central_widget)

        self.layout.setSpacing(0)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # Store and render root component
        self.root_component = root_component
        self.root_component.set_window(self)  # Allow component to trigger window updates

        # Initial render
        self.render()

    def set_current_component(self, component):
        """Set a new root component and re-render the window"""
        self.root_component = component
        self.root_component.set_window(self)
        self.render()

    def navigate_to(self, route_name, **kwargs):
        """Use the router to navigate and update the window's current component"""
        new_component = self.router.navigate(route_name, **kwargs)
        self.set_current_component(new_component)

    def render(self):
        """Render or update the root component"""
        # Clear existing widgets if any
        while self.layout.count():
            item = self.layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # Render root component
        root_widget = self.root_component.render()

        self.layout.addWidget(root_widget)


    def rerender(self):
        """Rerender the window - called by components when needed"""
        self.render()