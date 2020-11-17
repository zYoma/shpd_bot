# Telegram бот. Уведомления об авариях на сети, база контактов.
### Используется метод получения обновлений - webhook. Взаимодействие с API Telegram без сторонних библиотек, на requests. Для реализации используется фреймворк Flask, web-сервер - gunicorn. Хранение данных - sqlite3.

### Функционал бота:
Доступ к боту ограничен. Добавление пользователя в список доступа администратором командой add. 
Пользователям доступна клавиатура с кнопками, по нажатию которых бот присылает актуальные аварии.
Список аварий синхронизируется с сервером МТС раз в 10 секунд.
В inline-режиме бота реализован поиск контактов управляющих компаний/старших по дому.
Администратору доступно добаление и удаление контактов из БД.

### Установка: 

Установите зависимости:
```
pip install -r requirements.txt
```
Выполните миграции:
```
python manage.py db init
python manage.py db migrate
```

