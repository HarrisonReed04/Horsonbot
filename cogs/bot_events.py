import aiomysql
import discord
from discord.ext import tasks, commands
from colorama import Fore, init
init()
from database import command_permission_set, add_guild, databases, db_commit, db_select, emojis, add_user, reset_user, initiate_config, permissions, config
from datetime import datetime
from requests import get
import asyncio

class events(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def get_data(self, url):
        response = get(url, 10)
        if response.status_code not in [200, 204]:
            print(Fore.RED + f"CRITICAL : COULD NOT CONNECT TO " + Fore.CYAN + f"{url}" + Fore.RED + f", ERROR STATUS CODE: " + Fore.CYAN + f"{response.status_code} " + Fore.RED + "WITH TEXT: " + Fore.CYAN + f"{response.text}", Fore.YELLOW + "\nWaiting 1 Second before attempting again")
            await asyncio.sleep(1)
            await self.get_data(url)
        else:
            return (response.json())

    @commands.Cog.listener()
    async def on_ready(self):
        infochannelid = int(config['info_channel'])
        infochannel = self.bot.get_channel(infochannelid)
        owner = self.bot.get_user(538838470727172117)
        await infochannel.purge(limit=500)
        embed=discord.Embed(title="The bot has loaded and is ready to get going!", description=f"Logged in with ID: {self.bot.user} [{self.bot.user.id}]", color=0x00FF00)
        embed.set_footer(text=f"Loaded at {datetime.now().strftime('%d-%m-%Y @ %H:%M.%S')}")
        try:
            await infochannel.send(embed=embed)
        except:
            await owner.send(embed=embed)
        print("USERS")
        await self.check_all_users()
        print("USERS DONE")
        print("GUILDS")
        await self.check_all_guilds()
        print("GUILDS DONE")
    
    @commands.Cog.listener()
    async def on_message(self, message):
        x = message
        try:
            await db_commit(f"""UPDATE `users` SET `last_message_time` = "{datetime.now()}" WHERE `user_snowflake_id` = "{message.author.id}";""")
        except:
            pass
        if message.author.id == self.bot.user.id:
            return
        if message.embeds and not message.guild:
            ctx = await self.bot.get_context(message)
            message = ctx.message.content.replace('"', "'")
            message = message.replace('`', "'")
            await (self.bot.get_channel(config['private_message_channel'])).send(embed=discord.Embed(title=f"Embed Receieved in private messages, from `{message.author.name}`"))
            await (self.bot.get_channel(config['private_message_channel'])).send(embed=message.embeds[0])
            await db_commit(f"""INSERT INTO `messages`(`message_snowflake_id`,`message_time_sent`,`message_guild_name`,`message_channel_snowflake_id`,`message_guild_snowflake_id`,`message_channel_name`,`message_author_name`,`message_author_snowflake_id`,`message_content`) VALUES("{ctx.message.id}","{datetime.now()}","DM","DM","DM","DM","{ctx.author}","{ctx.author.id}","{message}")""")
        if message.content == "":
            return
        private_message_channel = self.bot.get_channel(config['private_message_channel'])
        ctx = await self.bot.get_context(message)
        message = ctx.message.content.replace('"', "'")
        message = message.replace('`', "'")
        if str(ctx.channel.id) in [f"{config['private_message_channel']}",f"{config['edited_message_channel']}",f"{config['deleted_message_channel']}",f"{config['errors_channel']}",f"{config['info_channel']}",f"{config['permissions_channel']}"]:
            return 
        if ctx.guild:
            await db_commit(f"""INSERT INTO `messages`(`message_snowflake_id`,`message_time_sent`,`message_guild_name`,`message_channel_snowflake_id`,`message_guild_snowflake_id`,`message_channel_name`,`message_author_name`,`message_author_snowflake_id`,`message_content`) VALUES("{ctx.message.id}","{datetime.now()}","{ctx.guild.name}","{ctx.guild.id}","{ctx.channel.id}","{ctx.channel.name}","{ctx.author}","{ctx.author.id}","{message}")""")
        else:
            await db_commit(f"""INSERT INTO `messages`(`message_snowflake_id`,`message_time_sent`,`message_guild_name`,`message_channel_snowflake_id`,`message_guild_snowflake_id`,`message_channel_name`,`message_author_name`,`message_author_snowflake_id`,`message_content`) VALUES("{ctx.message.id}","{datetime.now()}","DM","DM","DM","DM","{ctx.author}","{ctx.author.id}","{message}")""")
            embed = discord.Embed(
                title = f"Private message received from {ctx.author}",
                description = f"""\n```{message}```""",
                color = 0x7289DA
            )
            embed.set_thumbnail(url=ctx.author.avatar_url)
            await private_message_channel.send(embed=embed)
        if "goodnight" in message:
            await x.add_reaction(f"{emojis['G']}")
            await x.add_reaction(f"{emojis['N']}")

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        #for embed in after.embeds:
        #    await after.channel.send(embed.to_dict())
        if before.content == after.content:
            return
            
    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        join_time = datetime.now()
        try:
            await db_commit(f"""INSERT INTO `guilds`(`guild_name`,`guild_snowflake_id`,`guild_prefix`,`guild_join_time`) VALUES ("{guild.name}", "{guild.id}", "{config['default_prefix']}", "{join_time}")""")
        except aiomysql.IntegrityError:
            await db_commit(f"""UPDATE `guilds` SET `guild_join_time` = "{join_time}" WHERE `guild_snowflake_id` = "{guild.id}";""")
        await self.check_all_users()
    #If the bot rejoins the server then the join time is just overwritten

    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        leave_time = datetime.now()
        await db_commit(f"""UPDATE `guilds` SET `guild_leave_time` = "{leave_time}" WHERE `guild_snowflake_id` = "{guild.id}";""")

    @commands.command(alias=["command_perms"])
    async def commands(self, ctx):
        await self.check_all_commands(ctx)

    async def check_all_users(self):
        for guild in self.bot.guilds:
            for member in guild.members:
                try:
                    members_list = (await db_select(f"""SELECT `user_snowflake_id` FROM `users`"""))
                    if not (any(str(member.id) in i for i in members_list)):
                        await add_user(member)
                except Exception as e:
                    print(e)
                if member.id == 538838470727172117:
                    try:
                        await db_commit(f"""UPDATE `users` SET `permission_level` = "5" WHERE `user_snowflake_id` = "{member.id}";""")
                    except Exception as e:
                        print(Fore.RED + f"{member} could not be given permission level 5! Here is the error: {e}")

    @tasks.loop(seconds=15)
    async def status_loop(self):
        data = await self.get_data("https://api.coronavirus.data.gov.uk/v1/data")
        cases, cumcases, deaths, cumdeaths = data['data'][0]['dailyCases'], data['data'][0]['cumulativeCases'], data['data'][0]['dailyDeaths'], data['data'][0]['cumulativeDeaths']

    async def check_all_commands(self, ctx):
        owner = self.bot.get_user(538838470727172117)
        for command in self.bot.walk_commands():
            #Iterates through every command the bot has
            try:
                command_permission_level = (await db_select(f"""SELECT `command_permission_level` FROM `commands` WHERE `command_name` = "{command.name}";"""))[0]
            except IndexError:
                await command_permission_set(command.name, owner, self.bot, ctx)
            #Checks for a permission level and if there isn't one then the owner sets one 

    async def check_all_guilds(self):
        owner = self.bot.walk_commands()
        for guild in self.bot.guilds:
            #Iterates through every guild
            try:
                guild_name = (await db_select(f"""SELECT `guild_name` FROM `guilds` WHERE `guild_snowflake_id` = "{guild.id}";"""))[0]
            except IndexError:
                await add_guild(guild, "normal")
            #Checks for a database entry for every server the bot is in, if not found then the guild is added

def setup(bot):
    bot.add_cog(events(bot))