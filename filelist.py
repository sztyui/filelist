from flask import (Blueprint, url_for,
                   render_template, send_file,
                   after_this_request, request, abort,
                   jsonify, current_app, Response)
import flask_login
try:
    from .environment import PATH, TEMPLATE_ENVIRONMENT
    from .ssh import ssh
    from .config import config
    from .decorators import lower_it
except Exception as e:
    from environment import PATH, TEMPLATE_ENVIRONMENT
    from ssh import ssh
    from config import config
    from decorators import lower_it

import operator
import datetime
import zipfile
import jinja2
import socket
import shlex
import time
import json
import sys
import os
import io

fl = Blueprint('fl', __name__)


def get_file(for_download):
    local_tmp_dir = "/tmp/"
    __local_file = os.path.join(local_tmp_dir, os.path.basename(for_download))
    sftp = ssh.open_sftp()
    sftp.get(for_download, __local_file)
    sftp.close()
    ssh.exec_command('rm {0}'.format(for_download))
    return __local_file


@fl.route("/afps/<system>", methods=['POST', 'GET'], strict_slashes=False)
@flask_login.login_required
@lower_it
def get_afp(system):
    if request.method == 'GET':
        if system not in config.sections():
            abort(404)
        command = "ssh -n {user}@{server} 'python {afp_scpipt} {system}'".format(system=system, **config[system.lower()])
        stdin, stdout, stderr = ssh.exec_command(command)
        return jsonify([json.loads(line) for line in stdout.readlines()])
    else:
        abort(500)


# For sending out ZIP files to Drescher.
@fl.route("/zips/<system>", methods=['POST', 'GET'], strict_slashes=False)
@flask_login.login_required
def zip_new(system):
    system_name = system.lower().replace('x', 'q')
    if request.method == 'GET':
        if system.upper() not in ['ICP', 'PU5', 'ICX', 'XU5']:
            abort(404)
        command = "ssh -n {user}@{server} 'python {zip_script} {system}'".format(system=system.lower(), **config[system.lower()])
        stdin, stdout, stderr = ssh.exec_command(command)
        lines = stdout.readlines()
        content = list()
        for line in lines:
            json_data = json.loads(line)
            json_data["create"] = datetime.datetime.fromtimestamp(json_data["create"])
            content.append(json_data)
        return jsonify(content)
    elif request.method == 'POST':
        if system.upper() not in ['ICX', 'XU5']:
            return json.dumps({'error': True}), 200, {'ContentType':'application/json'}
        filename = request.get_json().get('filename', None)
        current_app.logger.warning("user: {0}, resent: {1}".format(flask_login.current_user.id, filename))
        command = "ssh -n {user}@{server} 'cp {zip}/{filename} {uc4}/{zip_filename}'".format(filename=filename, zip_filename=filename.replace('.zin', '.zik').replace('zip', 'zik'), **config[system.upper()])
        _, _, stderr = ssh.exec_command(command)
        if stderr.readlines():
            return json.dumps({'success': True}), 200, {'ContentType':'application/json'}
        return json.dumps({'error': True}), 200, {'ContentType':'application/json'}
    else:
        abort(500)
    return 


# Zip part Index.
@fl.route("/<view>/<system>", methods=["GET"])
@flask_login.login_required
def zippings(view: str, system: str):
    if request.method == 'GET':
        actual_date = datetime.datetime.now()
        if view.lower() in ['zip', 'afp']:
            return TEMPLATE_ENVIRONMENT.get_template("{0}.html".format(view.lower())).render({
                "date": actual_date, 
                "system": system,
                "logged_in_as": flask_login.current_user.id
                })
        else:
            return abort(500)
    else:
        return abort(404)

@fl.route("/download/<system>/<filename>")
@flask_login.login_required
def download(system: str, filename: str):
    if filename:
        command = "source {webserver_download} {system} {file}".format(system=system, file=os.path.basename(filename), **config['nstrs2'])
        stdin, stdout, stderr = ssh.exec_command(command)
        for_download = stdout.readlines()[-1].strip("\n")
        if for_download == "-1":
            return abort(404)
        
        __local_file = get_file(for_download)
        print(__local_file)
        
        @after_this_request
        def remove_everything(response):
          try:
              os.remove(__local_file)
          except Exception as error:
              print("Valami hiba volt a fajl torlesenel: {0}".format(__local_file))
          return response

        return send_file(__local_file, 
                        attachment_filename=os.path.basename(__local_file), 
                        as_attachment=True, mimetype='application/zip'
                        )
