import time
import requests
import functools
import logging

from environs import Env
from telegram import Update, ForceReply
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from google_spreadsheets_api import TelegramLogsHandler, detect_intent_texts


logger = logging.getLogger('Logger')


def start(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    update.message.reply_markdown_v2(
        fr'Здравствуйте {user.mention_markdown_v2()}\!',
        reply_markup=ForceReply(selective=True),
    )


def echo(project_id, session_id, update: Update, context: CallbackContext) -> None:
    """Echo the user message."""
    check = detect_intent_texts(project_id, session_id, [update.message.text], 'ru')
    update.message.reply_text(check)


def main(telegram_token, project_id, session_id) -> None:
    updater = Updater(telegram_token)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help_command))

    end = functools.partial(echo, project_id, session_id)
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, end))

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
    )
    logger.setLevel(logging.INFO)
    env = Env()
    env.read_env()
    telegram_token = env('TELEGRAM_TOKEN')
    reserve_telegram_token = env('RESERVE_TELEGRAM_TOKEN')
    project_id = env('PROJECT_ID')
    session_id = env('SESSION_ID')
    logger.addHandler(TelegramLogsHandler(reserve_telegram_token, session_id))
    logger.info('Telegram бот начал работу')
    try:
        main(telegram_token, project_id, session_id)
    except requests.exceptions.HTTPError:
        logger.error('Telegram бот упал с ошибкой HTTPError')
    except requests.exceptions.ReadTimeout:
        logger.debug('Telegram бот. Wait... I will try to send the request again')
    except requests.exceptions.ConnectionError:
        logger.error('Telegram бот упал с ошибкой ConnectionError')
        time.sleep(10)
