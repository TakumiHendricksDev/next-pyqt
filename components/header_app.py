from template_engine import NextPyComponent, NextPyProps


class HeaderProps(NextPyProps):
    title: str  # Required prop

class HeaderApp(NextPyComponent):
    props_schema = HeaderProps

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.template_path = 'templates/header.html'
