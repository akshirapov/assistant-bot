# -*- coding: utf-8 -*-

"""
Assistant Bot to send some services.
"""

import telegram
import logging
import sys
import yaml

from telegram import ChatAction
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from functools import wraps
from weather import Gismeteo
from datetime import time

# Logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s: [%(levelname)s] "%(name)s" -> %(message)s')

logger = logging.getLogger()
logger.info("Running " + sys.argv[0])


# Setting from config file
logger.info("Load setting from config file")
with open('config.yaml', 'rt', encoding='utf-8') as stream:
    config = yaml.load(stream, Loader=yaml.FullLoader)

TOKEN = config['TOKEN']
REQUEST_KWARGS = {
    'proxy_url': config['PROXY']['url']
}
MESSAGES = {
    'start': config['MESSAGES']['start'],
    'unknown': config['MESSAGES']['unknown'],
    'weather': config['MESSAGES']['weather']
}


def send_typing_action(func):
    """Sends typing action while processing func command."""

    @wraps(func)
    def command_func(update, context, *args, **kwargs):
        context.bot.send_chat_action(chat_id=update.effective_message.chat_id, action=ChatAction.TYPING)
        return func(update, context,  *args, **kwargs)

    return command_func


def get_weather():

    g = Gismeteo()
    t = g.now + g.today + g.tomorrow

    return MESSAGES['weather'] % t


@send_typing_action
def weather_daily(context: telegram.ext.CallbackContext):

    chat_id_ls = ['312042633', '340851588']
    weather_info = get_weather()

    for chat_id in chat_id_ls:
        context.bot.send_message(chat_id=chat_id,
                                 text=weather_info)
        logger.info('Send weather to %s' % chat_id)


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


#
logger.info("Setting handlers")
updater = Updater(token=TOKEN, request_kwargs=REQUEST_KWARGS, use_context=True)
dispatcher = updater.dispatcher
j = updater.job_queue

dispatcher.add_handler(CommandHandler('start', start))
dispatcher.add_handler(CommandHandler('weather', weather))
dispatcher.add_handler(MessageHandler(Filters.command, unknown))

next_t = time(9)  # at 9:00am
job_weather_daily = j.run_daily(weather_daily, time=next_t)


logger.info("Starting polling")
updater.start_polling()
updater.idle()
