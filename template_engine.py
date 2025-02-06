import re
from string import Template
import ast

class PyComponent:
    def __init__(self):
        self.template = None
        self.state = {}
        self.computed = {}
        self.methods = {}
        self.renderer = {}

    def setState(self, new_state):
        self.state.update(new_state)
        self.rerender()
        # Here you would trigger a re-render

    def add_computed(self, name, func):
        self.computed[name] = func

    def add_method(self, name, func):
        self.methods[name] = func

    def set_renderer(self, window):
        self.renderer = window

    def rerender(self):
        """ Triggers a re-render if the renderer exists. """
        if self.renderer:
            self.renderer.rerender()


class HTMLTemplate:
    def __init__(self, component: PyComponent):
        self.component = component

    def parse_python_blocks(self, html_content):
        # Replace {py} blocks with evaluated Python code
        def evaluate_python(match):
            python_code = match.group(1)
            try:
                # Create context with component's state and computed properties
                context = {
                    'state': self.component.state,
                    'computed': self.component.computed
                }

                # Add any component methods
                context.update({
                    name: getattr(self.component, name)
                    for name in dir(self.component)
                    if callable(getattr(self.component, name))
                       and not name.startswith('_')
                })

                # Evaluate the Python expression
                result = eval(python_code, {}, context)
                if callable(result):
                    result = result()
                return str(result)
            except Exception as e:
                return f"Error: {str(e)}"

        # Replace {py} blocks
        pattern = r'{{\s+(.*?)\s+}}'
        return re.sub(pattern, evaluate_python, html_content)

    def parse_for_loops(self, html_content):
        # Handle for loops in the template
        def process_loop(match):
            loop_expr = match.group(1)
            loop_content = match.group(2)

            # Parse the loop expression
            loop_parts = loop_expr.split(' in ')
            if len(loop_parts) != 2:
                return "Error: Invalid for loop syntax"

            item_name = loop_parts[0].strip()
            collection_expr = loop_parts[1].strip()

            try:
                # Evaluate the collection expression
                context = {
                    'state': self.component.state,
                    'computed': self.component.computed
                }
                collection = eval(collection_expr, {}, context)

                # Generate content for each item
                result = []
                for item in collection:
                    # Add the loop variable to the context
                    loop_context = context.copy()
                    loop_context[item_name] = item

                    # Process the loop content
                    content = loop_content
                    # Replace {{ }} blocks within the loop
                    content = re.sub(
                        r'{{\s+(.*?)\s+}}',
                        lambda m: str(eval(m.group(1), {}, loop_context)),
                        content
                    )
                    result.append(content)

                return ''.join(result)
            except Exception as e:
                return f"Error in loop: {str(e)}"

        # Replace {for} blocks
        pattern = r'{for\s+(.*?)}(.*?){/for}'
        return re.sub(pattern, process_loop, html_content, flags=re.DOTALL)

    def parse_if_blocks(self, html_content):
        def process_if(match):
            condition = match.group(1)
            if_content = match.group(2)
            else_content = match.group(3) if match.group(3) else ""

            try:
                # Evaluate the condition
                context = {
                    'state': self.component.state,
                    'computed': self.component.computed
                }
                result = eval(condition, {}, context)

                # Return appropriate content
                return if_content if result else else_content
            except Exception as e:
                return f"Error in if condition: {str(e)}"

        # Replace {if} blocks
        pattern = r'{if\s+(.*?)}(.*?)(?:{else}(.*?))?{/if}'
        return re.sub(pattern, process_if, html_content, flags=re.DOTALL)

    def render(self, html_content):
        # Process the template in order: for loops, if blocks, and Python expressions
        html_content = self.parse_for_loops(html_content)
        html_content = self.parse_if_blocks(html_content)
        html_content = self.parse_python_blocks(html_content)
        return html_content

    def render_template(self):
        try:
            with open(self.component.template_path, 'r') as file:
                template_content = file.read()

                return self.render(template_content)
        except Exception as e:
            return f"Error: {str(e)}"