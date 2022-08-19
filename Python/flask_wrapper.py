from flask import Flask, render_template, redirect
from flask import request as req

class FlaskWrapper:
    def __init__(self, app = Flask(__name__)):
        self._app = app

    def add_endpoint(self, endpoint=None, endpoint_name=None, handler=None, methods=['GET']):
        self._app.add_url_rule(endpoint, endpoint_name, handler, methods=methods)
        
    def render(self, template: str = 'index.html', **kwargs):
        return render_template(template, **kwargs)

    def redirect(self, url):
        return redirect(url)

    def run(self, **kwargs):
        self._app.run(**kwargs)

    def request(self):
        return req