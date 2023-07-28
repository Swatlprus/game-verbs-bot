from environs import Env
import random

import vk_api as vk
from vk_api.longpoll import VkLongPoll, VkEventType
from google.cloud import dialogflow


def detect_intent_texts(project_id, session_id, texts, language_code='ru'):
    session_client = dialogflow.SessionsClient()
    session = session_client.session_path(project_id, session_id)

    for text in texts:
        text_input = dialogflow.TextInput(text=text, language_code=language_code)

        query_input = dialogflow.QueryInput(text=text_input)

        response = session_client.detect_intent(
            request={"session": session, "query_input": query_input}
        )
        check = response.query_result.fulfillment_text
        return check


def echo(event, vk_api, project_id, session_id):
    dialog_chat = detect_intent_texts(project_id, session_id, [event.text], 'ru')
    vk_api.messages.send(
        user_id=event.user_id,
        message=dialog_chat,
        random_id=random.randint(1, 1000)
    )


if __name__ == '__main__':
    env = Env()
    env.read_env()
    project_id = env('PROJECT_ID')
    session_id = env('SESSION_ID')
    vk_token = env('VK_TOKEN')
    vk_session = vk.VkApi(token=vk_token)
    vk_api = vk_session.get_api()
    longpoll = VkLongPoll(vk_session)
    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
            echo(event, vk_api, project_id, session_id)
