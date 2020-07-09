from flask import Flask
# pip install Flask-SSLify
from flask_sslify import SSLify
# pip install -U Flask-SQLAlchemy  #pip install flask-script
from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager
from flask_sqlalchemy import SQLAlchemy
# pip install flask-migrate

# pip install -U python-dotenv
from dotenv import load_dotenv
import os
import json

load_dotenv()
TOKEN = os.getenv("TOKEN")
URL = 'https://api.telegram.org/bot' + TOKEN + '/'
IP = os.getenv("IP")
DB_PATH = os.getenv("DB_PATH")

app = Flask(__name__)
sslify = SSLify(app)
app.config['SQLALCHEMY_DATABASE_URI'] = DB_PATH
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

migrate = Migrate(app, db)
manager = Manager(app)
manager.add_command('db', MigrateCommand)


def write_json(data, filename='answer.json'):
    with open(filename, 'w') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
