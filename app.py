from components.todo_item import TodoItem
from component import NextPyComponent

class TodoApp(NextPyComponent):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = "Todo App"
        self.template_path = 'todo_app.html'
        self._state = {
            'todos': [],
            'new_todo': ''
        }
        self.components = {
            'todo-item': TodoItem
        }
        self.methods['add_todo'] = self.add_todo
        self.methods['update_new_todo'] = self.update_new_todo
        self.methods['remove_todo'] = self.remove_todo
        self.methods['update_todo_status'] = self.update_todo_status
        self.methods['go_to_hello'] = self.go_to_hello
        self.computed['todo_count'] = lambda: len(self.state['todos'])

    def go_to_hello(self):
        self.window.navigate_to('hello_world')

    def add_todo(self):
        if self.state['new_todo']:
            self.set_state({
                'todos': self.state['todos'] + [{
                    'text': self.state['new_todo'],
                    'completed': False
                }],
                'new_todo': ''
            })
            # Only updates the todo list and clears the input

    def update_new_todo(self, value):
        self.set_state({
            **self.state,
            'new_todo': value
        }, rerender=False)

    def remove_todo(self, index):
        self.set_state({
            **self.state,
            "todos": self.state["todos"][:index] + self.state["todos"][index + 1:]
        })

    def update_todo_status(self, index, completed):
        todos = self.state['todos'].copy()
        todos[index]['completed'] = completed
        self.set_state({'todos': todos})