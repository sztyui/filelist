from . import app
from flask import jsonify

@app.errorhandler(404)
def custom404error(error):
	response = jsonify({'message': error.description})
	response.status_code = 404
	response.status = 'error.Bad Request'
	return response