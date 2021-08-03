from flask import Flask, Response, request, render_template, session, abort, redirect, url_for
import json
import secrets

from jedi_database import InitializerDatabase, GroupDatabase, ModeratorDatabase, Identity, Group, Candidate, Stake, GroupView, ModeratorView, InvalidGroupException, NotModeratorException

app = Flask(__name__)

MODERATOR_KEY = None

@app.route('/', methods=['GET'])
def index():
	with JediDatabase() as jedi_db:
		groups = jedi_db.get_all_groups()
		return render_template('index.html', data=groups)

@app.route('/moderator/<key>')
def moderator_key(key: str):
	# check if client is the moderator
	if key == MODERATOR_KEY:
		session['id'] = -1
		return redirect(url_for('moderator'))
	else:
		# user provided wrong key
		abort(401)

@app.route('/moderator', methods=['GET'])
def moderator():
	try:	
		with ModeratorDatabase() as mod_db:
			moderator_view = mod_db.get_view()
			return render_template('moderator.html', data=moderator_view)	
	except NotModeratorException:
		abort(401)

@app.route('/moderator/initialize', methods=['POST'])
def moderator_initialize():
	if session.get('id') != -1:
		abort(401)
	if 'file' not in request.files:
		return ('No file provided.', 400)
	
	response_file = request.files['file']
	
	if not response_file.filename:
		return ('No file selected.', 400)

	try:
		with ModeratorDatabase(session.get('id')) as mod_db:
				jedi_db.initialize_from_google_form_response_csv(response_file)
	except NotModeratorException:
		abort(401) 
	except Exception as ex:
		print(f'Error reading response file; {ex}')
		print('Please ensure that you are uploading the .csv file exported from Google Forms.')
	
	return redirect(url_for('moderator'))
	
@app.route('/moderator/update/candidates', methods=['POST'])
def moderator_update_candidates():
	candidates_json = request.form.get("candidate_list")

	candidates_dict = json.loads(candidates_json)

	candidates = [Candidate(id = c[0], name = c[1], group_id = c[2]) for c in candidates_dict]

	try:
		with ModeratorDatabase(session.get('id')) as mod_db:
			mod_db.post_candidates(candidates)
			return mod_db.get_all_candidates()
	except NotModeratorException:
		abort(401)

@app.route('/moderator/do_round', methods=['POST'])
def do_round():
	try:
		with ModeratorDatabase(session.get('id')) as mod_db:
			mod_db.do_round()
			return mod_db.get_view()
	except NotModeratorException:
		abort(401)

@app.route('/moderator/refresh/candidates', methods=['GET'])
def moderator_refresh_candidates():
	try:
		with ModeratorDatabase(session.get('id')) as mod_db:
			return mod_db.get_all_candidates()
	except NotModeratorException:
		abort(401)

@app.route('/moderator/refresh/groups', methods=['GET'])
def moderator_refresh_groups():
	try:
		with ModeratorDatabase(session.get('id')) as mod_db:
			return mod_db.get_moderator_groups()
	except NotModeratorException:
		abort(401)

@app.route('/register', methods=['POST'])
def register():
	client_id = int(request.form['id'])
	
	# verify that the given group exists
	try:
		with GroupDatabase(client_id) as group_db:
			_ = group_db.get_group()
	except InvalidGroupException:
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
	
	try:
		with GroupDatabase(client_id) as group_db:
			_ = group_db.get_group()
	except InvalidGroupException:
		abort(400)
	
	return render_template('group.html')

@app.route('/group/poll', methods=['GET'])
def group_poll():
	if session.get('id') is None:
		abort(401)

	client_id = int(session['id'])

	try:
		with GroupDatabase(client_id) as group_db:
			group = group_db.get_group()
			return json.dumps(group.ready)
	except InvalidGroupException:
		abort(400)

@app.route('/group/refresh', methods=['GET'])
def group_refresh():
	if session.get('id') is None:
		abort(401)

	client_id = int(session['id'])

	try:
		with GroupDatabase(client_id) as group_db:
			group_view = group_db.get_view()
			return json.dumps(group_view)
	except InvalidGroupException:
		abort(400)


@app.route('/group', methods=['POST'])
def group_post():
	if session.get('id') is None:
		abort(401)

	client_id = int(session['id'])

	claim_list = request.form.getlist('claim_list[]')
	claims = [Stake(group_id = client_id, candidate_id = int(claim)) for claim in claim_list]

	hold_list = request.form.getlist('hold_list[]')
	holds = [Stake(group_id = client_id, candidate_id = int(hold)) for hold in hold_list]
	
	try:
		with GroupDatabase(client_id) as group_db:
			group_db.update_claims(claims)
			group_db.update_holds(holds)
			#testing new robustness measures; might not need cleaning step
			#group_db.clean_claims_and_holds() 
			group_db.ready()
			return group_db.get_view()
	except InvalidGroupException:
		abort(400)

@app.route('/results', methods=['GET'])
def results():
	if session.get('id') is None:
		abort(401)
	
	client_id = int(session['id'])

	if client_id == -1:
		with ModeratorDatabase(client_id) as mod_db:
			return Response(
				mod_db.generate_results(), 
				mimetype='text/csv',
				headers={"Content-disposition": "attachment; filename=results.csv"})
	else:
		try:
			with GroupDatabase(client_id) as group_db:
				return Response(
					group_db.generate_results(), 
					mimetype='text/csv',
					headers={"Content-disposition": "attachment; filename=results.csv"})
		except InvalidGroupException:
			abort(400)

if __name__ == '__main__':
	try:
		MODERATOR_KEY = secrets.token_hex(32)
		print(f'{MODERATOR_KEY=}')
		with InitializerDatabase() as init_db:
			init_db.create_tables()
		
		app.secret_key = secrets.token_hex(32)

		app.run(host='0.0.0.0')
	except KeyboardInterrupt:
		print('done')
