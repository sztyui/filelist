# Alap Flask
from flask import (
	Blueprint, abort, request, 
	redirect, flash, render_template, url_for
	)

# Flask forms
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.fields.html5 import EmailField
from wtforms.validators import DataRequired, Email, InputRequired
from wtforms.widgets import TextArea

# Egyeb cuccok.
import flask_login
import datetime
import json

bzmail = Blueprint('bzmail', __name__)

try:
	from .ssh import ssh
	from .environment import PATH, TEMPLATE_ENVIRONMENT
	from .config import config
except Exception as e:
	from ssh import ssh
	from environment import PATH, TEMPLATE_ENVIRONMENT
	from config import config

class SystemForm(FlaskForm):
	icp = BooleanField('ICP')
	pu5 = BooleanField('PU5')
	icq = BooleanField('ICQ')
	qu5 = BooleanField('QU5')
	lsubmit = SubmitField('Lekerdez')

class EmailForm(FlaskForm):
	to = EmailField("Cimzett", [DataRequired(), Email(), InputRequired("Add meg az email cimedet!")], default="istvan.szilagyi.ext@eon.com")
	cc = EmailField("Masolatot kap", [DataRequired(), Email()], default="istvan.szilagyi.ext@eon.com")
	content = StringField("Elkuldott szoveg.", widget=TextArea())
	msubmit = SubmitField('Kuldes')

def bzget_content(system):
	command = "ssh -n {user}@{server} 'cd {sav}; find . -type f -newermt $(date -d \"now\" \"+%Y-%m-%d\") | cut -d \"_\" -f 3 | sort | uniq'".format(**config[system])
	stdin, stdout, stderr = ssh.exec_command(command)
	spools = [x.strip() for x in stdout.readlines() if len(x) > 3]
	error = stderr.readlines()
	if error:
		raise RunetimeError(', '.join(error))
	return "Spoolok a {0} rendszerben ({1}):\n{2}".format(system, datetime.datetime.now().strftime('%Y.%m.%d %H:%M:%S'), '\n'.join(spools))

@bzmail.route('/bzmail/', methods=['GET'])
@flask_login.login_required
def mail_to_bereizoli():
	lekerdezo_form = SystemForm()
	content_form = EmailForm()
	if request.method == 'GET':
		return TEMPLATE_ENVIRONMENT.get_template("bzmail.html").render({
				"date": datetime.datetime.now(), 
				"logged_in_as": flask_login.current_user.id
				},
				lekerdezo_form=lekerdezo_form
		)
	else:
		abort(404)

@bzmail.route('/bzmail/ask', methods=['POST'])
@flask_login.login_required
def ask():
	lekerdezo_form = SystemForm()
	content_form = EmailForm()
	if lekerdezo_form.validate_on_submit():
		systems = dict(zip(["icp", "pu5", "icq", "qu5"], 
			[lekerdezo_form.icp.id, lekerdezo_form.pu5.id, lekerdezo_form.icq.id, lekerdezo_form.qu5.id]))
		content = str()
		if lekerdezo_form.icp.data:
			content += '\n' + bzget_content("icp")
		if lekerdezo_form.pu5.data:
			content += '\n' + bzget_content("pu5")
		if lekerdezo_form.icq.data:
			content += '\n' + bzget_content("icq")
		if lekerdezo_form.qu5.data:
			content += '\n' + bzget_content("qu5")
		content_form.content.data = content
		content_form.to.data=config['mail']['to']
		content_form.cc.data=config['mail']['cc']
		return TEMPLATE_ENVIRONMENT.get_template("bzmail.html").render({ 
			"systems": systems,
			"date": datetime.datetime.now(), 
			"logged_in_as": flask_login.current_user.id},
			lekerdezo_form=lekerdezo_form,
			content_form=content_form
			)
	else:
		abort(404)

@bzmail.route('/bzmail/send', methods=['POST'])
@flask_login.login_required
def send():
	lekerdezo_form = SystemForm()
	content_form = EmailForm()
	if content_form.validate_on_submit():
		print(content_form.to.data)
		print(content_form.cc.data)
		print(content_form.content.data)
		mail_to_send = {
			"subject": "Spool feldolgozas {0}".format(datetime.datetime.now().strftime('%Y.%m.%d %H:%M:%S')),
			"from": "nstrs2@eon.com",
			"to": content_form.to.data,
			"cc":content_form.cc.data,
			"content": content_form.content.data
		}
		try:
			stdin, _, stderr = ssh.exec_command(config["nstrs2"]["email_to_everyone"])
			print(json.dumps(mail_to_send))
			stdin.write(json.dumps(mail_to_send))
			stdin.write('\n')
			stdin.flush()
			error = stderr.readlines()
			flash("Kikuldve!")
			if error:
				return "<h1>Valami hiba tortent: {0}</h1>".format(', '.join(error))
		except Exception as e:
			return "<h1>Valami hiba tortent: {0}</h1>".format(e)
		return redirect("/bzmail")
	else:
		abort(404)