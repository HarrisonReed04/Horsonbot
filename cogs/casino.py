import discord
from discord.ext import commands
from database import db_commit, db_select
from datetime import datetime
class horsonbotcasino(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        print("Hello")

    @commands.command()
    async def claim(self, ctx):
        last_claim = (await db_select(f"""SELECT `last_claim` FROM `users` WHERE `user_snowflake_id` = "{ctx.author.id}";"""))[0][0]
        last_claim = datetime.strptime(last_claim, '%d-%m-%Y') if last_claim != "Null" else "Null"
        if datetime.now().strftime('%d-%m-%Y') == last_claim:
            await ctx.send(embed=discord.Embed(title=f"Sorry, {ctx.author.name}, you have already claimed today...",description="Wait until tomorrow to claim again."))
        else:
            await db_commit(f"""UPDATE `users` SET `last_claim` = "{datetime.now().strftime('%d-%m-%Y')}" WHERE `user_snowflake_id` = "{ctx.author.id}";""")
            


def teardown(bot):
    print("Ending")




def setup(bot):
    bot.add_cog(horsonbotcasino(bot))