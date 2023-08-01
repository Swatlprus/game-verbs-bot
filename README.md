# ВК и Telegram бот на DialogFlow
Два бота: ВК и Telegram, которые отвечают на основе данных из DialogFlow

<img src="./assets/tgbot.gif"/>

## Подготовка к запуску
Для запуска сайта вам понадобится Python 3.8+ версии. 

Чтобы скачать код с Github, используйте команду:
```shell
git clone git@github.com:Swatlprus/game-verbs-bot.git
```
Для создания виртуального окружения используйте команду (Linux):
```shell
python3 -m venv venv
```
Для установки зависимостей, используйте команду:
```shell
pip3 install -r requirements.txt
```

## Настройка переменных окружения
Пример .env файла
```
TELEGRAM_TOKEN=53423430081:AAHFoYxtfzunbFm31jdfsdfsdfsdf
RESERVE_TELEGRAM_TOKEN=605454520:AAExux2WuWthjjftrre
GOOGLE_APPLICATION_CREDENTIALS=/gcloud/application_default_credentials.json
PROJECT_ID=dvmn-343243
SESSION_ID=3145354354
VK_TOKEN=vk1.a.N0bsDBLyLESh35U7bfimAtiWjc9xhHeuF_vC
BASE_QUESTIONS=questions.json
```
TELEGRAM_TOKEN - Токен от Telegram бота. Создать его можно через https://t.me/BotFather<br>
RESERVE_TELEGRAM_TOKEN - Токен от Telegram бота, который будет оповещать вас об ошибках. Создать его можно через https://t.me/BotFather<br>
GOOGLE_APPLICATION_CREDENTIALS - Путь к файлу credentials.json. Набор ключей от аккаунта Google (https://cloud.google.com/docs/authentication/api-keys)<br>
PROJECT_ID - ID проекта из DialogFlow<br>
SESSION_ID - Уникальный ID чата. Узнать свой можно с помощью бота - https://t.me/userinfobot<br>
VK_TOKEN - Токен от группы ВК. Получить его можно в настройках группы<br>
BASE_QUESTIONS - путь к JSON файлу с набором вопросов для обучения DialogFlow<br>

## Обучить DialogFlow набору фраз
В файле questions.json лежит пример для обучения фразам
Запуск скрипта для обучения
```shell
python3 learn_dialogflow.py
```

## Как запустить локально
Команда для запуска проекта локально (Linux).
Запуск бота в Telegram
```shell
python3 tg_bot.py
```

Запуск бота в Вконтакте
```shell
python3 vk_bot.py
```

## Как запустить на сервере
Необходимо настроить демонизацию (https://dvmn.org/encyclopedia/deploy/systemd-tutorial/).
Для этого в папке `etc/systemd/system` создайте файл `tgbot.service` с таким содержимым:

```
[Service]
ExecStart=/opt/game-verbs-bot/venv/bin/python3 /opt/game-verbs-bot/tg_bot.py
Restart=always

[Install]
WantedBy=multi-user.target
```

ExecStart - указываем путь к python3 (который принадлежит к venv) и путь к скрипту для запуска бота (tg_bot.py)<br>
Restart - Перезапускает бота, если произошел какой-либо сбой<br>
WantedBy - Запускает бота, если сервер перезагрузился<br>

Далее запустите юнит с помощью команды:
```shell
systemctl start tgbot
```

И добавьте юнит в автозагрузку сервера:
```shell
systemctl enable tgbot
```

Проверить, запустился ли юнит, используйте команду:
```shell
journalctl -u tgbot
```

Аналогично нужно проделать и для Вконтакте-бота.

## Цели проекта

Код написан в учебных целях — это урок в курсе по Python и веб-разработке на сайте [Devman](https://dvmn.org).