import flask
from flask import Flask, render_template, session
from google.cloud import datastore


app = Flask(__name__)

SESSION_KEY = 'piggyback'


@app.route('/')
def root(error=None):
	return render_template("login.html", invalid_credentials=error)


@app.route('/create_account')
def create_account():
    return render_template("create_account.html")


@app.route('/profile')
def profile():
    return render_template("profile.html")

@app.route('/home_page')
def home_page(username=None, password=None, error=None):
	return render_template("home_page.html", uname=username, pname=password)

@app.route('/validate_login', methods=['POST'])
def validate_login():
	username = flask.request.values['username']
	password = flask.request.values['password']
	client = datastore.Client()
	verify_login_query = client.query(kind='user')
	verify_login_query.add_filter('username', '=', username)
	verify_login_query.add_filter('password', '=', password)
	# return '12'
	res = list(verify_login_query.fetch())
	if len(res) > 0:
		retrieved_username = res[0]['username']
		retrieved_password = res[0]['password']
	else:
		return root(True)
	if retrieved_username == username and retrieved_password == password:
		session['username'] = username
		session['password'] = password
		return home_page(username, password)

@app.route('/logout')
def logout():
	session.pop('username', None)
	session.pop('password', None)
	



if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)

