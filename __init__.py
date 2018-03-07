from flask import Flask
import flask_login
import ssl
import os

app = Flask(__name__)
app.secret_key = 'Eon123'

login_manager = flask_login.LoginManager()
login_manager.init_app(app)

try:
	from .login_logic import login
	from .filelist import fl
	from .index import index
	from .qm_module import qm
except Exception as e:
	print('Manual mode: {!r}'.format(e))
	from login_logic import login
	from filelist import fl
	from index import index
	from qm_module import qm

app.register_blueprint(fl)
app.register_blueprint(index)
app.register_blueprint(qm)

# ctx = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
# priv_file = os.path.join(os.path.dirname(os.path.realpath(__file__)), "certs", "key.pem")
# cer_file = os.path.join(os.path.dirname(os.path.realpath(__file__)), "certs", "cert.pem")
# ctx.load_cert_chain(cer_file, priv_file)


if __name__ == "__main__":
	from werkzeug.serving import run_simple
	#app.run("0.0.0.0", port=5000)
	run_simple('0.0.0.0', 5000, app)
	#run_simple('0.0.0.0', 5000, app, ssl_context=ctx)