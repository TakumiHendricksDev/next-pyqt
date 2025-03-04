from component import NextPyComponent

class HelloWorldApp(NextPyComponent):
    template_path = 'hello_world.html'
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = "Hello World App"
        self.methods["redirect_todo"] = self.redirect_todo

    def redirect_todo(self):
        self.window.navigate_to("todo_app")