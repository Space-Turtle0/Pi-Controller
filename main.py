import ghau
from discord.ext import commands
import logging
import pathlib
import os
import core.common as common

# Logging Controller
logging.basicConfig(level=logging.INFO)

# Update Controller
update = ghau.Update(version="v0.0.1", repo="InValidFire/Pi-Controller", reboot=ghau.python("main.py"))
update.update()

# Discord Bot Controller
bot = commands.Bot(command_prefix="pi.")
cogs = ['cogs.core', 'cogs.servers']
if __name__ == '__main__':
    for cog in cogs:
        bot.load_extension(cog)


@bot.event
async def on_connect():
    root = pathlib.Path(common.getbotdir())
    if root.joinpath("data.json").exists():
        print("Loading data.json")
    else:
        await common.makefile("data.json", "{}")
        print("No 'data.json' file found, creating.")
    bot.appdata = await common.loadjson("data.json")
    if 'admins' not in bot.appdata:
        bot.appdata['admins'] = []
    if 'settings' not in bot.appdata:
        bot.appdata['settings'] = {}
    if 'serverjson' not in bot.appdata['settings']:
        bot.appdata['settings']['serverjson'] = "servers.json"


@bot.event
async def on_ready():
    print("Building App Info")
    if not hasattr(bot, 'appinfo'):
        bot.appinfo = await bot.application_info()
    owner = bot.appinfo.owner.id
    if owner not in bot.appdata['admins']:
        print("Owner not found in admin list, adding.")
        bot.appdata['admins'].append(owner)
    await common.dumpjson(bot.appdata, "data.json")

bot.run(os.environ['PICONTROLLER'], reconnect=True)
