from flask import Flask, Response, request, render_template, session, abort, redirect, url_for
from json import loads, dumps
from secrets import token_hex

from jedi_database import JediDatabase

app = Flask(__name__)

MODERATOR_KEY = None

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

@app.route('/moderator', methods=['GET'])
def moderator():
	if session.get('id') != -1:
		abort(401)
	
	with JediDatabase() as jedi_db:
		moderator_view = jedi_db.get_moderator_total_view()
		return render_template('moderator.html', data=moderator_view)	

@app.route('/moderator/initialize', methods=['POST'])
def moderator_initialize():
	if session.get('id') != -1:
		abort(401)
	if 'file' not in request.files:
		return ('No file provided.', 400)
	
	response_file = request.files['file']
	
	if not response_file.filename:
		return ('No file selected.', 400)

	with JediDatabase() as jedi_db:
		try:
			jedi_db.initialize_from_google_form_response_csv(response_file)
		except Exception as ex:
			print(f'Error reading response file; {ex}')
			print('Please ensure that you are uploading the .csv file exported from Google Forms.')
		return redirect(url_for('moderator'))

		
	
@app.route('/moderator/update/candidates', methods=['POST'])
def moderator_update_candidates():
	# user must be logged in as moderator
	if session.get('id') != -1:
		abort(401)
	
	candidates_json = request.form.get("candidate_list")

	candidates = loads(candidates_json)

	with JediDatabase() as jedi_db:
		jedi_db.post_moderator_candidates(candidates)
		return jedi_db.get_moderator_candidates()

@app.route('/moderator/do_round', methods=['POST'])
def do_round():
	# user must be logged in as moderator
	if session.get('id') != -1:
		abort(401)

	# do the round
	with JediDatabase() as jedi_db:
		jedi_db.do_round()
		return jedi_db.get_moderator_view()

@app.route('/moderator/refresh/candidates', methods=['GET'])
def moderator_refresh_candidates():
	# user must be logged in as moderator
	if session.get('id') != -1:
		abort(401)

	with JediDatabase() as jedi_db:
		return jedi_db.get_moderator_candidates()

@app.route('/moderator/refresh/groups', methods=['GET'])
def moderator_refresh_groups():
	# user must be logged in as moderator
	if session.get('id') != -1:
		abort(401)

	with JediDatabase() as jedi_db:
		return jedi_db.get_moderator_groups()

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
	if session.get('id') is None:
		return redirect(url_for('index'))
	
	client_id = int(session['id'])

	if client_id == -1:
		return redirect(url_for('moderator'))

	with JediDatabase() as jedi_db:
		group = jedi_db.get_group(client_id)
		
		if(group is None):
			abort(401)

		return render_template('group.html')

@app.route('/group/poll', methods=['GET'])
def group_poll():
	if session.get('id') is None:
		abort(401)

	client_id = int(session['id'])

	if client_id == -1:
		abort(400)

	with JediDatabase() as jedi_db:
		_, ready = jedi_db.get_group(client_id)
		return dumps(ready)

@app.route('/group/refresh', methods=['GET'])
def group_refresh():
	if session.get('id') is None:
		abort(401)

	client_id = int(session['id'])

	if client_id == -1:
		abort(400)

	with JediDatabase() as jedi_db:
		return jedi_db.get_group_view(client_id)


@app.route('/group', methods=['POST'])
def group_post():
	if session.get('id') is None:
		abort(401)

	client_id = int(session['id'])

	if client_id == -1:
		abort(400)

	claim_list = request.form.getlist('claim_list[]')
	hold_list = request.form.getlist('hold_list[]')

	with JediDatabase() as jedi_db:
		jedi_db.update_group_claims(client_id, claim_list)
		jedi_db.update_group_holds(client_id, hold_list)
		jedi_db.clean_claims_and_holds()
		jedi_db.ready_group(client_id)

		return jedi_db.get_group_view(client_id)

@app.route('/results', methods=['GET'])
def results():
	if session.get('id') is None:
		abort(401)
	
	client_id = int(session['id'])

	with JediDatabase() as jedi_db:
		if(client_id == -1):
			return Response(
				jedi_db.generate_moderator_results(), 
				mimetype='text/csv',
				headers={"Content-disposition": "attachment; filename=results.csv"})
		else:
			return Response(
				jedi_db.generate_results(client_id), 
				mimetype='text/csv',
				headers={"Content-disposition": "attachment; filename=results.csv"})

if __name__ == '__main__':
	try:
		MODERATOR_KEY = token_hex(32)
		print(f'{MODERATOR_KEY=}')
		with JediDatabase() as yoda:
			yoda.create_tables()
		
		app.secret_key = token_hex(32)

		app.run(host='0.0.0.0')
	except KeyboardInterrupt:
		print('done')
