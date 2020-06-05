from discord.ext import commands, tasks
from cogs.core import is_admin
import core.common as common
import core.embed as ebed
import discord
import requests
import asyncio
import os


async def dircheck(directory) -> bool:
    print("Running dircheck")
    return os.path.exists(directory)


async def load_args(data: dict) -> dict:  # TODO: make recursive, possibly load all args for file on load.
    """Load args for the given dict. Replaces placeholders with their actual values"""
    print("Loading Args for dict: {}".format(str(data)))
    newdict = {}
    argdict = data['args']
    for key in data.keys():
        if key == 'args':
            continue
        item = data[key]
        for argkey in argdict.keys():
            if "#{}#".format(argkey) in item:
                item = item.replace('#{}#'.format(argkey), argdict[argkey])
                print("Loaded arg '{}' for item '{}', new value: {}".format(argkey, key, item))
        newdict[key] = item
    print(newdict)
    return newdict


async def download_file(url, save_file):  # move to thread
    """Download the given server and initialize setup."""
    print("Running download_file")
    r = requests.get(url, stream=True)
    with open(save_file, "wb") as fd:
        i = 0
        for chunk in r.iter_content(chunk_size=512):
            if chunk:
                i += 1
                fd.write(chunk)


async def makedir(dir_name: str) -> str:
    """Creates directory if needed, returns directory path."""
    print("Running makedir")
    if await dircheck(dir_name) is False:
        os.makedirs(dir_name)
        print("Made directory '{}'".format(dir_name))
    else:
        print("Directory '{}' already exists".format(dir_name))
    return dir_name


async def asyncio_subprocess(*args):
    """Runs a async compatible subprocess, returning the created process."""
    process = await asyncio.create_subprocess_shell(*args,
                                                    stdout=asyncio.subprocess.PIPE,
                                                    stdin=asyncio.subprocess.PIPE,
                                                    stderr=asyncio.subprocess.PIPE)
    return process


