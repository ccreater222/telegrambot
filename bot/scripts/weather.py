from scripts import script
from telegram.ext import CallbackContext
import telegram
import requests
import config
import json
import wcwidth
from tabulate import tabulate
@script.command()
def weather(update:telegram.Update=None, context:CallbackContext=None):
    adcode = script.get_data("adcode")
    district = script.get_data("district")
    if adcode==None or district == None:
        location = script.get_location()
        if location == None:
            context.bot.send_message(chat_id=update.effective_chat.id, text="我不知道你在哪里诶，我能问你一下吗")
            return
        
        data = requests.get(f"https://restapi.amap.com/v3/geocode/regeo",params={
            "key":config.GAODEKEY,
            "location":f"{location['longitude']},{location['latitude']}"}
        ).json()
        if data["status"] == 0:
            context.bot.send_message(chat_id=update.effective_chat.id, text=json.dumps(data))
            return
        adcode = data["regeocode"]["addressComponent"]["adcode"]
        district = data["regeocode"]["addressComponent"]["district"]
        script.set_data("adcode",adcode)
        script.set_data("district",district)
    data = requests.get("https://restapi.amap.com/v3/weather/weatherInfo",params={
        "key":config.GAODEKEY,
        "city":adcode,
        "extensions":"all"
    }).json()
    if data["status"] == 0:
        context.bot.send_message(chat_id=update.effective_chat.id, text=json.dumps(data))
        return
    for forcast in data["forecasts"]:
        if forcast["city"] == district:
            table = processcast(forcast["casts"][0])
            context.bot.send_message(chat_id=update.effective_chat.id, text="```\n"+table+"\n```",parse_mode=telegram.constants.PARSEMODE_MARKDOWN_V2)
            if "雨" in table:
                context.bot.send_message(chat_id=update.effective_chat.id, text="今天有雨，记得带伞🌂哦")
            return



def processcast(cast:dict)->str:
    return tabulate([
        ["日期",cast["date"]],
        ["白天天气",f"{cast['dayweather']} {cast['daytemp']}°C"],
        ["夜间天气",f"{cast['nightweather']} {cast['nighttemp']}°C"]
    ], tablefmt='fancy_grid')
