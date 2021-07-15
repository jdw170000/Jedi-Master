from flask import Flask, request, render_template, session, abort, redirect, url_for
from secrets import token_hex

from jedi_database import JediDatabase

app = Flask(__name__)

MODERATOR_KEY = None

#todo: create the templates; index.html, moderator.html, and group.html

@app.route('/', methods=['GET'])
def index():
	with JediDatabase() as jedi_db:
		groups = jedi_db.get_all_groups()
		return render_template('index.html', data=groups)


@app.route('/moderator/<key>')
def moderator_key(key):
	# check if client is the moderator
	if key == MODERATOR_KEY:
		session['id'] = -1
		return redirect(url_for('moderator'))
	else:
		# user provided wrong key
		abort(401)

@app.route('/moderator')
def moderator():
	if int(session['id']) != -1:
		abort(401)
	
	#todo: collect the relevant data

	return render_template('moderator.html')	

@app.route('/moderator/do_round', methods=['POST'])
def do_round():
	# user must be logged in as moderator
	if int(session['id']) != -1:
		abort(401)

	# do the round
	with JediDatabase() as jedi_db:
		jedi_db.do_round()
	
	return redirect(url_for('moderator'))

@app.route('/register', methods=['POST'])
def register():
	client_id = int(request.form['id'])
	
	# check if client is in the database
	group = None
	with JediDatabase() as jedi_db:
		group = jedi_db.get_group(client_id)
	
	if(group is None):
		abort(400)

	session['id'] = client_id
	return redirect(url_for('group'))

@app.route('/group', methods=['GET'])
def group():
	if session['id'] == None:
		abort(401)
	
	client_id = int(session['id'])

	if client_id == -1:
		return redirect(url_for('moderator'))

	with JediDatabase() as jedi_db:
		group = jedi_db.get_group(client_id)
		
		if(group is None):
			abort(401)

		return render_template('group.html')

@app.route('/group_refresh', methods=['GET'])
def group_refresh():
	if session['id'] == None:
		abort(401)

	client_id = int(session['id'])

	if client_id == -1:
		abort(400)

	with JediDatabase() as jedi_db:
		return jedi_db.get_group_view(client_id)


@app.route('/group', methods=['POST'])
def group_post():
	if session['id'] == None:
		abort(401)

	client_id = int(session['id'])

	if client_id == -1:
		abort(400)

	claim_list = request.form.getlist('claim_list[]')
	hold_list = request.form.getlist('hold_list[]')

	#todo: type check and input validation

	with JediDatabase() as jedi_db:
		jedi_db.update_group_claims(client_id, claim_list)
		jedi_db.update_group_holds(client_id, hold_list)
		jedi_db.clean_claims_and_holds()
		jedi_db.ready_group(client_id)

		return jedi_db.get_group_view(client_id)

if __name__ == '__main__':
	try:
		MODERATOR_KEY = token_hex(32)
		print(f'{MODERATOR_KEY=}')
		with JediDatabase() as yoda:
			yoda.create_tables()
			# todo: read candidate list from configuration file
			yoda.insert_test_data()
		
		app.secret_key = token_hex(32)

		app.run(host='0.0.0.0')
	except KeyboardInterrupt:
		print('done')
