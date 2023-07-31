import time
import requests
import functools
import logging

from environs import Env
from google.cloud import dialogflow
import telegram
from telegram import Update, ForceReply
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

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
        check = response.query_result.fulfillment_text
        return check


def start(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    update.message.reply_markdown_v2(
        fr'Здравствуйте {user.mention_markdown_v2()}\!',
        reply_markup=ForceReply(selective=True),
    )


def help_command(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /help is issued."""
    update.message.reply_text('Help!')


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
    env = Env()
    env.read_env()
    telegram_token = env('TELEGRAM_TOKEN')
    reserve_telegram_token = env('RESERVE_TELEGRAM_TOKEN')
    project_id = env('PROJECT_ID')
    session_id = env('SESSION_ID')
    logger.setLevel(logging.INFO)
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
