from flask import Blueprint, Response
import flask_login

try:
	from .ssh import ssh
	from .environment import PATH, TEMPLATE_ENVIRONMENT
except Exception as e:
	from ssh import ssh
	from environment import PATH, TEMPLATE_ENVIRONMENT

index = Blueprint('index', __name__)

last_file_in_folder = lambda x: "find {0} -maxdepth 1 -type f | sort -t_ -nk2,2 | tail -n1".format(x)

def get_file_content(folder):
	stdin, stdout, stderr = ssh.exec_command(last_file_in_folder(folder))
	fn = stdout.readline().strip('\n \t')
	if not fn:
		return "<h2>Nem talaltam meg a fajlt.</h2>"
	ftp = ssh.open_sftp()
	remote_file = ftp.open(fn)
	try:
		content = [line for line in remote_file]
	finally:
		remote_file.close()
		ftp.close()
	if not content:
		return "<h1>Ures volt a fajl</h2>"
	return '\n'.join(content)

@index.route("/napi_nyitott")
@flask_login.login_required
def napi_nyitott():
	return get_file_content("/usr/strs/napi_nyitott/")


@index.route("/napi_zsort")
@flask_login.login_required
def napi_zsort():
	return get_file_content("/usr/strs/napi_zsort/")

@index.route("/")
@index.route("/menu")
@flask_login.login_required
def mainpage():
	return TEMPLATE_ENVIRONMENT.get_template("index.html").render({"logged_in_as": flask_login.current_user.id})