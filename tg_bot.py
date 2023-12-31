import time
import requests
import functools
import logging

from environs import Env
from telegram import Update, ForceReply
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from google_cloud_api import TelegramLogsHandler, detect_intent_texts


logger = logging.getLogger('Logger')


def start(update: Update, context: CallbackContext) -> None:
    user = update.effective_user
    update.message.reply_markdown_v2(
        fr'Здравствуйте {user.mention_markdown_v2()}\!',
        reply_markup=ForceReply(selective=True),
    )


def answer_question(project_id, update: Update, context: CallbackContext) -> None:
    chat_id = update.message.chat_id
    fallback, intent_question = detect_intent_texts(project_id, f'tg-{chat_id}', update.message.text, 'ru')
    update.message.reply_text(intent_question)


def start_tg_bot(telegram_token, project_id) -> None:
    updater = Updater(telegram_token)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start))

    answer = functools.partial(answer_question, project_id)
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, answer))

    updater.start_polling()
    updater.idle()


def main():
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
    )
    logger.setLevel(logging.INFO)
    env = Env()
    env.read_env()
    telegram_token = env('TELEGRAM_TOKEN')
    reserve_telegram_token = env('RESERVE_TELEGRAM_TOKEN')
    project_id = env('PROJECT_ID')
    admin_tg_id = env('ADMIN_TG_ID')
    logger.addHandler(TelegramLogsHandler(reserve_telegram_token, admin_tg_id))
    logger.info('Telegram бот начал работу')
    try:
        start_tg_bot(telegram_token, project_id)
    except requests.exceptions.HTTPError:
        logger.error('Telegram бот упал с ошибкой HTTPError')
    except requests.exceptions.ReadTimeout:
        logger.debug('Telegram бот. Wait... I will try to send the request again')
    except requests.exceptions.ConnectionError:
        logger.error('Telegram бот упал с ошибкой ConnectionError')
        time.sleep(10)


if __name__ == '__main__':
    main()
