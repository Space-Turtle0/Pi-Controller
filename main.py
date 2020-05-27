import ghau
from discord.ext import commands, tasks
import logging
import os
from tinydb import TinyDB, Query

# Logging Controller
logging.basicConfig(level=logging.INFO)

# Update Controller
update = ghau.Update(version="v0.0.1", repo="InValidFire/Pi-Controller", reboot=ghau.python("main.py"))
update.update()

# Discord Bot Controller
bot = commands.Bot(command_prefix="pi.")
cogs = ['cogs.core','cogs.servers']
if __name__ == '__main__':
    for cog in cogs:
        bot.load_extension(cog)


@bot.event
async def on_ready():
    print("Building App Info")
    if not hasattr(bot, 'appinfo'):
        bot.appinfo = await bot.application_info()
    print("Loading data.json")
    with TinyDB("data.json", indent=4) as data:  # adds owner to admin list if not present
        admins = data.table("admins")
        users = Query()
        owner = admins.search(users.id == bot.appinfo.owner.id)
        if len(owner) == 0:
            print("Owner not found in data.json, adding.")
            admins.insert({"id": bot.appinfo.owner.id})

bot.run(os.environ['PICONTROLLER'], reconnect=True)
