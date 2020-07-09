from flask import Flask
# pip install Flask-SSLify
from flask_sslify import SSLify
from flask import request
from flask import jsonify

from config import URL
from config import TOKEN
from config import write_json
import requests
import json


app = Flask(__name__)
sslify = SSLify(app)


@app.route('/TOKEN/', methods=['POST'])
def index():
	print('work!')
	r = request.get_json()
	write_json(r)
    return jsonify(r)


if __name__ == '__main__':
    app.run(host='176.57.215.48', port=443, debug=True,
            ssl_context=('webhook_cert.pem', 'webhook_pkey.pem'))
