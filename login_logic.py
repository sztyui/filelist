import flask
import flask_login
import sqlalchemy.orm
import datetime

try:
	from . import login_manager, app
	from .environment import PATH, TEMPLATE_ENVIRONMENT
	from .users import *
except:
	from icp_filelist import login_manager, app
	from environment import PATH, TEMPLATE_ENVIRONMENT
	from users import *

class User(flask_login.UserMixin):
	pass

@login_manager.user_loader
def user_loader(email):
	referring_users = Session().query(Users).filter(Users.name.like(email))
	if referring_users.count() != 1:
		return
	user = User()
	user.id = email
	return user

@login_manager.request_loader
def request_loader(request):
	email = flask.request.form.get('email', None)
	if email:
		sess = Session()
		user = Session().query(Users).filter(Users.name.like(email))
		if user.count() != 1:
			return
		user = User()
		user.id = email
		try:
			actual_user = user.one()
		except sqlalchemy.orm.exc.NoResultFound as e:
			return
		if flask.request.form['password'] == actual_user.password:
			user.is_authenticated = True
			actual_user.last_login = datetime.datetime.now()
			sess.commit()
		return user
	else:
		return

@app.route('/bejelentkezes', methods=['GET', 'POST'])
def login():
	if flask.request.method == 'GET':
		return TEMPLATE_ENVIRONMENT.get_template('login.html').render()
	email = flask.request.form['email']
	try:
		act_user = Session().query(Users).filter(Users.name.like(email)).one()
	except sqlalchemy.orm.exc.NoResultFound as e:
		print(e)
		return TEMPLATE_ENVIRONMENT.get_template('login.html').render({"hibas_bejelentkezes": True})

	if flask.request.form['password'] == act_user.password:
		user = User()
		user.id = email
		flask_login.login_user(user)
		return flask.redirect("/menu")
	else:
		return TEMPLATE_ENVIRONMENT.get_template('login.html').render({"hibas_bejelentkezes": True})

@app.route('/jelszo_csere', methods=['GET', 'POST'])
def password_change():
	if flask.request.method == 'GET':
		return TEMPLATE_ENVIRONMENT.get_template('password_change.html').render()
	else:
		sess = Session()
		try:
			email = flask.request.form['email']
			act_user = sess.query(Users).filter(Users.name.like(email)).one()
		except Exception as e:
			print(e)
			sess.rollback()
			return TEMPLATE_ENVIRONMENT.get_template('password_change.html').render({"hiba": "Sikertelen bejelentkezes!"})

		if flask.request.form['password-old'] == act_user.password \
		and flask.request.form.get('password-new', None) == flask.request.form.get('password-again') \
		and flask.request.form.get('password-new', None):
			act_user.password = flask.request.form['password-new']
			sess.commit()
			return TEMPLATE_ENVIRONMENT.get_template('password_change.html').render({"jelszo_megvaltoztatva": True})
		else:
			return TEMPLATE_ENVIRONMENT.get_template('password_change.html').render({"hiba": "Valami hiba tortent!"})

@app.route('/kijelentkezes')
def logout():
	flask_login.logout_user()
	return flask.redirect("/bejelentkezes")

@login_manager.unauthorized_handler
def unauthorized_handler():
	return flask.redirect("/bejelentkezes")