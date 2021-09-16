import asyncio
import os 
import discord
from discord.ext import commands
from database import emojis, config, db_commit, db_select, determine_prefix, utc_to_locat
from datetime import datetime
from colorama import Fore, init
from pprint import pprint
init()

class misc_commands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def tyty(self, ctx):
        pprint(vars(commands))

    @commands.command()
    async def lines(self, ctx):
        count = 0
        files = {}
        value = ""
        base_path = os.getcwd()
        base_path = base_path.replace("/cogs", "")
        for file in os.listdir(base_path):
            if file.endswith(".py"):
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
    async def nick(self, ctx, user:discord.Member ,* ,nickname:str=""):
        if nickname == "":
            await user.edit(nick=None)
        else:
            await user.edit(nick=nickname)



    @commands.command()
    async def embedtest(self, ctx):
        embed = discord.Embed(title="F", description="`aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa`")
        await ctx.send(embed=embed)


    @commands.command(aliases=['bot'])
    async def _bot_info(self, ctx):
        embed = discord.Embed(
            title = "Here's some information about me!",
            description = f"**Join the support server: [Click]{emojis['curved_down_arrow']}\n**https://discord.gg/XVFGVjqmAT",
            color=0x00ff00)
        embed.add_field(
            name = "Total servers I'm in:",
            value = f"**`{len(self.bot.guilds)}`**",
            inline=False
        )
        embed.add_field(
            name = "Total Users:",
            value = f"**`{len(self.bot.users)}`**",
            inline=False
        )
        embed.add_field(
            name = "Online Users",
            value = f"**`{str(len({member.id for member in self.bot.get_all_members() if member.status is not discord.Status.offline and member.id != 842940605126279169}))}`**",
            inline=False
        )
        embed.add_field(
            name = "Total Channels",
            value = f"**`{sum(1 for guild in self.bot.guilds for channel in guild.channels)}`**",
            inline=False
        )
        embed.add_field(
            name = "Latency:",
            value = f"**`{round(self.bot.latency, 4) * 1000}ms / {round(self.bot.latency, 4)}s`**",
            inline=False
        )
        embed.add_field(
            name = "bot Invite Link",
            value = f"**`[Click]`{emojis['curved_down_arrow']}**\nhttps://discord.com/api/oauth2/authorize?client_id=773859915806670869&permissions=8&scope=bot",
            inline=False
        )
        embed.add_field(
            name = "Github Code",
            value = f"**`[Click]`{emojis['curved_down_arrow']}**\nhttps://github.com/HarrisonReed04/Neabot",
            inline=False
        )
        embed.set_footer(
            text=f"Powered by discord.py. Info requested by {ctx.author}",
        )
        embed.set_author(icon_url=ctx.author.avatar_url, name=ctx.author)
        await ctx.send(embed=embed)

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
    async def nuke(self, ctx):
        await ctx.send("Ok, nuking")


    @commands.group()
    async def prefix(self, ctx):
        if ctx.invoked_subcommand == None:
            #await ctx.send(str((await db_select(f"""SELECT `guild_prefix` FROM `guilds` WHERE `guild_snowflake_id` = "{ctx.guild.id}";"""))[0][0]).split("-"))
            await ctx.send(" / ".join((await db_select(f"""SELECT `guild_prefix` FROM `guilds` WHERE `guild_snowflake_id` = "{ctx.guild.id}";"""))[0][0].split("-")))
            #embed = discord.Embed(
            #    title = {str(list((await db_select(f"""SELECT `guild_prefix` FROM `guilds` WHERE `guild_snowflake_id` = "{ctx.guild.id}";"""))[0][0]))}
            #)
            #await ctx.send(embed=embed)

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

    #This command will respond with the latency of the bot.

    @commands.command()
    async def say(self, ctx, *, arg):
        await ctx.send(arg)

    @commands.command()
    async def abc(self, ctx, user:str):
        print(user)
        await ctx.send(user)

    @commands.command()
    async def print(self, ctx):
        x = ", ".join(str(user) for user in ctx.guild.members)
        await ctx.send(x)

    @commands.command()
    async def eb(self, ctx, arg1):
        await ctx.send(embed=discord.Embed(title=f"{arg1}",description=f"{arg1}"))

    @commands.command()
    async def profile(self, ctx, profileid:str=None, mode:str="default"):
        try:
            if profileid[1] == "#":
                profileid = profileid[2:-1]
            elif profileid[1] == "@":
                profileid = profileid[3:-1]
            profileid = int(profileid)
        except TypeError:
            user = ctx.author
        try:
            user = self.bot.get_user(profileid)
        except:
            pass
        try:
            guild = self.bot.get_guild(profileid)
        except:
            pass
        try:
            channel = self.bot.get_channel(profileid)
        except:
            embed = discord.Embed(title="Couldn't locate that User, Channel or Guild, ensure the ID is correct and try again.", color=0xff0000)
            await ctx.reply(embed=embed)
            return        

        if user != None:
            embed=discord.Embed(
                title=f"User `{user.name}`'s Profile." if mode != "admin" else f"**!!ADMIN REQUESTED!!** User `{user.name}`'s Profile.",
                description=f"Requested by: {ctx.author.mention} ",
                color=0x7289DA
            )

            embed.add_field(
                name = "Account creation:",
                value = f"`{(user.created_at).strftime('%H:%M.%S %d-%m-%Y').lower()}`",
                inline=True
            )
            embed.add_field(
                name='\u200b',
                value='\u200b',
                inline=True
            )
            embed.add_field(
                name = "Days since creation:",
                value = f"`{(datetime.now()-user.created_at).days}`"
            )
            try:

                member = ctx.guild.get_member(user.id)
                embed.add_field(
                    name = "User has boosted this server?",
                    value = f"`{member.premium_since.strftime('%d-%M-%Y %H:%M.%S').lower() if member.premium_since != None else 'False, how sad...'}`",
                    inline = True
                )
                if user.bot == True:
                    embed.add_field(
                    name='\u200b',
                    value='\u200b',
                    inline=True
                    )
                    embed.add_field(
                        name='\u200b',
                        value='\u200b',
                        inline=True
                    )
            except AttributeError:
                pass

            embed.add_field(
                name = "User is a bot?",
                value= f"`{user.bot}`",
                inline=False if user.bot == False else True
            )

            if user.bot == True:
                embed.add_field(
                    name='\u200b',
                    value='\u200b',
                    inline=True
                )
                embed.add_field(
                    name = "Verified Bot?",
                    value = f"`{user.public_flags.verified_bot}`",
                    inline = True
                )

            embed.add_field(
                name = "Snowflake ID:",
                value = f"`{user.id}`",
                inline=True
            )

            embed.add_field(
                name='\u200b',
                value='\u200b',
                inline=True
            )

            embed.add_field(
                name='Discriminator:',
                value=f'`#{user.discriminator}`',
                inline=True
            )

            embed.add_field(
                name = "Display Name:",
                value = f"`{user.display_name}`",
                inline=True
            )

            embed.add_field(
                name='\u200b',
                value='\u200b',
                inline=True
            )
            embed.add_field(
                name = "Full username:",
                value = f"`{user}`",
                inline=True
            )

            try:
                if mode == "admin":
                    msg_info = (await db_select(f"""SELECT `message_guild_name`,`message_channel_name`,`message_content` FROM `messages` WHERE `message_author_snowflake_id` = "{user.id}" ORDER BY `message_time_sent` DESC LIMIT 1;"""))[0]

                    embed.add_field(
                        name = "Last message:",
                        value = f'`{((await db_select(f"""SELECT `message_time_sent` FROM `messages` WHERE `message_author_snowflake_id` = "{user.id}" ORDER BY `message_time_sent` DESC LIMIT 1;"""))[0][0]).strftime("%H:%M.%S%P").lower()} {((await db_select(f"""SELECT `message_time_sent` FROM `messages` WHERE `message_author_snowflake_id` = "{user.id}" ORDER BY `message_time_sent` DESC LIMIT 1;"""))[0][0]).strftime("%d-%m-%Y") if ((await db_select(f"""SELECT `message_time_sent` FROM `messages` WHERE `message_author_snowflake_id` = "{user.id}" ORDER BY `message_time_sent` DESC LIMIT 1;"""))[0][0]).strftime("%d-%m-%Y") != datetime.now().strftime("%d-%m-%Y") else "Today"}`\nGuild Name: `{msg_info[0]}`\nChannel Name: `{msg_info[1]}`'
                    )
                    if len(msg_info[2]) <= 1024:
                        embed.add_field(
                            name='\u200b',
                            value='\u200b',
                            inline=True
                        )
                        content = msg_info[2]
                        content = content.replace("`", "(bt)")
                        content = content.replace('"', "'")
                        embed.add_field(
                            name = "Message Content:",
                            value = f"```{msg_info[2]}```",
                            inline = False
                        )
                    else:
                        await ctx.send(embed=discord.Embed(title = f'Message length was too long, {user.name}\'s message from {((await db_select(f"""SELECT `message_time_sent` FROM `messages` WHERE `message_author_snowflake_id` = "{user.id}" ORDER BY `message_time_sent` DESC LIMIT 1;"""))[0][0]).strftime("%H:%M.%S%P").lower()} has been sent here instead.', value = f"{msg_info[2]}", color = 0x7289DA))
                    embed.set_footer(text=f"**REQUESTED BY ADMIN {ctx.author.name}**")
                else:
                    embed.add_field(
                        name = "Time of last message I saw:",
                        value = f'`{((await db_select(f"""SELECT `message_time_sent` FROM `messages` WHERE `message_author_snowflake_id` = "{user.id}" ORDER BY `message_time_sent` DESC LIMIT 1;"""))[0][0]).strftime("%H:%M.%S%P").lower()} {((await db_select(f"""SELECT `message_time_sent` FROM `messages` WHERE `message_author_snowflake_id` = "{user.id}" ORDER BY `message_time_sent` DESC LIMIT 1;"""))[0][0]).strftime("%d-%m-%Y") if ((await db_select(f"""SELECT `message_time_sent` FROM `messages` WHERE `message_author_snowflake_id` = "{user.id}" ORDER BY `message_time_sent` DESC LIMIT 1;"""))[0][0]).strftime("%d-%m-%Y") != datetime.now().strftime("%d-%m-%Y") else "Today"}`',
                        inline = False
                    )
            except:
                embed.add_field(
                    name = f"Time of last message I saw:",
                    value = f"`None... How sad, are you dead {user.display_name}?`",
                    inline = False
                )

            try:
                embed.add_field(
                    name = "Activity Status:",
                    value = f"`Desktop: " + f"{emojis['noentry'] if member.desktop_status == discord.Status.dnd else emojis['redtick'] if member.desktop_status == discord.Status.offline else emojis['idle'] if member.desktop_status == discord.Status.idle else emojis['greentick'] if member.desktop_status == discord.Status.online else emojis['?']}`" + f" `Web: " + f"{emojis['noentry'] if member.web_status == discord.Status.dnd else emojis['redtick'] if member.web_status == discord.Status.offline else emojis['idle'] if member.web_status == discord.Status.idle else emojis['greentick'] if member.web_status == discord.Status.online else emojis['?']}`" + f" `Mobile: " + f"{emojis['noentry'] if member.mobile_status == discord.Status.dnd else emojis['redtick'] if member.mobile_status == discord.Status.offline else emojis['idle'] if member.mobile_status == discord.Status.idle else emojis['greentick'] if member.mobile_status == discord.Status.online else emojis['?']}`",
                    inline = False
                )
            except AttributeError:
                pass


            embed.set_image(url=user.avatar_url)
            await ctx.send(embed=embed)

        elif guild != None:

            embed = discord.Embed(
                title = f"Guild `{guild.name}`'s profile.",
                description = f"Requested by {ctx.author.mention}.",
                color = 0x7289DA
            )

            embed.add_field(
                name = f"Guild Owner",
                value = f'`Name: {guild.owner}`\n`ID: {guild.owner.id}`\n`Activity Status: ` ' + f"\n`Desktop:" + f"{emojis['noentry'] if guild.owner.desktop_status == discord.Status.dnd else emojis['redtick'] if guild.owner.desktop_status == discord.Status.offline else emojis['idle'] if guild.owner.desktop_status == discord.Status.idle else emojis['greentick'] if guild.owner.desktop_status == discord.Status.online else emojis['?']}`" + f" `Web:" + f"{emojis['noentry'] if guild.owner.web_status == discord.Status.dnd else emojis['redtick'] if guild.owner.web_status == discord.Status.offline else emojis['idle'] if guild.owner.web_status == discord.Status.idle else emojis['greentick'] if guild.owner.web_status == discord.Status.online else emojis['?']}`" + f" `Mobile:" + f"{emojis['noentry'] if guild.owner.mobile_status == discord.Status.dnd else emojis['redtick'] if guild.owner.mobile_status == discord.Status.offline else emojis['idle'] if guild.owner.mobile_status == discord.Status.idle else emojis['greentick'] if guild.owner.mobile_status == discord.Status.online else emojis['?']}`",
                inline = False
            )

            if guild.description:
                embed.add_field(
                    name = "Guild description:", 
                    value = f"`{guild.description}`",
                    inline = False
                )
            
            embed.add_field(
                name = f"Channels:",
                value = f"Text Channels: `{len(guild.text_channels)}`\nVoice Channels: `{len(guild.voice_channels)}`",
                inline = False
            )

            embed.add_field(
                name = f"Members:",
                value = f"Member Count: `{len(guild.members)}`",
                inline = False
            )

            embed.add_field(
                name = f"Boosts:",
                value = f"Boost Count: `{guild.premium_subscription_count}`\nBoosting User Count: `{len(guild.premium_subscribers)}`\nBoosting Tier: `{guild.premium_tier}`",
                inline = False
            )
            
            embed.add_field(
                name = f"Account Creation:",
                value = f"`{guild.created_at.strftime('%d-%m-%Y %H:%M.%S').lower()}`",
                inline = True
            )

            embed.add_field(
                name = f"Days since creation:",
                value = f"`{(datetime.now()-guild.created_at).days}`"
            )

            embed.add_field(
                name = f"My prefixes in this channel:",
                value = f'`{(" or ".join((await db_select(f"""SELECT `guild_prefix` FROM `guilds` WHERE `guild_snowflake_id` = "{ctx.guild.id}";"""))[0][0].split("-")))}`',
                inline = False
            )


            embed.set_image(url=guild.icon_url)

            await ctx.send(embed=embed)
             

        elif channel != None:


            embed = discord.Embed(
                title = f"`#{channel.name}`'s Profile.",
                description = f"Requested by {ctx.author.mention}",
                color = 0x7289DA
            )
            embed.add_field(
                name = f"Creation:",
                value = f"`{channel.created_at.strftime('%d-%m-%Y %H:%M.%S').lower()}`",
                inline = True
            )
            embed.add_field(
                name='\u200b',
                value='\u200b',
                inline=True
            )
            embed.add_field(
                name = "Days since creation:",
                value= f"`{(datetime.now()-channel.created_at).days}`",
                inline = True
            )
            embed.add_field(
                name = "Guild:",
                value = f"`{channel.guild.name}`",
                inline = True
            )
            embed.add_field(
                name='\u200b',
                value='\u200b',
                inline=True
            )
            embed.add_field(
                name = "Guild Category:",
                value = f"`{channel.category.name}`",
                inline = True
            )
            embed.add_field(
                name = "Channel Type:",
                value = f"`{str(channel.type).capitalize()} Channel`",
                inline=True
            )
            if channel.type == discord.ChannelType.text:
                if channel.topic:
                    embed.add_field(
                        name = f"Channel Topic:",
                        value = f"`{channel.topic}`",
                        inline = False
                    )
            
                embed.add_field(
                    name = f"NSFW Channel:",
                    value = f"`{channel.is_nsfw()}`",
                    inline = True
                )
                embed.add_field(
                    name='\u200b',
                    value='\u200b',
                    inline=True
                )
                embed.add_field(
                    name = f"Slowmode:",
                    value = "`False`" if channel.slowmode_delay == 0 else f"`{channel.slowmode_delay}s`",
                    inline = True 
                )
                try:
                    embed.add_field(
                        name = f"Last message time:",
                        value = f"`{ (await utc_to_locat((await channel.fetch_message(channel.last_message_id)).created_at)).strftime('%d-%m-%Y %H:%M.%S%P').lower()}`",
                        inline=False
                    )
                except discord.errors.HTTPException:
                    embed.add_field(
                        name = "Last message time:",
                        value = f"`Well, sadly there is literally no messages in that channel.`",
                        inline = False
                    )

                embed.add_field(
                    name = f"My prefixes in this channel:",
                    value = f'`{(" or ".join((await db_select(f"""SELECT `guild_prefix` FROM `guilds` WHERE `guild_snowflake_id` = "{ctx.guild.id}";"""))[0][0].split("-")))}`',
                    inline = False
                )

            if channel.type == discord.ChannelType.voice:
                embed.add_field(
                    name = f"# Users in channel currently:",
                    value = f"`{len(channel.members)}`",
                    inline = True
                )

                embed.add_field(
                    name = f"User limit:",
                    value = f"`{channel.user_limit}` people",
                    inline = True
                )

                embed.add_field(
                    name = f"Current Bitrate:",
                    value = f"`{channel.bitrate // 1000}kbps`",
                    inline= False
                )

                embed.add_field(
                    name = f"Preferred region:",
                    value = f"`{str(channel.rtc_region).capitalize()}.`" if channel.rtc_region != None else "`Automatic.`",
                    inline = False
                )

            embed.set_image(url=channel.guild.icon_url)
            await ctx.send(embed=embed)

    @commands.command(aliases=['adm_profile', 'aprofile'])
    async def admin_profile(self, ctx, user=None):
        if user == None:
            user = str(ctx.author.mention)
        await ctx.invoke(self.bot.get_command('profile'), mode="admin", profileid=user)

    @commands.command()
    async def id(self, ctx, user:discord.Member=None):
        if user == None:
            user = ctx.author.mention
        await ctx.send(embed=discord.Embed(title=f"Here is {user.name}'s Snowflake ID.", description=f"{user.id}", color=0x00ff00))

    @commands.command()
    async def discuss(self, ctx, *, what):
        temp = what.split(":")
        if len(temp) > 2:
            await ctx.send(embed=discord.Embed(title="You added too many topics and therefore I cannot compute that... Try again with only 1 colon (topic).", color=0xff0000))
            return
        topic = temp[0] if len(temp) > 1 else None
        what = str(temp[1]) if len(temp) > 1 else str(temp[0])
        what = what.split("/")
        what = [x for x in what if not x.isspace() and x != ""]
        if len(what) >= 20:
            await ctx.send(embed=discord.Embed(title="Due to discord limitations, messages can only have 20 reactions, meaning only 20 available...", description="Don't worry, I will still let you choose from the first 20 you provided.", color=0xff0000))
            what = what[:20]
        if len(what) == 0:
            await ctx.send(embed=discord.Embed(title=f"You can't choose between nothing...", color=0xff0000))
            return
        embed=discord.Embed(title="Discussion Time!", description=f"Discussion started by {ctx.author.name}!" if topic == None else f"Topic: `{topic}`", color=0x00ff00)
        if len(what) == 1:
            x = what[0]
            embed.add_field(name=f"`{x[1:-1] if x[0] == ' ' and x[-1] == ' ' else x[1:] if x[0] == ' ' and x[-1] != ' ' else x[:-1] if x[0] != ' ' and x[-1] == ' ' else x}`", value="⠀", inline=False)
        else:
            for y,x in enumerate(what):
                if not x.isspace():
                    if y+1 < 10:
                        embed.add_field(name=f"{emojis[f'{y+1}']} - `{x[1:-1] if x[0] == ' ' and x[-1] == ' ' else x[1:] if x[0] == ' ' and x[-1] != ' ' else x[:-1] if x[0] != ' ' and x[-1] == ' ' else x}`", value="⠀", inline=False)
                    else:
                        embed.add_field(name=f"{emojis[f'{chr(65+(y-9))}']} - `{x[1:-1] if x[0] == ' ' and x[-1] == ' ' else x[1:] if x[0] == ' ' and x[-1] != ' ' else x[:-1] if x[0] != ' ' and x[-1] == ' ' else x}`", value="⠀", inline=False)
        msg = await ctx.send(embed=embed)
        if len(what) == 1:
            await msg.add_reaction(emojis['greentick'])
            await msg.add_reaction(emojis['redtick'])
            return
        for y,x in enumerate(what):
            if y < 9:
                await msg.add_reaction(emojis[f'{y+1}'])       
            else:
                await msg.add_reaction(emojis[f'{chr(65+(y-9))}'])    

    @commands.command()
    async def discussion_append(self, ctx, msgid, title, description):
        try:
            msg = await ctx.fetch_message(msgid)
        except:
            await ctx.reply(embed=discord.Embed(title="This needs to be done in the same channel as the message.", color=0xff0000))
            return
        embed = msg.embeds[0]
        embed.insert_field_at(index=(len(embed.fields)), name=title, value=description)
        await msg.edit(embed=embed)

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
        await ctx.send(embed=discord.Embed(title="Girlfriend check", description=f"{(datetime.now()-datetime.strptime('30-07-2021', '%d-%m-%Y')).days} days without a girlfriend :cry:", color=0xff0000))

def setup(bot):
    bot.add_cog(misc_commands(bot))
