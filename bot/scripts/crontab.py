from apscheduler.triggers.cron import CronTrigger
from telegram.ext import CallbackContext
import telegram
from pytz import timezone
from scripts import script
import constrant
import os
import json
@script.command("crontab",description="添加一个定时任务")
def crontab(update:telegram.Update, context:CallbackContext):
    if len(context.args) < 6:
        error_message="""**ERROR**: crontab 的参数必须大于等于6个"""
        context.bot.send_message(chat_id=update.effective_chat.id, text=error_message,parse_mode="MarkdownV2")
        return
    cron = ' '.join(context.args[:5])
    task = context.args[5]
    args = []
    if len(context.args) > 6 :
        args = context.args[6:]
    func = script.get_script(task)
    if func == None:
        error_message="""**ERROR**: 命令不存在"""
        context.bot.send_message(chat_id=update.effective_chat.id, text=error_message,parse_mode="MarkdownV2")
        return
    def callback(context:CallbackContext=None):
        func(update,context)
    context.args = args
    context.__setattr__("cron",cron)
    context.job_queue.run_custom(callback=callback,name=task, job_kwargs={"trigger": CronTrigger.from_crontab(cron,timezone=timezone('Asia/Shanghai'))} ,context=context)
    context.bot.send_message(chat_id=update.effective_chat.id, text="添加成功")
    savecron(update,context)

@script.command("listcron",description="列出当前的定时任务")
def listcron(update:telegram.Update, context:CallbackContext):
    message = "任务列表如下：\n"
    for num in range(len(context.job_queue.jobs())):
        job = context.job_queue.jobs()[num]
        message += f"{num+1}. {job.context.cron} {job.name} {''.join(job.context.args)} {job.next_t} {job.job.id}\n"
    context.bot.send_message(chat_id=update.effective_chat.id, text=message)

@script.command("delcron",description="根据id删除定时任务")
def delcron(update:telegram.Update, context:CallbackContext):
    if len(context.args)<1:
        context.bot.send_message(chat_id=update.effective_chat.id, text="缺少id参数")
        return
    jobs = context.job_queue.jobs()
    index = int(context.args[0]) - 1
    if index > len(jobs) or index < 0:
        context.bot.send_message(chat_id=update.effective_chat.id, text="无法找到对应任务")
        return
    jobs[index].schedule_removal()
    context.bot.send_message(chat_id=update.effective_chat.id, text="删除成功")
    savecron(update,context)


@script.command("readcron",description="从文件中读取保存的crontab")
def readcron(update:telegram.Update, context:CallbackContext):
    message = ""
    if not os.path.exists(constrant.store_cron):
        with open(constrant.store_cron,"w") as f:
            f.write(json.dumps([]))
    with open(constrant.store_cron,"r") as f:
        crontabs = json.loads(f.read())

    for cron in crontabs:
        func = script.get_script(cron["task"])
        if func == None:
            continue
        def callback(context:CallbackContext=None):
            func(update,context)
        context.args = cron["args"]
        context.__setattr__("cron",cron["cron"])
        context.job_queue.run_custom(callback=callback,name=cron["task"], job_kwargs={"trigger": CronTrigger.from_crontab(cron["cron"],timezone=timezone('Asia/Shanghai'))} ,context=context)
        message += f"加载: {cron['cron']} {cron['task']} {''.join(cron['args'])} \n"

    if message == "":
        message = "没有保存的cron"
    context.bot.send_message(chat_id=update.effective_chat.id, text=message)

@script.command("savecron",description="保存crontab到文件(会自动保存的哦)")
def savecron(update:telegram.Update, context:CallbackContext):
    cronlist = []
    for job in context.job_queue.jobs():
        cronlist.append({
            "cron":job.context.cron,
            "task":job.name,
            "args":job.context.args
        })
    with open(constrant.store_cron,"w") as f:
        f.write(json.dumps(cronlist))
    context.bot.send_message(chat_id=update.effective_chat.id, text="成功cron保存到文件")