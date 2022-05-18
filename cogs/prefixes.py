import discord
from discord.ext import commands
from database import emojis, config, db_commit, db_select, determine_prefix


class prefixes(commands.Cog):
    def __init__(self,bot):
        self.bot = bot

    @commands.group()
    async def prefix(self, ctx):
        if ctx.invoked_subcommand == None:
            #await ctx.send(str((await db_select(f"""SELECT `guild_prefix` FROM `guilds` WHERE `guild_snowflake_id` = "{ctx.guild.id}";"""))[0][0]).split("-"))
            prefixes = (await db_select(f"""SELECT `guild_prefix` FROM `guilds` WHERE `guild_snowflake_id` = "{ctx.guild.id}";"""))[0][0].split("-")
            embed=discord.Embed(title="My current prefixes here:", description=f'\n'.join(prefixes), color=0x0f0f0f)
            await ctx.send(embed=embed)

    @prefix.command()
    async def add(self, ctx, prefix:str="!"):
        if len(prefix) > 1:
            embed=discord.Embed(title=f"Sorry, Prefixes can only currently be 1 character. For example, `£` is the default prefix.", color=0xff0000)
        if prefix.isspace() == True:
            embed=discord.Embed(title=f"Nice try, {ctx.author.name}, you can't break me like that!", color=0xff0000)
            await ctx.reply(embed=embed)
            return
        if ctx.guild:
            newprefixes = ""
            """`Add a new prefix.`"""
            prefixes = (await db_select(f"""SELECT `guild_prefix` FROM `guilds` WHERE `guild_snowflake_id` = "{ctx.guild.id}";"""))[0][0].split("-")
            if prefix in prefixes:
                await ctx.send(embed=discord.Embed(title = f"`{prefix}` is already a prefix here!", color=0xff0000))
                return  
            prefixes.append(prefix)
            for np in prefixes:
                if np != prefixes[-1]:
                    newprefixes += f"{np}-"
                else:
                    newprefixes += f"{np}"
            if ctx.author == ctx.guild.owner or ctx.author.id == 538838470727172117:
                await self.set_prefix(ctx, newprefixes)
                embed=discord.Embed(title=f"Okay, {ctx.author.name}, I've added `{prefix}` to this servers prefixes. New prefixes are: `{newprefixes.replace('-', ' / ')}`.", color=0xff0000)
                await ctx.reply(embed=embed)
        else:
            await ctx.reply(embed=discord.Embed(title=f"Sorry, {ctx.author.name}, I currently do not support custom prefixes in DMs. The prefix in DMs is still `£`", color=0xff00))

    @prefix.command(aliases=['set'])
    async def reset(self, ctx, new_prefix:str="£"):
        """`This allows the bot owner or guild owner to change the bot's prefix. Permission Level is: 1, Although only the guild owner can run the command.`"""
        infochannel = self.bot.get_channel((int(config['info_channel'])))
        if ctx.author == ctx.guild.owner or ctx.author.id == 538838470727172117:
            if not new_prefix == '"':
                await db_commit(f"""UPDATE `guilds` SET `guild_prefix` = "{new_prefix}" WHERE `guild_snowflake_id` = "{ctx.guild.id}";""")
                embed=discord.Embed(title=f"Okay, {ctx.author.name}, I've changed this servers prefix to {new_prefix}.", color=0xff0000)
                await ctx.reply(embed=embed)
        else:
            embed = discord.Embed(title=f"{emojis['barrier']}Sorry, You can't do that!{emojis['barrier']}", description=f"You'll have to get the server owner or bot owner to change that!\nMy prefix here is `{await determine_prefix(self.bot,ctx.message)}`")
            await ctx.reply(embed=embed)


    async def set_prefix(self, ctx, prefix):
        await db_commit(f"""UPDATE `guilds` SET `guild_prefix` = "{prefix}" WHERE `guild_snowflake_id` = "{ctx.guild.id}";""")


def setup(bot):
    bot.add_cog(prefixes(bot))