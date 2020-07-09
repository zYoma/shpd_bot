# pip install -U python-dotenv
from dotenv import load_dotenv
import os

load_dotenv()
TOKEN = os.getenv("TOKEN")
URL = 'https://api.telegram.org/bot' + TOKEN + '/'
IP = os.getenv("IP")


def write_json(data, filename='answer.json'):
    with open(filename, 'w') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
