from discord.ext import commands
from cogs.core import is_admin
import aiofiles
import json
import discord
import requests
import asyncio
import os


async def dircheck(directory) -> bool:
    print("Running dircheck")
    return os.path.exists(directory)


async def load_args(data: dict) -> dict:  # make recursive
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


async def makefile(filename, data):
    async with aiofiles.open(filename, mode="w+") as file:
        await file.write(data)


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
    process = await asyncio.create_subprocess_shell(*args, stdout=asyncio.subprocess.PIPE)
    return process


def load_servers(serverfile) -> dict:
    with open(serverfile) as file:
        data = json.load(file)
    print("Loaded server data file.")
    return data


class Servers(commands.Cog):
    """Cog focused for controlling 3rd-Party Servers through JSON data."""
    def __init__(self, bot):
        self.bot = bot
        self.server_data = load_servers("servers.json")
        self.current_server = None
        self.current_dir = None
        self.main_dir = os.getcwd()

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

    async def run_command(self, server_data: dict, command: str):
        """Process the given command found in serverdata."""
        statustypes = {"playing": discord.ActivityType.playing,
                       "watching": discord.ActivityType.watching,
                       "streaming": discord.ActivityType.streaming,
                       "listening": discord.ActivityType.listening}
        cmd = server_data["commands"][command]
        i = 0
        m = len(cmd)
        for step in cmd:
            i += 1
            print("Running step {} of {}".format(i, m))
            if 'file' in step.keys():
                print("Running file creation for setup step: {}".format(step))
                await makefile(step['file']['name'], step['file']['data'])
            elif 'presence' in step.keys():
                activity = discord.Activity(name=step['presence']['status'],
                                            type=statustypes[step['presence']['type']])
                await self.bot.change_presence(activity=activity)
            elif 'shell' in step.keys():
                if 'args' in step.keys():
                    step = await load_args(step)
                self.current_server = await asyncio_subprocess(step['shell'])

    @commands.group()
    async def server(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send("Invalid command.")

    @server.command(pass_context=True)
    @commands.check(is_admin)
    async def start(self, ctx, server_name: str):
        """Start a server"""
        if server_name in self.server_data.keys():
            if await dircheck(self.server_data[server_name]['directories']['main']):
                os.chdir(server_name)
                await self.run_command(self.server_data[server_name], "start")
                await ctx.send("Starting server {}".format(server_name))
            else:  # not downloaded yet
                await ctx.send("Directory for '{}' currently does not exist. Starting download.".format(server_name))
                await self.download(self.server_data[server_name])
                await ctx.send("Download finished, run the command again to start the server.")
        else:
            await ctx.send("No server by '{}' found".format(server_name))

    @server.command(pass_context=True)
    @commands.check(is_admin)
    async def data(self, ctx):
        """Receive raw JSON serverdata from the loaded file."""
        await ctx.author.send(file=discord.File("servers.json"))

    @server.command(pass_context=True)
    @commands.check(is_admin)
    async def list(self, ctx):
        """List all servers available to launch."""
        msg = "Servers Loaded: "
        for key in self.server_data:
            msg += "\n{}".format(key)
        await ctx.send(msg)


def setup(bot):
    bot.add_cog(Servers(bot))
