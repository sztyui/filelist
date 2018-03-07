from flask import (
	Blueprint, Response, abort, 
	make_response, request, send_from_directory,
	after_this_request)
import flask_login
try:
	from .ssh import ssh, config
	from .environment import PATH, TEMPLATE_ENVIRONMENT
except Exception as e:
	from ssh import ssh, config
	from environment import PATH, TEMPLATE_ENVIRONMENT

import urllib.parse
import datetime
import os

qm = Blueprint('qm', __name__)

header = ["meret", "honap", "nap", "ido", "fajlnev"]
def create_content(label, lines, system_folder):
	if not isinstance(lines, list):
		return AttributeError("Nem lista erkezett a line valtozoban a create_filename_dict fuggvenyben.")
	result = list()
	for line in lines:
		line_array = line.strip('\t ').split()
		if len(line_array) != len(header):
			continue
		tmp = dict(zip(header, line_array))
		tmp["fajl_helye"] = urllib.parse.urlencode({"sys": system_folder, "file": tmp['fajlnev']})
		if ':' in tmp["ido"]:
			tmp['time_format'] = "%Y.%m.%d %H:%M"
			tmp["formatted_time"] = datetime.datetime.strptime("{3} {0} {1} {2}".format(tmp["honap"], tmp["nap"], tmp["ido"], datetime.datetime.now().year), "%Y %b %d %H:%M")
		else:
			tmp['time_format'] = "%Y.%m.%d"
			tmp["formatted_time"] = datetime.datetime.strptime("{0} {1} {2}".format(tmp["honap"], tmp["nap"], tmp["ido"]), "%b %d %Y")
		result.append(tmp)
	return sorted(result, key=lambda x: x['formatted_time'], reverse=True)

@qm.route('/qm/<system>')
@flask_login.login_required
def qm_page(system):
	if system.lower() not in ['icp', 'pu5', 'icx', 'xu5']:
		abort(404)	# 404 mert nincs ilyen rendszer.
	system_folder = '/usr/qm_{0}'.format(system.lower())
	command = "ls -ltrh {0} | cut -d' ' -f 5-".format(system_folder)
	stdin, stdout, stderr = ssh.exec_command(command)
	try:
		content = create_content(header, stdout.readlines(), system_folder)
	except AttributeError as e:
		print("Hiba: {!r}".format(e))
		abort(500)
	template = TEMPLATE_ENVIRONMENT.get_template("qm.html")
	return template.render({
		"sorok" : content, 
		"date": datetime.datetime.now(), 
		"system": system,
		"logged_in_as": flask_login.current_user.id
		})

@qm.route('/qm/download')
@flask_login.login_required
def qm_download():
	system = request.args.get("sys")
	file = request.args.get("file")
	filename = os.path.join(system, file)
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

