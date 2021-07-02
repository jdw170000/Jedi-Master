from flask import Flask
from core.class_definitions import Candidate, Group
from core.do_round import do_round
from jedi_database import JediDatabase

# todo: read candidate list from configuration file

app = Flask(__name__)

@app.route('/')
def hello():
	result = None
	with JediDatabase() as yoda:
		result = yoda.get_all_candidates()
		print(result)

		yoda.do_round()

		result = yoda.get_all_candidates()
		print(result)
		

	return ', '.join(candidate[1] for candidate in result)

if __name__ == '__main__':
	try:
		with JediDatabase() as yoda:
			yoda.create_tables()
			yoda.insert_test_data)
		app.run()
	except KeyboardInterrupt:
		print('done')
