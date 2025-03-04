from pydantic import BaseModel

from component import NextPyComponent


class TodoItemProps(BaseModel):
    text: str
    completed: bool = False
    id: int


class TodoItem(NextPyComponent):
    props_schema = TodoItemProps
    emits = ["remove", "checked"]
    template_path = "todo_item.html"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = "Todo Item"
        self.state = {
            "is_editing": False,
        }
        self.methods["toggle_complete"] = self.toggle_complete
        self.methods["remove_todo"] = self.remove_todo

    def toggle_complete(self):
        self.emit_event("checked", self.props["id"], not self.props["completed"])

    def remove_todo(self):
        self.emit_event("remove", self.props["id"])
