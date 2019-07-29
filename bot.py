# -*- coding: utf-8 -*-

"""
Assistant Bot to send some services.
"""

import logging
import sys
import yaml
import requests
import bs4

from telegram import ChatAction
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from functools import wraps


logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s: [%(levelname)s] "%(name)s" -> %(message)s')

logger = logging.getLogger()
logger.info("Running " + sys.argv[0])

# Set up setting
logger.info("Load setting from config file")
with open('config.yaml') as stream:
    config = yaml.load(stream, Loader=yaml.FullLoader)

TOKEN = config['TOKEN']

REQUEST_KWARGS = {
    'proxy_url': config['PROXY']['url'],
}

MESSAGES = {
    'start': config['MESSAGES']['start'],
    'unknown': config['MESSAGES']['unknown']
}


def send_typing_action(func):
    """Sends typing action while processing func command."""

    @wraps(func)
    def command_func(update, context, *args, **kwargs):
        context.bot.send_chat_action(chat_id=update.effective_message.chat_id, action=ChatAction.TYPING)
        return func(update, context,  *args, **kwargs)

    return command_func


def get_weather():
    url = 'https://www.gismeteo.ru/weather-irkutsk-4787/now/'

    response = requests.get(url, headers={"User-Agent": "Firefox/68.0"})
    response.raise_for_status()

    soup = bs4.BeautifulSoup(response.text, features="html.parser")
    el = soup.select('span.nowvalue__text_l')
    return el[0].text


@send_typing_action
def start(update, context):
    chat_id = update.message.chat.id
    username = update.message.chat.first_name
    text = MESSAGES['start'] % username

    logger.info(f'handler: start; username: {username}')
    context.bot.send_message(chat_id=chat_id, text=text)


@send_typing_action
def unknown(update, context):
    chat_id = update.message.chat.id
    username = update.message.chat.first_name
    text = MESSAGES['unknown']

    logger.info(f'handler: unknown; username: {username}')
    context.bot.send_message(chat_id=chat_id, text=text)


@send_typing_action
def weather(update, context):
    chat_id = update.message.chat.id
    username = update.message.chat.first_name
    text = get_weather()

    logger.info(f'handler: weather; username: {username}')
    context.bot.send_message(chat_id=chat_id, text=text)


# Handlers
logger.info("Setting handlers")
updater = Updater(token=TOKEN, request_kwargs=REQUEST_KWARGS, use_context=True)
dispatcher = updater.dispatcher

dispatcher.add_handler(CommandHandler('start', start))
dispatcher.add_handler(CommandHandler('weather', weather))

dispatcher.add_handler(MessageHandler(Filters.command, unknown))

logger.info("Starting polling")
updater.start_polling()
updater.idle()
