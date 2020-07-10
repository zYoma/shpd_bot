
from flask import request
from flask import jsonify
from sqlalchemy import func

from models import User, Contact
from config import URL
from config import TOKEN
from config import IP
from config import write_json
from config import app
from config import sslify
from config import db
import requests
import re
import json

CONTACTS = {}


def send_Message(chat_id, text, kb=None):
    url = URL + 'sendMessage'

    kb_markup = {'resize_keyboard': True, 'keyboard': [
        [{'text': 'Аварии ШПД'}, {'text': 'Добавить контакт'}], [{'text': 'Аварии КТВ'}, {'text': 'Аварии ИБП'}, {'text': 'Аварии RX'}]]}
    answer = {'chat_id': chat_id, 'text': text, 'parse_mode': 'Markdown'}
    if kb is not None:
        answer['reply_markup'] = kb_markup
    r = requests.post(url, json=answer)
    return r.json()


def edit_Message(chat_id, message_id, text):
    url = URL + 'editMessageText'
    answer = {'chat_id': chat_id, 'message_id': message_id,
              'text': text, 'parse_mode': 'HTML'}
    r = requests.post(url, json=answer)
    return r.json()


def send_inline_results(id, admin, result):
    url = URL + 'answerInlineQuery'
    results = []
    for contact in result:
        input_message_content = {
            'message_text': contact.date, 'parse_mode': 'Markdown'}
        data = {
            'type': 'article',
            'title': contact.date,
            'id': contact.id,
            'input_message_content': input_message_content
        }
        if admin:
            date = f'delete__{contact.id}'
            kb_markup = {'inline_keyboard': [
                [{'text': 'Удалить', 'callback_data': date}]]}
            data['reply_markup'] = kb_markup
        results.append(data)

    answer = {
        'inline_query_id': id,
        'results': json.dumps(results),
    }
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


def search(query):
    re_start_word = r"(^|\s)%s"
    text = re.escape(query.lower())
    date = Contact.query.all()
    result = [contact for contact in date if re.search(
        re_start_word % text, str(contact.date.lower()))]

    return result


def delete_contact(id):
    exists_contact = db.session.query(
        Contact.id).filter_by(id=id).scalar() is not None
    if exists_contact:
        contact = Contact.query.filter(Contact.id == id).delete()
        db.session.commit()
        return True
    return False


def create_contact(message):
    contact = Contact(date=message)
    db.session.add(contact)
    db.session.commit()


@app.route(f'/{TOKEN}/', methods=['POST'])
def index():
    print(TOKEN)
    r = request.get_json()
    write_json(r)
    # если бот вызван в inlineрежиме
    if 'inline_query' in r:
        id = r['inline_query']['id']
        query = r['inline_query']['query']
        chat_id = r['inline_query']['from']['id']
        result = search(query)
        if result:
            admin = is_admin(chat_id)
            send_inline_results(id, admin, result)
        return jsonify(r)

    elif 'callback_query' in r:
        callback_data = r['callback_query']['data'].split('__')
        callback_from_chat_id = r['callback_query']['from']['id']
        first_name = r['callback_query']['from']['first_name']
        callback_message = r['callback_query'].get('message')
        if callback_message:
            callback_message_id = r['callback_query']['message']['message_id']
            callback_message_text = r['callback_query']['message']['text']

        if callback_data[0] == 'delete':
            if is_admin(callback_from_chat_id):
                delete = delete_contact(callback_data[1])
                text = 'Удалено!' if delete else 'ID не найден.'
                send_Message(callback_from_chat_id, text=text)

        return jsonify(r)

    else:
        chat_id = r['message']['chat']['id']
        first_name = r['message']['from']['first_name']
        message = r['message'].get('text')
        via_bot = r['message'].get('via_bot')

        access = check_user(first_name, chat_id)
        if not access:
            return jsonify(r)

        if message:
            if message == '/exit':
                CONTACTS.pop(chat_id, None)
                send_Message(chat_id, text='OK!')
                return jsonify(r)

            if chat_id in CONTACTS:
                if CONTACTS[chat_id] == 'adress':
                    create_contact(message)
                    CONTACTS.pop(chat_id, None)
                    send_Message(chat_id, text='Сохранено!')
                    return jsonify(r)

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

            elif message == 'Добавить контакт':
                if is_admin(chat_id):
                    CONTACTS[chat_id] = 'adress'
                    send_Message(
                        chat_id, text='Ввежите данные по следующему шаблону:\n*Адрес дома* _пробел_ *контактные данные*\nЕсли не хотите добавлять данные нажмите /exit')
                else:
                    send_Message(
                        chat_id, text='У вас нет доступа к добавлению!')

            else:
                if via_bot:
                    return jsonify(r)

                text = '*МТС-ШПД-БОТ*\nДля получения информации по авариям воспользуйтесь соответствующими клавишами.\nСписок аварий обновляется раз в *10 минут*.\nДля поиска контактов начните вводить сообщение:\n*@MTS_SHPD_Bot* _Адрес который ищите_'
                send_Message(chat_id, text=text, kb=1)

        return jsonify(r)


if __name__ == '__main__':
    ip_port = IP.split(':')
    app.run(host=ip_port[0], port=ip_port[1], debug=True,
            ssl_context=('webhook_cert.pem', 'webhook_pkey.pem'))
