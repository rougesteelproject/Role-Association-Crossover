from flask import Flask, render_template

class FlaskWrapper:
    def __init__(self, app = Flask(__name__)):
        self._app = app

    def add_endpoint(self, endpoint=None, endpoint_name=None, handler=None, methods=['GET'], *args, **kwargs):
        self._app.add_url_rule(endpoint, endpoint_name, handler, methods=methods, *args, **kwargs)
        
    def render(template: str = 'index.html', **kwargs):
        return render_template(template, kwargs)

    def run(self, **kwargs):
        self._app.run(**kwargs)