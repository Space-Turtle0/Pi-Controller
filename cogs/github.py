from discord.ext import commands, tasks
import core.common as common
import core.embed as ebed
import github
import discord
import os


class Github(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.g = github.Github(os.environ['GAPI'])

    @commands.command()
    async def github(self, ctx):
        embed = discord.Embed(color=ebed.randomrgb())
        embed.description = "[Bot Github Link!](https://github.com/InValidFire/Pi-Controller)"
        await ctx.send(embed=embed)

    @commands.group(aliases=['contributor'])
    async def contributors(self, ctx):
        if ctx.invoked_subcommand is None:
            repo = self.g.get_repo("InValidFire/Pi-Controller")
            contributors = repo.get_contributors()
            embed = discord.Embed(color=ebed.randomrgb())
            for contributor in contributors:
                latest_commit = None
                for commit in repo.get_commits(author=contributor):
                    latest_commit = commit
                    break
                embed.add_field(name="{}'s latest contribution".format(contributor.login),
                                value="[{sha}]({url})".format(sha=latest_commit.sha, url=latest_commit.html_url))
            await ctx.send(embed=embed)

    @contributors.command(pass_context=True)
    @commands.is_owner()
    async def link(self, ctx, user: discord.User, github_profile):
        """Link a Discord user to a Github Profile for use with other commands."""
        data = await common.loadjson(os.path.join(common.getbotdir(), "data", "data.json"))
        data['contributors'][user.id] = {}
        data['contributors'][user.id]['github'] = github_profile
        await common.dumpjson(data, os.path.join(common.getbotdir(), "data", "data.json"))
        embed = discord.Embed(color=ebed.randomrgb())
        embed.description = "{} has been linked to the Github Profile '{}'".format(user.mention, github_profile)
        await ctx.send(embed=embed)

    @contributors.command()
    async def user(self, ctx, github_profile):
        """Look up bot contributions for the given Github User."""
        embed = discord.Embed(color=ebed.randomrgb())
        repo = self.g.get_repo("InValidFire/Pi-Controller")
        try:
            user = self.g.get_user(github_profile)
            commits = repo.get_commits(author=user)
            if commits.totalCount == 0:
                embed.description = "No contributions found for user '{}'".format(github_profile)
            else:
                for i, commit in enumerate(commits):
                    gc = repo.get_git_commit(commit.sha)
                    embed.add_field(name=gc.message.split("\n")[0],
                                    value="[{sha}]({url})".format(sha=gc.sha, url=gc.html_url),
                                    inline=False)
                    embed.title = "Last {} commits for user: {}".format(i + 1, github_profile)
                    if i == 9:
                        break
        except github.UnknownObjectException:
            embed.description = "The Github user '{}' could not be found.".format(github_profile)
        finally:
            await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Github(bot))
