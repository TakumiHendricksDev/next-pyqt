from template_engine import PyComponent


class HeaderApp(PyComponent):
    props_config = {
        'title': {
            'type': str,
            'required': True,
        }
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.template_path = 'templates/header.html'
