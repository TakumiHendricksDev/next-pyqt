from header_app import HeaderApp
from template_engine import PyComponent

class App(PyComponent):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.template_path = 'templates/index.html'
        self.state = {
            'todos': [
            ],
            'new_todo': ''
        }
        self.components = {
            "header": HeaderApp
        }
        self.add_computed('todo_count', lambda: len(self.state['todos']))
        self.add_method('add_todo', self.add_todo)
        self.add_method('update_new_todo', self.update_new_todo)
        self.add_method('remove_todo', self.remove_todo)

    def add_todo(self):
        if self.state['new_todo']:
            self.setState({
                'todos': self.state['todos'] + [self.state['new_todo']],
                'new_todo': ''
            })

    def update_new_todo(self, value):
        self.state['new_todo'] = value

    def remove_todo(self, index):
        todos = self.state['todos'].copy()
        todos.pop(int(index))
        self.setState({'todos': todos})