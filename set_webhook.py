import requests
from config import TOKEN, IP


cert_file_path = 'webhook_cert.pem'
key_file_path = 'webhook_pkey.pem'

url = 'https://api.telegram.org/bot' + TOKEN + '/deleteWebHook'
r = requests.get(url)
print(r.status_code)
print(r.text)
print('----------------------------------------')

url = 'https://api.telegram.org/bot' + TOKEN + \
    '/setWebhook?url=https://' + IP + '/' + TOKEN + '/'
files = {'certificate': open('webhook_cert.pem', 'rb')}
cert = (cert_file_path, key_file_path)

r = requests.post(url, files=files)
print(r.status_code)
print(r.text)
print('----------------------------------------')

url = 'https://api.telegram.org/bot' + TOKEN + '/getWebhookInfo'
r = requests.get(url)
print(r.status_code)
print(r.text)
