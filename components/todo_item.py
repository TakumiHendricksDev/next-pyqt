from pydantic import BaseModel

from template_engine import NextPyComponent


class TodoItemProps(BaseModel):
    text: str
    completed: bool = False
    id: int

class TodoItem(NextPyComponent):
    props_schema = TodoItemProps
    emits = ['remove']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.template_path = 'todo_item.html'
        self.state = {
            'is_editing': False,
        }
        self.methods['toggle_complete'] = self.toggle_complete
        self.methods['start_edit'] = self.start_edit
        self.methods['remove_todo'] = self.remove_todo


    def toggle_complete(self):
        if self.parent_component:
            self.parent_component.update_todo_status(
                self.props['text'],
                not self.props['completed']
            )

    def start_edit(self):
        self.setState({'is_editing': True})
        # Only this component will rerender, not the entire app

    def remove_todo(self):
        self.emit_event('remove', self.props['id'])