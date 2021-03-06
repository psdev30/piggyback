import flask
from flask import Flask, render_template, session
from google.cloud import datastore


app = Flask(__name__)

app.secret_key = 'piggyback'


@app.route('/')
def root(error=None):
	return render_template("login.html", invalid_credentials=error)


@app.route('/create_account_page')
def create_account_page(error=None):
    return render_template('create_account.html', error=error)

@app.route('/create_account', methods=['POST'])
def create_account():
	client = datastore.Client()
	try:
		account_key = client.key('user')
		user_entity = datastore.Entity(account_key)
		user_entity['firstName'] = flask.request.values['name'].split(' ')[0]
		user_entity['lastName'] = flask.request.values['name'].split(' ')[1]
		user_entity['phone'] = flask.request.values['phone']
		user_entity['email'] = flask.request.values['email']
		user_entity['username'] = flask.request.values['username']
		user_entity['password'] = flask.request.values['password']
		user_entity['street'] = flask.request.values['street']
		user_entity['city'] = flask.request.values['city']
		user_entity['state'] = flask.request.values['state']
		user_entity['zip'] = flask.request.values['zip']
		user_entity['ownsCar'] = flask.request.values['car']
		if flask.request.values['car_make'] and flask.request.values['car_model']:
			user_entity['carMake'] = flask.request.values['car_make']
			user_entity['carModel'] = flask.request.values['car_model']
	except:
			return create_account_page('Oops, your input was invalid. Try again!')

	try:
		client.put(user_entity)
	except:
		return create_account_page('Oops, something went wrong on our end! Try creating an account another time')
	
	session['username'] = flask.request.values['username']
	session['password'] = flask.request.values['password']
	return home_page()


@app.route('/profile')
def profile():
	client = datastore.Client('project-1520')
	if verify_credentials_helper():
		fetchProfile = client.query(kind='user')
		fetchProfile.add_filter('username', '=', session['username'])
		fetchProfile.add_filter('password', '=', session['password'])
		res = list(fetchProfile.fetch())
		if len(res) == 1:
			name = res[0]['firstName'] + ' ' +  res[0]['lastName']
			city = res[0]['city']
			state = res[0]['state']
			location = city + ', ' + state
			num_rides = res[0]['numRides']
			car = None
			if res[0]['lastPiggyBack'] != '':
				last_piggyback = res[0]['lastPiggyBack']
			else:
				last_piggyback = 'A new piglet!'

			profile_info = {'Lives in': location, 'Number of Rides: ': num_rides, 'Last PiggyBack: ': last_piggyback}

			if res[0]['ownsCar']:
				car = res[0]['carMake'] + ' ' +  res[0]['carModel']
				profile_info['Owns a '] = car
			if res[0]['mostFrequentDestination'] != '':
				profile_info['Most frequent travel destination: '] = res[0]['mostFrequentDestination']

			return render_template("profile.html", name=name, profile=profile_info)
	else:
		return root(True)

@app.route('/home_page')
def home_page(error=None):
	if verify_credentials_helper:
		return render_template('home_page.html')
	else:
		return render_template('error.html', error='Oops, you aren\'t logged in!')


@app.route('/validate_login', methods=['POST'])
def validate_login():
	username = flask.request.values['username']
	password = flask.request.values['password']
	client = datastore.Client()
	verify_login_query = client.query(kind='user')
	verify_login_query.add_filter('username', '=', username)
	verify_login_query.add_filter('password', '=', password)
	res = list(verify_login_query.fetch())
	if len(res) == 1:
		retrieved_username = res[0]['username']
		retrieved_password = res[0]['password']
	else:
		return root(True)
	if retrieved_username == username and retrieved_password == password:
		session['username'] = username
		session['password'] = password
		return home_page()

@app.route('/logout')
def logout():
	session.pop('username', None)
	session.pop('password', None)
	return root()


def verify_credentials_helper():
	client = datastore.Client('project-1520')
	verify_login_query = client.query(kind='user')
	verify_login_query.add_filter('username', '=', session['username'])
	verify_login_query.add_filter('password', '=', session['password'])
	res = list(verify_login_query.fetch())
	if len(res) == 1:
		return True
	return False
	



if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)

