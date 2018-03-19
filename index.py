from flask import Blueprint, Response
import flask_login

try:
	from .ssh import ssh
	from .environment import PATH, TEMPLATE_ENVIRONMENT
	from .config import config
except Exception as e:
	from ssh import ssh
	from environment import PATH, TEMPLATE_ENVIRONMENT
	from config import config

index = Blueprint('index', __name__)

last_file_in_folder = lambda x: "find {0} -maxdepth 1 -type f | sort -t_ -nk2,2 | tail -n1".format(x)

def get_system_statuses():
	result = dict()

	def ask_running(system_name):
		stdin, stdout, stderr = ssh.exec_command("ssh {user}@{server} 'ps -ef | grep \"[S]PG\"'".format(**config[system_name.lower()]))
		return True if len(stdout.readlines()) else False

	result['icq'] = ask_running("icq")
	result['qu5'] = result['icq']
	result['icp'] = ask_running("icp")
	result['pu5'] = result['icp']

	return result

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
	system_statuses = get_system_statuses()
	return TEMPLATE_ENVIRONMENT.get_template("index.html").render({
		"logged_in_as": flask_login.current_user.id,
		"system_statuses": system_statuses
		})