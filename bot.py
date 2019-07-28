# -*- coding: utf-8 -*-

"""
Assistant Bot to send some services.
"""

import logging
import sys
import pprint
import yaml

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s: [%(levelname)s] "%(name)s" -> %(message)s')

logger = logging.getLogger()
logger.info("Running " + sys.argv[0])

# Set up setting
logger.info("Load setting from config file")
with open('config.yaml') as stream:
    config = yaml.load(stream, Loader=yaml.FullLoader)

TOKEN = config['TOKEN']
REQUEST_KWARGS = {'proxy_url': config['PROXY_SERVER']}
MESSAGES = {
    'start': config['MESSAGES']['start'],
    'unknown': config['MESSAGES']['unknown']
}


def start(update, context):
    chat_id = update.message.chat.id
    username = update.message.chat.first_name
    text = MESSAGES['start'] % username

    logger.info(f'handler: start; username: {username}')
    context.bot.send_message(chat_id=chat_id, text=text)


def unknown(update, context):
    chat_id = update.message.chat.id
    username = update.message.chat.first_name
    text = MESSAGES['unknown']

    logger.info(f'handler: unknown; username: {username}')
    context.bot.send_message(chat_id=chat_id, text=text)


# Handlers
logger.info("Setting handlers")
updater = Updater(token=TOKEN, request_kwargs=REQUEST_KWARGS, use_context=True)
dispatcher = updater.dispatcher

dispatcher.add_handler(CommandHandler('start', start))
dispatcher.add_handler(MessageHandler(Filters.command, unknown))

logger.info("Starting polling")
updater.start_polling()
