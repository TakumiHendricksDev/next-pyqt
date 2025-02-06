from template_engine import PyComponent

class App(PyComponent):
    def __init__(self):
        super().__init__()
        self.template_path = 'templates/app_template.html'
        self.state = {
            'todos': [
            ],
            'new_todo': ''
        }
        self.add_computed('todo_count', lambda: len(self.state['todos']))
        self.add_method('add_todo', self.add_todo)
        self.add_method('handle_input_change', self.handle_input_change)

    def add_todo(self):
        if self.state['new_todo']:
            self.setState({
                'todos': self.state['todos'] + [self.state['new_todo']],
                'new_todo': ''
            })

    def handle_input_change(self, value):
        self.state['new_todo'] = value

    def update_new_todo(self, value):
        self.setState({'new_todo': value})

    def remove_todo(self, index):
        todos = self.state['todos'].copy()
        todos.pop(index)
        self.setState({'todos': todos})