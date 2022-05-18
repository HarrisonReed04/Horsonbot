import asyncio
import os 
import discord
from discord.ext import commands
from database import emojis, config, db_commit, db_select, determine_prefix
from datetime import datetime, timedelta
from colorama import Fore, init
from requests import get
import random
init()

class misc_commands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def get_data(self, url):
        response = get(url=url)
        if response.status_code not in [200, 204]:
            print(Fore.RED + f"CRITICAL : COULD NOT CONNECT TO " + Fore.CYAN + f"{url}" + Fore.RED + f", ERROR STATUS CODE: " + Fore.CYAN + f"{response.status_code} " + Fore.RED + "WITH TEXT: " + Fore.CYAN + f"{response.text}", Fore.YELLOW + "\nWaiting 1 Second before attempting again")
            await asyncio.sleep(1)
            await self.get_data(url)
        else:
            return (response.json())

    async def remove_microseconds(self, ms):
        return ms - timedelta(microseconds=ms.microseconds)

    @commands.command()
    async def lines(self, ctx):
        count = 0
        files = {}
        value = ""
        base_path = os.getcwd()
        base_path = base_path.replace("/cogs", "")
        for file in os.listdir(base_path):
            if file.endswith(".py"):
                if file != "wordlist.py":
                    with open(file, 'r') as f:
                        lines = len(f.readlines())
                    count += lines
                    x = {file[:-3]:lines}
                    files.update(x)
        
        for file in os.listdir(f"{base_path}/cogs"):
            if file.endswith(".py"):
                with open(base_path+"/cogs/"+file, 'r') as f:
                    lines = len(f.readlines())
                count += lines
                x = {file[:-3]:lines}
                files.update(x)

        pairs = files
        pre = f"`Filename" + ((40-len("`Filename")) * " ") + f" : Lines`"
        for pair in pairs:
            value += f"`{pair}" + ((40-len(pair)) * " ") + f": {str(pairs[pair]).zfill(3)}`\n"

        embed = discord.Embed(
            title = f"Total lines: `{count}`\nHere is a breakdown:",
            color = 0x7289DA,
            description = f"{pre}\n{value}"
            )
            

        await ctx.send(embed=embed)

    @commands.command()
    async def react(self, ctx, msg_id : int, *, reactions):
        msg = await ctx.fetch_message(msg_id)
        await ctx.message.delete()
        for letter in list(reactions):
            try:
                await msg.add_reaction(emojis[letter.upper()])
            except:
                pass

    @commands.command(aliases=['profile_picture'])
    async def pfp(self, ctx, member:discord.Member=None):
        embed = discord.Embed(
            title = f"Profile picture of {ctx.author if member == None else member}",
            color = 0x00f000
        )
        embed.set_image(url=ctx.author.avatar_url if member == None else member.avatar_url)
        embed.set_footer(text=f"Requested by: {ctx.author}")
        await ctx.send(embed=embed)

    @commands.command()
    async def ping(self, ctx):
        """`This command is used to see if the bot is online and working. Permission level is: 1`"""
        embed = discord.Embed()
        embed.title="Calculating the ping"
        embed.color = 0xff0000
        s = datetime.now()
        msg = await ctx.send(embed=embed)
        ping = f"{int((datetime.now()-s).microseconds / 1000)}ms"
        embed.color = 0x00ff00
        await asyncio.sleep(1)
        embed.title = f"Current ping: {ping}"
        embed.description = f"Bot Latency: {self.bot.latency}"
        await msg.edit(embed=embed)

    @commands.command()
    async def say(self, ctx, *, arg):
        await ctx.message.delete()
        await ctx.send(arg)

    @commands.command(aliases=['id'])
    async def user_id(self, ctx, user:discord.Member=None):
        if user == None:
            user = ctx.author.mention
        await ctx.send(embed=discord.Embed(title=f"Here is {user.name}'s Snowflake ID.", description=f"{user.id}", color=0x00ff00))

    @commands.command(aliases=['msg_all', 'msg'])
    async def message_all(self, ctx, users:commands.Greedy[discord.Member], *,arg1):
        temp = arg1.split("/")
        title = temp[0]
        description = temp[1]
        embed = discord.Embed(color=0x7289DA, title=title, description=description)
        print(Fore.MAGENTA + f"INFO : Message to be sent to users " + Fore.RED + f"{[user.name for user in users]}" + Fore.MAGENTA+ f" \nMessage Content:\n     {title} \n      {description}")
        for user in users:
            try:
                await user.send(embed=embed)
                print(Fore.MAGENTA + f"Sent to " + Fore.YELLOW + f"{user}" + Fore.MAGENTA + " successfully.")
            except Exception as e:
                print(Fore.RED + f"ERROR : MESSAGE" + Fore.YELLOW + f"\n{title}\n{description}\n " + Fore.RED + "COULD NOT BE SENT TO " + Fore.BLUE + f"{user}" + Fore.RED + f"\nError: {e}")

    @commands.command()
    async def girlfriend(self, ctx):
        days = (datetime.now()-datetime.strptime('15-04-2022', '%d-%m-%Y')).days
        await ctx.send(embed=discord.Embed(title="Girlfriend check", description=f"{days} days with a girlfriend :smile:{emojis['greentick']} (Round 2!)\nCombined total of {days+720} days :grimacing:", color=0x00ff00))

    @commands.command()
    async def fact(self, ctx):
        fact = get("https://uselessfacts.jsph.pl/random.json?language=en")
        await ctx.send(embed=discord.Embed(title="Your random fact is:", description=f"`{fact.json()['text']}`", color=0xff00ff))

    @commands.command()
    async def activities(self, ctx, member:discord.Member):
        await ctx.send(f"{','.join(str(activity) for activity in member.activities)}")

def setup(bot):
    bot.add_cog(misc_commands(bot))
