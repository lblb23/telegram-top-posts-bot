# -*- coding: utf-8 -*-
import argparse
import logging
import time

import instaloader
import yaml
from chatbase import Message
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
)
from tinydb import TinyDB, Query

from utils import get_top_posts, send_limit_message

# Mac OS SSL problem
# import ssl
# ssl._create_default_https_context = ssl._create_unverified_context

parser = argparse.ArgumentParser()
parser.add_argument(
    "--config_path", default="config.yml", dest="config_path", help="Path to config"
)
parser.add_argument(
    "--db_users",
    default="db_users.json",
    dest="db_users_path",
    help="Path to database of users",
)
parser.add_argument(
    "--db_users_limits",
    default="db_users_limits.json",
    dest="db_users_limits_path",
    help="Path to database of limits",
)

args = parser.parse_args()
config_path = args.config_path
db_users_path = args.db_users_path
db_users_limits_path = args.db_users_limits_path


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
db_users = TinyDB(db_users_path)
messages = config["messages"]
messages_limit = config["messages_limit"]

L = instaloader.Instaloader(
    sleep=True,
    download_geotags=False,
    filename_pattern="{shortcode}",
    quiet=False,
    download_video_thumbnails=False,
    download_comments=False,
)

if config["authorization"]:
    L.load_session_from_file(config["login"])


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

        db_limits = TinyDB(db_users_limits_path)

        username = update.message.from_user.name
        chat_id = update.message.chat.id
        profile_url = update.message.text

        db_limits.insert({"user": username})

        count_messages = len(db_limits.search(query.user == username))

        if count_messages <= messages_limit:
            context.bot.send_message(
                chat_id=chat_id,
                text=messages["loading"].format(count_messages, messages_limit),
            )
            result, traceback = get_top_posts(
                L,
                context,
                chat_id,
                messages,
                profile_url,
                top_n=config["top_n"],
                lookback_posts=config["lookback_posts"],
            )
        else:
            result, traceback = send_limit_message(context, chat_id, messages)

        # Print to pythonanywhere log
        print(
            username,
            time.ctime(int(time.time())),
            profile_url,
            result,
            traceback,
            sep="    ",
            flush=True,
        )

        # Send data to chatbase
        msg = Message(
            api_key=config["chatbase_token"], user_id=username, message=profile_url
        )
        msg.send()

        # Add user and their chat id to database if not exists
        user_exist = db_users.search(query.user == username)
        if len(user_exist) == 0:
            db_users.insert({"user": username, "chat_id": chat_id})


if __name__ == "__main__":
    main()
