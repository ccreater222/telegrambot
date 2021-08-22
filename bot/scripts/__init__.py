import typing as t
from telegram.ext import CommandHandler,MessageHandler,Filters, dispatcher
from telegram.update import Update
import constrant
from os.path import dirname, basename, isfile, join,exists
import json
import config
import glob
import telegram
class Scripts:
    def __init__(self):
        self.commandlist = {}
        self.data = None
    
    def get_script(self,script:str):
        command = self.commandlist.get(script)
        if command == None:
            return command
        return command["function"]

    def get_data(self,key:str,default:t.Any=None):
        if self.data == None:
            if not exists(constrant.script_data):
                with open(constrant.script_data,"w") as f:
                    f.write(json.dumps({}))
            with open(constrant.script_data,"r") as f:
                self.data = json.loads(f.read())
        value = self.data.get(key)
        if value == None:
            value = default
        return value
        
    def set_data(self,key:str,value:t.Any):
        if self.data == None:
            self.get_data("aaa")
        self.data[key] = value
        with open(constrant.script_data,"w") as f:
            f.write(json.dumps(self.data))


    def get_location(self):
        location = self.get_data("location")
        if location == None:
            location_keyboard = telegram.KeyboardButton(text="send_location", request_location=True)
            custom_keyboard = [[ location_keyboard ]]
            reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard)
            self.dispatcher.bot.send_message(chat_id=config.USERID, 
                        text="Would you mind sharing your location and contact with me?", 
                        reply_markup=reply_markup)
            return None
        
        return location

    def command(self,cmd_name="",**kwargs: t.Any) ->t.Callable:
        def commandwrap(f: t.Callable) -> t.Callable:
            
            if cmd_name=="":
                name = f.__name__
            else:
                name = cmd_name

            self.commandlist[name] = {
                "function":f,
                "description":kwargs.get("description"),
                "example":kwargs.get("example")
            }
            
            
            def wrapper(*args: t.Any, **kwargs:t.Any) -> t.Any:
                f(*args,**kwargs)
            return wrapper
        return commandwrap
    def register(self,dispatcher):
        self.dispatcher = dispatcher
        helpmessage = ""
        for command in self.commandlist:
            handler = CommandHandler(command, self.commandlist[command]["function"])
            self.dispatcher.add_handler(handler)
            example = ""
            description = ""
            if self.commandlist[command]["description"]!=None:
                description = self.commandlist[command]["description"]
                description = description.splitlines()
                for i in range(len(description)):
                    line = description[i]
                    if len(line) == 0:
                        continue
                    if line[0] != " ":
                        line = "        " + line
                    description[i] = line
                description = "\n".join(description)
                
            else:
                description = "        None"
            description = "\n    description: \n"+description+"\n"

            if self.commandlist[command]["example"] != None:
                example = self.commandlist[command]["example"]
                example = example.splitlines()
                for i in range(len(example)):
                    line = example[i]
                    if len(line) == 0:
                        continue
                    if line[0] != " ":
                        line = "        " + line
                    example[i] = line
                example = "\n".join(example)
            else:
                example = "        None"
            example = "\n    example: \n" + example + "\n"
            helpmessage+="{command}:{description}{example}".format(command = command,description=description,example=example)

        helpmessage = "commands:\n    " + ",".join(self.commandlist.keys())+"\n"+helpmessage
        # @TODO: 优化helper,实现多级查询
        def helper(update,context):            
            context.bot.send_message(chat_id=update.effective_chat.id, text=helpmessage)
        handler = CommandHandler("help", helper)
        self.dispatcher.add_handler(handler)

        def unknown(update, context):
            context.bot.send_message(chat_id=update.effective_chat.id, text="不好意思啊，理解不能")
        
        unknown_handler = MessageHandler(Filters.command, unknown)
        self.dispatcher.add_handler(unknown_handler)
        def set_location(update:Update, context):
            script.set_data("location",{"latitude":update.message.location.latitude,"longitude":update.message.location.longitude})
            context.bot.send_message(chat_id=update.effective_chat.id, text="保存经纬度成功")
        location_handler = MessageHandler(Filters.location, set_location)
        self.dispatcher.add_handler(location_handler)
script = Scripts()

modules = glob.glob(join(dirname(__file__), "*.py"))
__all__ = [ basename(f)[:-3] for f in modules if isfile(f) and not f.endswith('__init__.py')]
__all__.append("script")
