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
async def on_ready():
    root = pathlib.Path(common.getbotdir())
    print("Building App Info")
    if not hasattr(bot, 'appinfo'):
        bot.appinfo = await bot.application_info()
    owner = bot.appinfo.owner.id
    if root.joinpath("data/data.json").exists():
        print("Preloading data.json")  # TODO: Add server moderators, people who can control specific server.
    else:
        await common.makefile("data/data.json", "{}")
        print("No 'data.json' file found, creating.")
    data = await common.loadjson(root.joinpath("data/data.json"))
    if 'admins' not in data:
        data['admins'] = []
    if owner not in data['admins']:
        print("Owner not found in admin list, adding.")
        data['admins'].append(owner)
    await common.dumpjson(data, "data/data.json")

bot.run(os.environ['PICONTROLLER'], reconnect=True)
