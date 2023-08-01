import time
import random
import logging
import requests
import telegram

from environs import Env
import vk_api as vk
from vk_api.longpoll import VkLongPoll, VkEventType
from google.cloud import dialogflow


logger = logging.getLogger('Logger')


class TelegramLogsHandler(logging.Handler):

    def __init__(self, telegram_token, chat_id):
        super().__init__()
        self.chat_id = chat_id
        self.tg_bot = telegram.Bot(token=telegram_token)

    def emit(self, record):
        log_entry = self.format(record)
        self.tg_bot.send_message(chat_id=self.chat_id, text=log_entry)


def detect_intent_texts(project_id, session_id, texts, language_code='ru'):
    session_client = dialogflow.SessionsClient()
    session = session_client.session_path(project_id, session_id)

    for text in texts:
        text_input = dialogflow.TextInput(text=text, language_code=language_code)

        query_input = dialogflow.QueryInput(text=text_input)

        response = session_client.detect_intent(
            request={"session": session, "query_input": query_input}
        )
        if response.query_result.intent.is_fallback:
            return None
        else:
            return response.query_result.fulfillment_text


def echo(event, vk_api, project_id, session_id):
    dialog_chat = detect_intent_texts(project_id, session_id, [event.text], 'ru')
    if dialog_chat:
        vk_api.messages.send(
            user_id=event.user_id,
            message=dialog_chat,
            random_id=random.randint(1, 1000)
        )


if __name__ == '__main__':
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
    )
    logger.setLevel(logging.INFO)
    env = Env()
    env.read_env()
    project_id = env('PROJECT_ID')
    session_id = env('SESSION_ID')
    vk_token = env('VK_TOKEN')
    reserve_telegram_token = env('RESERVE_TELEGRAM_TOKEN')
    vk_session = vk.VkApi(token=vk_token)
    vk_api = vk_session.get_api()
    longpoll = VkLongPoll(vk_session)
    logger.addHandler(TelegramLogsHandler(reserve_telegram_token, session_id))
    logger.info('ВК бот начал работу')
    try:
        for event in longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                echo(event, vk_api, project_id, session_id)
    except requests.exceptions.HTTPError:
        logger.error('ВК бот упал с ошибкой HTTPError')
    except requests.exceptions.ReadTimeout:
        logger.debug('ВК бот. Wait... I will try to send the request again')
    except requests.exceptions.ConnectionError:
        logger.error('ВК бот упал с ошибкой ConnectionError')
        time.sleep(10)
