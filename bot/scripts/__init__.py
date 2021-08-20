import typing as t
from telegram.ext import CommandHandler,MessageHandler,Filters
from os.path import dirname, basename, isfile, join
import glob
class Scripts:
    def __init__(self):
        self.commandlist = {}
    
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
        def helper(update,context):            
            context.bot.send_message(chat_id=update.effective_chat.id, text=helpmessage)
        handler = CommandHandler("help", helper)
        self.dispatcher.add_handler(handler)

        def unknown(update, context):
            context.bot.send_message(chat_id=update.effective_chat.id, text="不好意思啊，理解不能")
        
        unknown_handler = MessageHandler(Filters.command, unknown)
        self.dispatcher.add_handler(unknown_handler)
script = Scripts()

modules = glob.glob(join(dirname(__file__), "*.py"))
__all__ = [ basename(f)[:-3] for f in modules if isfile(f) and not f.endswith('__init__.py')]
__all__.append("script")
