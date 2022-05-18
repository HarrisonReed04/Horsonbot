import discord
from discord.ext import commands
import random

from discord.ext.commands import context
from database import command_permission_set, db_select, determine_prefix, emojis, permissions, config, user_permission_set

class Perms_Cog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.group(invoke_without_command=True)
    async def perms(self, ctx, user:discord.Member=None):
        if ctx.invoked_subcommand == None:
            messages = ['You are almighty!', 'Wow, how cool!', 'Don\'t overrun the owner!', f'{emojis["warning"]} Woah, be careful with that much power!']
            permission_level = (await db_select(f"""SELECT `permission_level` from `users` where `user_snowflake_id` = "{ctx.author.id if user == None else user.id}";"""))[0][0]
            embed = discord.Embed(title=f"{ctx.author}, your permission level is {permission_level} - {permissions[f'{permission_level}']}", color=0x00ff00) if user == None else discord.Embed(title=f"{user}'s permission level is {permission_level} - {permissions[f'{permission_level}']}", color=0xff0000)
            embed.set_footer(text=f"{messages[random.randint(0,3)]}")
            embed.set_thumbnail(url=ctx.author.avatar_url if user == None else user.avatar_url)
            await ctx.reply(embed=embed)

    @perms.command()
    async def level(self, ctx, user:discord.Member):
        messages = ['You are almighty!', 'Wow, how cool!', 'Don\'t overrun the owner!', f'{emojis["warning"]} Woah, be careful with that much power!']
        permission_level = (await db_select(f"""SELECT `permission_level` from `users` where `user_snowflake_id` = "{ctx.author.id if user == None else user.id}";"""))[0][0]
        embed = discord.Embed(title=f"{ctx.author}, your permission level is {permission_level} - {permissions[f'{permission_level}']}", color=0x00ff00) if user == None else discord.Embed(title=f"{user}'s permission level is {permission_level} - {permissions[f'{permission_level}']}", color=0xff0000)
        embed.set_footer(text=f"{messages[random.randint(0,3)]}")
        embed.set_thumbnail(url=ctx.author.avatar_url if user == None else user.avatar_url)
        await ctx.reply(embed=embed)

    @perms.command()
    async def cmd(self, ctx, command_name:str, permission_level:int):
        owner = self.bot.get_user(538838470727172117)
        await command_permission_set(command_name,owner,self.bot,ctx,permission_level)
        await ctx.send(embed=discord.Embed(description=f"Command `{command_name}` permission level changed to `{permission_level}`", color=0xff0000))
        
    @perms.command()
    async def user(self, ctx, user:discord.Member, permission_level:int):
        await user_permission_set(user,self.bot,ctx,permission_level)

def setup(bot):
    bot.add_cog(Perms_Cog(bot))