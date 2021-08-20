from scripts import script
@script.command()
def weather(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="天气测试")
