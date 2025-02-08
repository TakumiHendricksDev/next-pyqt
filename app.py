from components.todo_item import TodoItem
from template_engine import NextPyComponent

class TodoApp(NextPyComponent):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.template_path = 'todo_app.html'
        self.state = {
            'todos': [],
            'new_todo': ''
        }
        self.components = {
            'todo-item': TodoItem
        }
        self.methods['add_todo'] = self.add_todo
        self.methods['update_new_todo'] = self.update_new_todo
        self.methods['remove_todo'] = self.remove_todo
        self.computed['todo_count'] = lambda: len(self.state['todos'])


    def add_todo(self):
        if self.state['new_todo']:
            self.setState({
                'todos': self.state['todos'] + [{
                    'text': self.state['new_todo'],
                    'completed': False
                }],
                'new_todo': ''
            })
            # Only updates the todo list and clears the inpu

    def update_new_todo(self, value):
        self.setState({
            **self.state,
            'new_todo': value
        }, rerender=False)

    def remove_todo(self, index):
        index_int = int(index)
        self.setState({
            **self.state,
            "todos": self.state["todos"][:index_int] + self.state["todos"][index_int + 1:]
        })

    def update_todo_status(self, todo_text: str, completed: bool):
        todos = self.state['todos'].copy()
        for todo in todos:
            if todo['text'] == todo_text:
                todo['completed'] = completed
        self.setState({'todos': todos})
        # Only updates the specific todo item