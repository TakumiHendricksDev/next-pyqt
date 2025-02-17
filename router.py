class NextPyRouter:
    def __init__(self):
        self.routes = {}

    def register_route(self, route_name: str, component_factory):
        self.routes[route_name] = component_factory

    def navigate(self, route_name: str, **kwargs):
        component_factory = self.routes.get(route_name)
        if component_factory:
            # Instantiate and return the component
            return component_factory(**kwargs)
        else:
            raise ValueError(f"Route '{route_name}' not found")