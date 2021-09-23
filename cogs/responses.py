import asyncio
import discord
from discord.ext import commands
from database import emojis

class responses(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def clown(self, ctx, user:discord.Member=None):
        await ctx.message.delete()
        if ctx.author.id == 546780798661951512:
            await ctx.send(f"{ctx.author.display_name} is a {emojis['clown']}!")
        elif user.id == 538838470727172117:
            await ctx.send(f"{user.display_name} is a very cool guy, lots of love from {ctx.author.display_name}")
        else:
            await ctx.send(f"{user.display_name} is a {emojis['clown']}")

def setup(bot):
    bot.add_cog(responses(bot))