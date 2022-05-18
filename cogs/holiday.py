import discord
from discord.ext import commands, tasks
from database import emojis, db_select, utc_to_locat
from datetime import datetime, timedelta, date
from requests import get
from colorama import Fore, init
import asyncio
init()
import asyncio


class holiday(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @tasks.loop(seconds=60)
    async def checker(self):
        print(Fore.WHITE + "| EVENT LOOP INFO | HOLIDAY CHECKER | NEXT ITERATION")
        injoy = self.bot.get_channel(674024871579353112)
        if datetime.now().strftime("%H:%M") == "00:00":
            d0 = date(datetime.now().year, datetime.now().month, datetime.now().day)
            d1 = date(2022, 7, 8)
            delta1 = d1-d0
            d2 = date(2022, 5, 7)
            delta2 = d2-d0
            if not delta1.days == 0:
                embed=discord.Embed(title="Holiday Countdown!", description=f"Upcoming Holidays", color=0xf0f4a3)
                embed.add_field(name="France:", value=f"Only {delta2.days} days to go!", inline=False)
                embed.add_field(name="Tenerife:", value=f"Only {delta1.days} days to go!", inline=False)
                print(Fore.GREEN + f"| HOLIDAY INFO | {delta1.days} LEFT UNTIL HOLIDAY")
            else:
                embed=discord.Embed(title=f"{emojis['celebrate']}ITS HOLIDAY TIME!!!{emojis['celebrate']}")
            await injoy.send(embed=embed)

    @commands.command()
    async def holiday(self, ctx):
        d0 = date(datetime.now().year, datetime.now().month, datetime.now().day)
        d1 = date(2022, 7, 8)
        delta1 = d1-d0
        d2 = date(2022, 5, 7)
        delta2 = d2-d0
        if not delta1.days == 0:
            embed=discord.Embed(title="Holiday Countdown!", description=f"Upcoming Holidays", color=0xf0f4a3)
            embed.add_field(name="France:", value=f"Only {delta2.days} days to go!", inline=False)
            embed.add_field(name="Tenerife:", value=f"Only {delta1.days} days to go!", inline=False)
            print(Fore.GREEN + f"| HOLIDAY INFO | {delta1.days} LEFT UNTIL TENERIFE")
            print(Fore.GREEN + f"| HOLIDAY INFO | {delta2.days} LEFT UNTIL TENERIFE")
        else:
            embed=discord.Embed(title=f"{emojis['celebrate']}ITS HOLIDAY TIME!!!{emojis['celebrate']}")
        await ctx.send(embed=embed)

    @commands.Cog.listener()
    async def on_ready(self):
        if datetime.now().second > 0:
            print(Fore.YELLOW + f"| EVENT LOOP INFO | HOLIDAY CHECKER | WAITING {60-datetime.now().second} TO START")
            await asyncio.sleep(60-datetime.now().second)
        try:
            await self.checker.start()
        except Exception as e:
            print(Fore.RED + f"| EVENT LOOP INFO | HOLIDAY CHECKER | EXCEPTION OCCURED : {e}")

def setup(bot):
    bot.add_cog(holiday(bot))