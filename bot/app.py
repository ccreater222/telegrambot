from telegram.ext import Updater
import logging
from telegram.ext import CommandHandler,MessageHandler,Filters
import config
from scripts import *
# init
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                     level=logging.DEBUG)
updater = Updater(token=config.TOKEN, use_context=True)
dispatcher = updater.dispatcher

# auth
def godie(update,context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Oh no I only talk to {user}".format(user=config.USERNAME))

godie_handler = MessageHandler((~Filters.chat(chat_id=config.USERID)), godie)
dispatcher.add_handler(godie_handler)



# test
@script.command("start",description="梦开始的地方")
def start(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="I'm a bot, please talk to me!I only talk to ccreater")

# start
script.register(dispatcher)
updater.start_webhook(
    listen='0.0.0.0',
    port=3000,
    webhook_url='https://bot.ccreater.top:8443/'
)