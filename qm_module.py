from flask import (
	Blueprint, Response, abort, 
	make_response, request, send_from_directory,
	after_this_request)
import flask_login
try:
	from .ssh import ssh
	from .config import config
	from .environment import PATH, TEMPLATE_ENVIRONMENT
except Exception as e:
	from ssh import ssh
	from config import config
	from environment import PATH, TEMPLATE_ENVIRONMENT

import urllib.parse
import datetime
import shlex
import json
import os

qm = Blueprint('qm', __name__)

@qm.route('/qm/<system>')
@flask_login.login_required
def qm_page(system):
	modif_sys = system.lower().replace('x', 'q')
	if modif_sys not in config.sections():
		abort(404)	# 404 mert nincs ilyen rendszer.
	system_folder = config.get(modif_sys, 'qm')
	command = "{0} {1}".format(config.get("nstrs2", "qm_list_api"), system_folder)
	content = list()
	try:
		_, _, _ = ssh.exec_command("ls {0}".format(system)) # Ez azert kell mert rohatt lassu a szamba...
		stdin, stdout, stderr = ssh.exec_command(command)
		for line in stdout.readlines():
			tmp_d = json.loads(line)
			tmp_d["fullpath"] = urllib.parse.urlencode({"fullpath": tmp_d['fullpath']})
			content.append(tmp_d)
	except AttributeError as e:
		print("Hiba: {!r}".format(e))	# Leszakadt a szamba... a faszamba... hahaha :(
		abort(500)
	template = TEMPLATE_ENVIRONMENT.get_template("qm.html")
	return template.render({
		"sorok" : sorted(content, key=lambda x: x["time"], reverse=True),
		"date": datetime.datetime.now(), 
		"system": system,
		"logged_in_as": flask_login.current_user.id
		})

@qm.route('/qm/download')
@flask_login.login_required
def qm_download():
	filename = request.args.get("fullpath")
	local_file = os.path.join('/tmp', os.path.basename(filename))
	sftp = ssh.open_sftp()
	sftp.get(filename, local_file)

	@after_this_request
	def remove(response):
		try:
			os.remove(local_file)
		except Exception as e:
			print("Valami hiba adodott a fajl torlese kozben: {0}".format(e))
		return response

	return send_from_directory('/tmp', os.path.basename(local_file))

