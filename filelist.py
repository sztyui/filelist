from flask import (Blueprint, url_for, 
	render_template, send_file,
	after_this_request)
import flask_login
try:
	from .environment import PATH, TEMPLATE_ENVIRONMENT
	from .ssh import ssh
	from .config import config
except Exception as e:
	from environment import PATH, TEMPLATE_ENVIRONMENT
	from ssh import ssh
	from config import config

import operator
import datetime
import zipfile
import jinja2
import socket
import json
import sys
import os
import io

fl = Blueprint('fl', __name__)

@fl.route("/afp/<system>")
@flask_login.login_required
def afplist(system):
	if system not in ['ICP', 'PU5', 'ICX', 'XU5']:
		return '<h1>Nincs ilyen rendszer: {0}</h1>'.format(system)
	sysname = system.lower().replace('x', 'q')
	connection_string = "ssh -n {user}@{server} 'cd {afp}; find . -type f -newermt $(date -d \"-1 month\" \"+%Y-%m-%d\") -exec ls -ltrh {{}} \; | column -t | while read _ _ user _ size month day time name; do echo $user $size $(date -d \"$month $day $time\" \"+%m-%d %H:%M\") $name; done'".format(**config[sysname])
	stdin, stdout, stderr = ssh.exec_command(connection_string)
	result=list()
	for line in stdout.readlines():
		tmp_list = dict(zip(["felhasznalo", "meret", "datum", "idopont", "fajlnev"], [x.strip() for x in line.split(" ") if x]))
		result.append(tmp_list)
	result.sort(key=lambda x: x["datum"], reverse=True)
	return TEMPLATE_ENVIRONMENT.get_template("afp.html").render(
		{"content": result, "date": datetime.datetime.now(), "system": system, "logged_in_as": flask_login.current_user.id}
	)

@fl.route("/zip/<system>")
@flask_login.login_required
def zippings(system):
	if system not in ['ICP', 'PU5', 'ICX', 'XU5']:
		return '<h1>Nincs ilyen rendszer: {0}</h1>'.format(system)
	sysname = system.lower().replace('x', 'q')
	command = "ssh -n {user}@{server} 'python {zip_script} {system}'".format(system=sysname, **config[sysname])
	stdin, stdout, stderr = ssh.exec_command(command.format(system))
	lines = stdout.readlines()
	content = list()
	for line in lines:
		json_data = json.loads(line)
		json_data["create"] = datetime.datetime.fromtimestamp(json_data["create"])
		content.append(json_data)
	return TEMPLATE_ENVIRONMENT.get_template("zip.html").render({
		"content": content, 
		"date": datetime.datetime.now(), 
		"system": system,
		"logged_in_as": flask_login.current_user.id
		})

@fl.route("/download/<system>/<path:filename>")
@flask_login.login_required
def download(system, filename):
	if system not in ['ICP', 'PU5', 'ICX', 'XU5']:
		return '<h1>Nincs ilyen rendszer: {0}</h1>'.format(system)
	stdin, stdout, stderr = ssh.exec_command("source /usr/UniQ/scripts/webserver_download.sh {system} {file}".format(
		system=system, file=os.path.basename(filename)))
	for_download = stdout.readlines()[-1].strip("\n")
	if for_download == "-1":
		return "<h1>Nincs ilyen fajl a szerveren: {0}</h1>".format(filename)
	else:
		local_tmp_dir = "/tmp/"
		__local_file = os.path.join(local_tmp_dir, os.path.basename(for_download))
		sftp = ssh.open_sftp()
		sftp.get(for_download, __local_file)
		sftp.close()
		ssh.exec_command('rm {0}'.format(for_download))

		@after_this_request
		def remove_everything(response):
			try:
				os.remove(__local_file)
			except Exception as error:
				print("Valami hiba volt a fajl torlesenel: {0}".format(__local_file))
			return response

		return send_file(__local_file, 
			attachment_filename=os.path.basename(__local_file), 
			as_attachment=True, mimetype='application/zip')
