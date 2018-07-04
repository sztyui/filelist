from flask import (
    Blueprint, Response, abort, request,
    after_this_request, jsonify, send_file,
    make_response)
import flask_login
try:
    from .ssh import ssh
    from .config import config
    from .environment import PATH, TEMPLATE_ENVIRONMENT
except Exception as e:
    from ssh import ssh
    from config import config
    from environment import PATH, TEMPLATE_ENVIRONMENT

try:
    from .decorators import lower_it
except ImportError as e:
    from decorators import lower_it

import urllib.parse
import datetime
import shlex
import json
import os
import io

qm = Blueprint('qm', __name__)

@qm.route('/qm_list/<system>', methods=['POST', 'GET'])
#@flask_login.login_required
@lower_it
def qm_list(system):
    if system not in config.sections():
        abort(404)
    if request.method == 'GET':
        folder = config.get(system, 'qm')
        ftp = ssh.open_sftp()
        files = ftp.listdir(folder)
        result = []
        for file in files:
            fullpath = os.path.join(folder, file)
            st = ftp.stat(fullpath)
            #datetime.datetime.fromtimestamp(st.st_mtime).strftime("MMM d, y")
            result.append({
                'create': datetime.datetime.fromtimestamp(st.st_mtime).strftime("%Y.%m.%d %H:%M:%S"),
                'filename': file,
                'fullpath': fullpath,
                'owner': st.st_uid,
                'size': st.st_size
                })
        return jsonify(result)
    elif request.method == 'POST':
        abort(500)


@qm.route('/qm/<system>/', methods=['GET'], strict_slashes=False)
@flask_login.login_required
@lower_it
def qm_page(system):
    if system not in config.sections():
        abort(404)
    if request.method == 'GET':
        return TEMPLATE_ENVIRONMENT.get_template("qm.html").render({
            "date": datetime.datetime.now(), 
            "system": system,
            "logged_in_as": flask_login.current_user.id,
        })
    else:
        abort(405)

def make_pdf_response(pdf_file: str) -> Response:
    with open(pdf_file, 'rb') as pdf_mem:
        return send_file(
                    io.BytesIO(pdf_mem.read()),
                    attachment_filename=os.path.basename(pdf_file),
                    mimetype='application/pdf'
            )

@qm.route('/qm_download/', strict_slashes=False)
def qm_download():
    system = request.args.get('system', None)
    if system is None: 
        abort(404, "Hibas parameter.")
    if request.method == 'GET':
        qm_folder = config.get(system.lower(), 'qm')
        filename = os.path.join(qm_folder, request.args.get('filename', None))
        if filename is None: 
            abort(404, "Hianyzo parameter.")
        local_file = os.path.join('/tmp', os.path.basename(filename))
        try:
            ssh.open_sftp().get(filename, local_file)
        except FileNotFoundError as e:
            abort(404, "A fajl nem talalhato.")

        @after_this_request
        def remove(response):
            try:
                os.remove(local_file)
            except Exception as e:
                print("Valami hiba tortent a {0} fajl torlese kozben: {1}".format(local_file, e))
            return response
        
        return make_pdf_response(local_file)
    else:
        abort(405)
