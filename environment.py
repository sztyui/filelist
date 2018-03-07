# environment.py

import jinja2
import os

PATH = os.path.dirname(__file__)
TEMPLATE_ENVIRONMENT = jinja2.Environment(
		autoescape=False,
		loader=jinja2.FileSystemLoader(os.path.join(PATH, "templates")),
		trim_blocks=False)