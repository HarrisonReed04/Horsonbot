import discord
from discord.ext import commands
from database import db_commit, db_select
from datetime import datetime
import random
class horsonbotcasino(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def claim(self, ctx):
        amount = random.randint(100,1000)
        last_claim = (await db_select(f"""SELECT `last_claim` FROM `users` WHERE `user_snowflake_id` = "{ctx.author.id}";"""))[0][0]
        print(last_claim)
        if last_claim != None:
            if last_claim != "Null":
                last_claim = datetime.strptime(last_claim, '%d-%m-%Y') if last_claim != "Null" else "Null"
            if datetime.now().strftime('%d-%m-%Y') == last_claim or last_claim != None:
                await ctx.send(embed=discord.Embed(title=f"Sorry, {ctx.author.name}, you have already claimed today...",description="Wait until tomorrow to claim again."))
        else:
            balance = (await db_select(f"""SELECT `balance` FROM `users` WHERE `user_snowflake_id` = "{ctx.author.id}";"""))[0][0]
            await ctx.send(embed=discord.Embed(title=f"Claimed £{amount}!", description=f"Your balance is now `£{balance+amount}`"))
            await db_commit(f"""UPDATE `users` SET `last_claim` = "{datetime.now().strftime('%d-%m-%Y')}" WHERE `user_snowflake_id` = "{ctx.author.id}";""")
            await db_commit(f"""UPDATE `users` SET `balance` = "{balance+amount}" WHERE `user_snowflake_id` = "{ctx.author.id}";""")



def setup(bot):
    bot.add_cog(horsonbotcasino(bot))