
from flask import request
from flask import jsonify


from config import URL
from config import TOKEN
from config import IP
from config import write_json
from config import app
from config import sslify
from config import db
import requests


@app.route(f'/{TOKEN}/', methods=['POST'])
def index():
    print('work!')
    r = request.get_json()
    write_json(r)
    return jsonify(r)


if __name__ == '__main__':
    ip_port = IP.split(':')
    app.run(host=ip_port[0], port=ip_port[1], debug=True,
            ssl_context=('webhook_cert.pem', 'webhook_pkey.pem'))
