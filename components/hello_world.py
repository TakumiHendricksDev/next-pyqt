from component import NextPyComponent

class HelloWorldApp(NextPyComponent):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = "Hello World App"
        self.template_path = 'hello_world.html'
        self.methods["redirect_todo"] = self.redirect_todo

    def redirect_todo(self):
        self.window.navigate_to("todo_app")