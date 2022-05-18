from unicodedata import category
import discord
from discord.ext import commands
from database import emojis, db_select, utc_to_locat
from datetime import datetime, timedelta
from requests import get
from colorama import Fore, init
init()
import asyncio
from urllib3.exceptions import InsecureRequestWarning
import requests
requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)
class profiles(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def get_data(self, url):
        response = get(url=url,verify=False)
        if response.status_code not in [200, 204]:
            print(Fore.RED + f"CRITICAL : COULD NOT CONNECT TO " + Fore.CYAN + f"{url}" + Fore.RED + f", ERROR STATUS CODE: " + Fore.CYAN + f"{response.status_code} " + Fore.RED + "WITH TEXT: " + Fore.CYAN + f"{response.text}", Fore.YELLOW + "\nWaiting 1 Second before attempting again")
            await asyncio.sleep(1)
            await self.get_data(url)
        else:
            return (response.json())

    async def remove_microseconds(self, ms):
        return ms - timedelta(microseconds=ms.microseconds)

    @commands.command()
    async def profile(self, ctx, profileid:str=None, mode:str="default"):
        try:
            if profileid[1] == "#":
                profileid = profileid[2:-1]
            elif profileid[1] == "@":
                profileid = profileid[3:-1]
            profileid = int(profileid)
            user = None
        except:
            user = ctx.author
        try:
            if user == None:
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
                title=f"User `{user.name}`'s Profile." if mode != "admin" else f"User `{user.name}`'s Profile. (Admin mode)",
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
                since = (await utc_to_locat(member.premium_since)).strftime("%d-%M-%Y %H:%M:%S")
                embed.add_field(
                    name = "User has boosted this server?",
                    value=f"""`{f'Yes, since: {since}' }`""",
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
                balance = (await self.get_data(url=f"https://mc.chippahh.com:6275/api/v1/get_profile?id="+f"{user.id}"))['message']['balance']
                formatted = f'{balance:,.2f}'
                embed.add_field(
                    name = "Chippahhbot Balance:",
                    value= f"`${formatted}`",
                    inline=False
                )
            except Exception as e:
                await ctx.send(e)
                embed.add_field(
                    name=f"Chippahhbot Balance",
                    value="`Could not retrieve info from the API.`",
                    #value="`Chippahhbot api linking is disabled at the moment. Try again later.`",
                    inline=False
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

            try:
                member = member or await ctx.guild.fetch_member(user.id)
                for activity in member.activities:
                    if isinstance(activity, discord.Spotify):
                        embed.add_field(name="Spotify:", value=f"{user.display_name} is currently vibing to:", inline=False)
                        embed.add_field(name="Song:", value=f"`{activity.title}`", inline=True)
                        embed.add_field(name="\u200b", value="\u200b")
                        embed.add_field(name="Artist:" if len(activity.artists) == 1 else "Artists:", value=f"`{', '.join(artist for artist in activity.artists)}`", inline=True)
                        embed.add_field(name="Album:", value=f"`{activity.album}`", inline=True)
                        embed.add_field(name="\u200b", value="\u200b")
                        embed.add_field(name="Started at:", value=f"`{(await utc_to_locat(activity.start)).strftime('%H:%M:%S')}`", inline=True)
                        embed.add_field(name="Duration:", value=f"`{await self.remove_microseconds(activity.duration)}`", inline=True)
                        embed.add_field(name="\u200b", value="\u200b")
                        embed.add_field(name="Time remaining", value=f"`{await self.remove_microseconds((await utc_to_locat(activity.end)) - (await utc_to_locat(datetime.now())))}`", inline=True)
            except Exception as e:
                print(e)

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


def setup(bot):
    bot.add_cog(profiles(bot))