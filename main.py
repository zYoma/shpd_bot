
from flask import request
from flask import jsonify

from models import User
from config import URL
from config import TOKEN
from config import IP
from config import write_json
from config import app
from config import sslify
from config import db
import requests
import re


def send_Message(chat_id, text, kb=None):
    url = URL + 'sendMessage'

    kb_markup = {'resize_keyboard': True, 'keyboard': [
        [{'text': 'Аварии ШПД'}, {'text': 'Добавить контакт'}], [{'text': 'Аварии КТВ'}, {'text': 'Аварии ИБП'}, {'text': 'Аварии RX'}]]}
    answer = {'chat_id': chat_id, 'text': text, 'parse_mode': 'Markdown'}
    if kb is not None:
        answer['reply_markup'] = kb_markup
    r = requests.post(url, json=answer)
    return r.json()


def check_user(first_name, chat_id):
    '''
    Проверяем имеет ли пользователь доступ к боту.
    Если доступа нет, уведомляем админа.
    '''
    user_hash = str(first_name) + str(chat_id)
    exists_user = db.session.query(User.id).filter_by(
        user_hash=user_hash).scalar() is not None
    if exists_user == False:
        text = f'{first_name}, Вы не имеете доступа к этой информации!\nЧтобы запросить доступ [оставьте заявку](http://t.me/zYoma_krd)'
        send_Message(chat_id, text=text)
        send_Message(chat_id=261552302, text=f'* {user_hash} * пытается получить доступ.')
    return exists_user


def is_admin(chat_id):
    if chat_id == 261552302:
        return True
    return False


def add_user(message):
    try:
        user_hash = message.split()[1].strip().replace(' ', '')
    except IndexError:
        send_Message(chat_id=261552302, text='Не верный формат!')
    else:
        user = User(user_hash=user_hash)
        db.session.add(user)
        db.session.commit()


def send_event(chat_id, input):
    with open(f'/root/{input}', 'r') as f:
        event_list = f.readlines()

    if len(event_list) > 150:
        # Делим сообщение на несколько если оно очень длинное
        n = 150
        messages_list = [event_list[i:i + n]
                         for i in range(0, len(event_list), n)]
        for i in messages_list:
            text = ''.join(i)
            send_Message(chat_id, text=text, kb=1)
    else:
        text = ''.join(event_list)
        send_Message(chat_id, text=text, kb=1)


@app.route(f'/{TOKEN}/', methods=['POST'])
def index():

    r = request.get_json()
    if 'callback_query' in r:
        callback_data = r['callback_query']['data']
        callback_from_chat_id = r['callback_query']['message']['chat']['id']
        callback_message_id = r['callback_query']['message']['message_id']
        first_name = r['callback_query']['from']['first_name']
        chat_id = callback_from_chat_id
        message_id = callback_message_id
    else:
        chat_id = r['message']['chat']['id']
        first_name = r['message']['from']['first_name']
        message = r['message'].get('text')

        access = check_user(first_name, chat_id)
        if not access:
            return jsonify(r)

        if message:
            if re.search(r'add', message):
                # Добавление пользователя.
                if is_admin(chat_id):
                    add_user(message)

            elif message == 'Аварии ШПД':
                send_event(chat_id, input='input.txt')

            elif message == 'Аварии КТВ':
                send_event(chat_id, input='input_ktv.txt')

            elif message == 'Аварии ИБП':
                send_event(chat_id, input='input_ups.txt')

            elif message == 'Аварии RX':
                send_event(chat_id, input='input_rx.txt')

            else:
                text = '*МТС-ШПД-БОТ*\nДля получения информации по авариям на сети воспользуйтесь соответствующими клавишами.\nСписок аварий обновляется раз в 10 минут.\nДля поиска контактов УК/старших по дому отправте адрес.'
                send_Message(chat_id, text=text, kb=1)
                # d = User.query.all()
                # print(d)

        write_json(r)
        return jsonify(r)


if __name__ == '__main__':
    ip_port = IP.split(':')
    app.run(host=ip_port[0], port=ip_port[1], debug=True,
            ssl_context=('webhook_cert.pem', 'webhook_pkey.pem'))
