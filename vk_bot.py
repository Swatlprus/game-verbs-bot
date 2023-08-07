import time
import random
import logging
import requests

from environs import Env
import vk_api as vk
from vk_api.longpoll import VkLongPoll, VkEventType
from google_cloud_api import TelegramLogsHandler, detect_intent_texts


logger = logging.getLogger('Logger')


def answer_question(event, vk_api, project_id):
    user_id = event.user_id
    fallback, intent_question = detect_intent_texts(project_id, f'vk-{user_id}', [event.text], 'ru')
    if fallback:
        return None

    if intent_question:
        vk_api.messages.send(
            user_id=event.user_id,
            message=intent_question,
            random_id=random.randint(1, 1000)
        )


def main():
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
                answer_question(event, vk_api, project_id)
    except requests.exceptions.HTTPError:
        logger.error('ВК бот упал с ошибкой HTTPError')
    except requests.exceptions.ReadTimeout:
        logger.debug('ВК бот. Wait... I will try to send the request again')
    except requests.exceptions.ConnectionError:
        logger.error('ВК бот упал с ошибкой ConnectionError')
        time.sleep(10)


if __name__ == '__main__':
    main()
