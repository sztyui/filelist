try:
	from .config import config
except:
	from config import config

from logging import INFO
from flask import Flask, flash
import flask_login
import ssl
import os

# App itself
app = Flask(__name__)
app.logger.setLevel(INFO)
app.secret_key = config['app']['secret_key']

# Login manager :)
login_manager = flask_login.LoginManager()
login_manager.init_app(app)

try:
	from .login_logic import login
	from .filelist import fl
	from .index import index
	from .qm_module import qm
	from .email_to_bereizoli import bzmail

	from .errorhandler import *
except Exception as e:
	print('Manual mode: {!r}'.format(e))
	from login_logic import login
	from filelist import fl
	from index import index
	from qm_module import qm
	from email_to_bereizoli import bzmail

	from errorhandler import *

app.register_blueprint(fl)
app.register_blueprint(index)
app.register_blueprint(qm)
app.register_blueprint(bzmail)

# ctx = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
# priv_file = os.path.join(os.path.dirname(os.path.realpath(__file__)), "certs", "key.pem")
# cer_file = os.path.join(os.path.dirname(os.path.realpath(__file__)), "certs", "cert.pem")
# ctx.load_cert_chain(cer_file, priv_file)

if __name__ == "__main__":
	from werkzeug.serving import run_simple
	#app.run("0.0.0.0", port=5000)
	run_simple('0.0.0.0', 5000, app)
	#run_simple('0.0.0.0', 5000, app, ssl_context=ctx)