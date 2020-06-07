from discord.ext import commands, tasks
import core.common as common
import core.embed as ebed
import datetime
import pytz
import discord
import requests
import psutil
import subprocess
import sys
import os


async def is_admin(ctx):
    program_dir = common.getbotdir()
    datafile = os.path.join(program_dir, "data/data.json")
    data = await common.loadjson(datafile)
    if ctx.author.id in data['admins']:
        return True


class Core(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.sys_status = {}
        self.sys_monitor.start()
        self.platform = sys.platform
        self.data_path = common.getbotdir()

    @commands.group()
    async def admins(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send("Invalid command.")

    @admins.command()
    async def list(self, ctx):
        data = await common.loadjson("data/data.json")
        count = 0
        msg = ""
        for admin in data['admins']:
            try:
                user = self.bot.get_user(admin)
                msg += "\n{}".format(user.mention)
                count += 1
            except commands.BadArgument:
                continue
        if count == 1:
            admin_count = "1 admin"
        else:
            admin_count = "{} admins".format(count)
        color = ebed.randomrgb()
        embed = discord.Embed(title="Bot Admins",
                              color=color)
        embed.add_field(name=admin_count, value=msg)
        embed.set_footer(text=ebed.rgb_to_hex(color.to_rgb()))
        await ctx.send(embed=embed)

    @admins.command(pass_context=True)
    @commands.check(is_admin)
    async def add(self, ctx, user: discord.User):
        data = await common.loadjson("data/data.json")
        if user.id not in data['admins']:
            data['admins'].append(user.id)
            await common.dumpjson(data, "data/data.json")
            await ctx.send("{} is now a bot admin.".format(user.mention))
        else:
            await ctx.send("{} is already a bot admin.".format(user.mention))

    @commands.command(pass_context=True)
    @commands.check(is_admin)
    async def restart(self, ctx):
        """Run the given command and close the python interpreter.
            If no command is given, it will just close."""
        print("Running restart")
        embed = discord.Embed(color=ebed.randomrgb())
        embed.description = "Be right back!"
        await ctx.send(embed=embed)
        os.execl(sys.executable, sys.executable, *sys.argv)

    @commands.command(pass_context=True)
    @commands.check(is_admin)
    async def shutdown(self, ctx):
        embed = discord.Embed(color=ebed.randomrgb())
        embed.description = "Goodbye!"
        await ctx.send(embed=embed)
        sys.exit()

    @commands.command(pass_context=True)
    async def getbotdir(self, ctx):
        embed = discord.Embed(color=ebed.randomrgb())
        embed.add_field(name="Bot Dir", value=common.getbotdir())
        embed.add_field(name="Arg 0", value="name: {}".format(str(sys.argv[0])))
        embed.add_field(name="Folder", value="name: {}".format(str(os.path.dirname(sys.argv[0]))))
        embed.add_field(name="Full Path", value=os.path.realpath(os.path.dirname(sys.argv[0])))
        await ctx.send(embed=embed)

    @commands.command()
    async def status(self, ctx):
        color = ebed.randomrgb()
        embed = discord.Embed(title="System Status",
                              timestamp=self.sys_status["UPDATE"],
                              color=color, description="Updated every minute.")
        embed.add_field(name="RAM", value="{}%".format(self.sys_status["RAM"]))
        embed.add_field(name="CPU", value="{}%".format(self.sys_status["CPU"]))
        embed.add_field(name="DISK", value="{}%".format(self.sys_status["DISK"]))
        if self.platform == 'linux':  # platform specific feature
            embed.add_field(name="Temperature",
                            value="{}°C/{}°F".format(self.sys_status["TEMPC"], self.sys_status["TEMPF"]))
        embed.add_field(name="Boot Time", value=self.sys_status["BOOT"], inline=False)
        embed.add_field(name="IP Address", value=self.sys_status["IP"], inline=False)
        embed.set_footer(text=ebed.rgb_to_hex(color.to_rgb()))
        await ctx.send(embed=embed)

    @add.error
    async def add_error(self, ctx, error):
        if isinstance(error, commands.BadArgument):
            await ctx.send(error.args[0])

    @commands.command()
    async def invite(self, ctx):
        await ctx.send("https://discord.com/api/oauth2/authorize?client_id=714607226756661258&permissions=116800&scope=bot")

    @tasks.loop(minutes=1)
    async def sys_monitor(self):
        tz = pytz.timezone("America/New_York")
        self.sys_status["UPDATE"] = pytz.utc.localize(datetime.datetime.utcnow())
        self.sys_status["CPU"] = round(psutil.cpu_percent())
        self.sys_status["RAM"] = round(psutil.virtual_memory().percent)
        self.sys_status["DISK"] = round(psutil.disk_usage("/").percent)
        if self.platform == 'linux':  # platform specific feature
            self.sys_status["TEMPF"] = psutil.sensors_temperatures()
            self.sys_status["TEMPC"] = psutil.sensors_temperatures()
        self.sys_status["BOOT"] = tz.localize(datetime.datetime.fromtimestamp(psutil.boot_time())).strftime("%Y-%m-%d%t%H:%M:%S %Z")
        self.sys_status["IP"] = requests.get("https://api.ipify.org?format=json").json()['ip']


def setup(bot):
    bot.add_cog(Core(bot))
