# -*- coding: utf-8 -*-
import argparse
import logging
import time

import yaml
from chatbase import Message
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
)
from tinydb import TinyDB, Query

from utils import get_top_posts

# Mac OS SSL problem
# import ssl
# ssl._create_default_https_context = ssl._create_unverified_context

parser = argparse.ArgumentParser()
parser.add_argument(
    "--config_path", default="config.yml", dest="config_path", help="Path to config"
)

args = parser.parse_args()
config_path = args.config_path

with open(config_path) as file:
    config = yaml.load(file, Loader=yaml.FullLoader)

update_id = None

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
    filename=".log",
)

logger = logging.getLogger(__name__)
query = Query()
db_users = TinyDB("db_users.json")
messages = config["messages"]


def main():
    updater = Updater(config["telegram_token"], use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(MessageHandler(Filters.text, handle_message))
    dp.add_error_handler(error)
    updater.start_polling()
    updater.idle()


def start(update, context):
    update.message.reply_text(messages["start"])


def help(update, context):
    update.message.reply_text(messages["help"])


def error(update, context):
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def handle_message(update, context):

    if update.message:
        username = update.message.from_user.name
        chat_id = update.message.chat.id
        profile_url = update.message.text

        result, traceback = get_top_posts(
            context,
            chat_id,
            messages,
            profile_url,
            top_n=config["top_n"],
            lookback_posts=config["lookback_posts"],
        )

        # Print to pythonanywhere log
        print(
            username,
            time.ctime(int(time.time())),
            result,
            traceback,
            sep="    ",
            flush=True,
        )

        # Send data to chatbase
        msg = Message(api_key=config["chatbase_token"], user_id=username, message=profile_url)
        msg.send()

        # Add user and their chat id to database if not exists
        user_exist = db_users.search(query.user == username)
        if len(user_exist) == 0:
            db_users.insert({"user": username, "chat_id": chat_id})


if __name__ == "__main__":
    main()