class Servers(commands.Cog):
    """Cog focused for controlling 3rd-Party Servers through JSON data."""
    def __init__(self, bot):
        self.bot = bot
        self.server_data = None
        self.current_console = None
        self.current_process = None
        self.current_server = None  # TODO: Change JSON format, remove the server identifier key, use filenames instead.
        self.current_dir = None
        self.main_dir = os.getcwd()
        self.server_cleanup.start()

    async def download(self, server_data: dict):
        """Initiates download functions for the given server."""
        print("Running download")
        if 'args' in server_data['download'].keys():
            server_data['download'] = await load_args(server_data['download'])
        main_dir = os.getcwd()
        server_dir = await makedir(server_data['directories']['main'])
        os.chdir(server_dir)
        file_dir = server_data['download']['file']
        link = server_data['download']['link']
        await download_file(link, file_dir)
        await self.run_command(server_data, "setup")
        os.chdir(main_dir)

    @tasks.loop(seconds=1)
    async def server_cleanup(self):
        if self.current_process is not None:
            if self.current_process.returncode is not None and hasattr(self.console_read, "finished"):
                self.current_process = None
                self.current_server = None
                self.current_console = None
                await self.bot.change_presence(activity=None)
                print("The running server has been terminated, resetting values.")

    @tasks.loop(seconds=1)
    async def console_read(self, channel_id):
        print("Running console_read task")
        channel = discord.utils.get(self.bot.get_all_channels(), id=channel_id)
        if self.current_process is not None:
            print("Server process found.")
            if self.current_process.stdout.at_eof() is not True:
                data = await self.current_process.stdout.readline()
                reply = data.decode().strip()
                await channel.send(reply)
                print("Sent: {}".format(reply))
            else:
                print("Nothing to read.")
                self.console_read.finished = True  # keeps the server_cleanup from running until all messages are sent.
        else:
            print("Stopping console_read task, no server running.")
            self.console_read.stop()

    async def console_write(self, data):
        print("cw: {}".format(self.current_process.stdin.is_closing()))
        if self.current_process is not None:
            data += "\n"
            print("Running console_write")
            data = data.encode()
            print("Writing '{}' to console".format(data.decode()))
            self.current_process.stdin.write(data)
            await self.current_process.stdin.drain()
            print("Finished console_write")

    async def run_command(self, server_data: dict, command: str):
        """Process the given command found in serverdata."""
        statustypes = {"playing": discord.ActivityType.playing,
                       "watching": discord.ActivityType.watching,
                       "streaming": discord.ActivityType.streaming,
                       "listening": discord.ActivityType.listening}
        cmd = server_data["commands"][command]
        i = 0
        m = len(cmd)
        print("Running command: {}".format(command))
        for step in cmd:
            i += 1
            print("Running step {} of {}".format(i, m))
            if 'file' in step.keys():
                print("Running file creation for setup step: {}".format(step))
                await common.makefile(step['file']['name'], step['file']['data'])
            elif 'presence' in step.keys():
                if step['presence']['type'] is not None:
                    activity = discord.Activity(name=step['presence']['status'],
                                                type=statustypes[step['presence']['type']])
                else:
                    activity = None
                await self.bot.change_presence(activity=activity)
            elif 'shell' in step.keys():
                if 'args' in step.keys():
                    step = await load_args(step)
                self.current_process = await asyncio_subprocess(step['shell'])
            elif 'channel' in step.keys():
                print("Found 'channel' key")
                if step['channel']['type'] == 'console':
                    print("Found 'console' key")
                    self.current_console = step['channel']['id']
                    self.console_read.start(step['channel']['id'])
            elif 'console' in step.keys():
                print("Sending command '{}' to server console.".format(step['console']))
                await self.console_write(step['console'])

    @commands.group(aliases=["servers"])
    async def server(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send("Invalid command.")

    @server.command(pass_context=True)
    @commands.check(is_admin)
    async def start(self, ctx, server_name: str):
        """Start a server"""
        if os.path.exists(os.path.join(common.getbotdir(), "data", "servers", "{}.json".format(server_name))):
            self.server_data = await common.loadjson("data/servers/{}.json".format(server_name))
            print("Loaded '{}' server data.".format(server_name))
            if await dircheck(self.server_data[server_name]['directories']['main']):
                os.chdir(self.server_data[server_name]['directories']['main'])
                await self.run_command(self.server_data[server_name], "start")
                self.current_server = server_name
                await ctx.send("Starting server '{}'".format(server_name))
            else:  # not downloaded yet
                await ctx.send("Directory for '{}' currently does not exist. Starting download.".format(server_name))
                await self.download(self.server_data[server_name])
                await ctx.send("Download finished, run the command again to start the server.")
        else:
            await ctx.send("No server by '{}' found".format(server_name))

    @server.command(pass_context=True)
    @commands.check(is_admin)
    async def stop(self, ctx):
        await self.run_command(self.server_data[self.current_server], "stop")
        await ctx.send("Stopping server '{}'".format(self.current_server))

    @server.group(pass_context=True)
    @commands.check(is_admin)
    async def data(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send("Invalid command.")

    @data.command(pass_context=True)
    @commands.check(is_admin)
    async def get(self, ctx, file):
        """Receive raw JSON serverdata from the loaded file."""
        await ctx.author.send(file=discord.File(os.path.join(common.getbotdir(),
                                                             "data",
                                                             "servers",
                                                             "{}.json".format(file))))

    @server.command(pass_context=True)
    @commands.check(is_admin)
    async def list(self, ctx):
        """List all servers available to launch."""
        color = ebed.randomrgb()
        embed = discord.Embed(title="Servers Listed",
                              color=color)
        count = 0
        msg = ""
        for file in os.listdir(os.path.join(common.getbotdir(), "data", "servers")):
            count += 1
            msg += "\n**-** {}".format(os.path.splitext(file)[0])
        embed.add_field(name="{} loaded".format(count), value=msg, inline=False)
        embed.set_footer(text="#{0:02x}{1:02x}{2:02x}".format(color.r, color.g, color.b))
        await ctx.send(embed=embed)

    @commands.Cog.listener()
    async def on_message(self, msg):
        if msg.content is None:
            print("NONE")
        if await is_admin(msg) and self.current_process is not None:
            if msg.channel.id == self.current_console:
                await self.console_write(msg.content)


def setup(bot):
    bot.add_cog(Servers(bot))
