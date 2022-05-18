#!/usr/bin/python3
#This ensures the system knows to use python 
#This is preference, when the bot restarts it starts to print on a new line
import warnings

from discord.flags import Intents
warnings.filterwarnings('ignore', module=r"aiomysql")
import discord
from discord.ext import commands
from datetime import datetime
import asyncio
import random 
import os
import sys
import aiomysql 
from database import command_permission_set, databases, db_commit, db_select, emojis, add_user, permissions, config, determine_prefix
from dateutil.relativedelta import relativedelta
from colorama import Fore, init
init(autoreset=True)
#This initialises colarama, used for changing colours of the outputs to the console outputs.

dbs = databases()
#This runs the databases class, to start the connection and to create any tables that are necessary.


bot = commands.Bot(
command_prefix=determine_prefix,
case_insensitive=True,
intents=discord.Intents.all(),
owner_id=538838470727172117,
strip_after_prefix=True
)
#This initiates the bot, giving it its prefix and telling it the owners Discord Snowflake ID
#command_prefix=determine_prefix <- This runs the function determine_prefix, so for every message the bot sees, it checks the prefix for that guild.

bot.remove_command("help")
#This removes the "help" command because I will use a custom help command later.

async def startup():
    locked_down = await db_select(f"""SELECT `value` FROM `config` WHERE `key` LIKE "locked_down";""")
    locked_down = locked_down[0][0]
    #This checks to see whether the bot was in the locked down state during the last shutdown.


    colours = [Fore.RED, Fore.WHITE, Fore.YELLOW, Fore.GREEN, Fore.BLUE, Fore.MAGENTA,Fore.WHITE, Fore.RED, Fore.YELLOW, Fore.GREEN, Fore.WHITE, Fore.BLUE, Fore.MAGENTA,Fore.RED, Fore.YELLOW, Fore.GREEN, Fore.BLUE, Fore.MAGENTA, Fore.WHITE, Fore.RED]
    for pos, char in enumerate("| COGS ARE LOADING |"):
        print(colours[pos] + f"{char}", end='')
    print(" ")

    for filename in os.listdir('./cogs'):
        if filename.endswith('.py'):
            try:
                bot.load_extension(f'cogs.{filename[:-3]}')
                print(Fore.BLUE + f"| {filename[:-3]} loaded successfully |")
            except Exception as e:
                print(Fore.RED + f"""| {filename[:-3]} was NOT loaded successfully, here is the error: {e} |""")
    #This will load all of the cogs and print any errors to the console if there are any.
    global bot_start_time
    bot_start_time = datetime.now()
    #This records the time that the bot has started.

    if locked_down == "True":
        print(Fore.BLUE + f"Bot starting at: {datetime.now().strftime('%d-%m-%Y @ %H:%M:%S')} **BOT STARTED LOCKED DOWN**" + Fore.WHITE)
    else:
        print(Fore.YELLOW + f"Bot starting at: {datetime.now().strftime('%d-%m-%Y @ %H:%M:%S')} **BOT STARTED REGULARLY**" + Fore.WHITE)
    #This prints out the status of the bot as it loads and the time the bot is starting.
        

    
loop = asyncio.get_event_loop()
#Allows me to use async
loop.run_until_complete(startup())
#This runs the async loop, loading cogs, checking if the bot is locked down


@bot.command(aliases=['reload'])
async def restart(ctx):
    """`This command will reload the bot. Permission level is: 5`"""
    await ctx.send(f"Okay, {ctx.author.name}, restarting now!")
    absolute_path = "F:/NEABOT/MainNEABotFile.py"
    os.execv(sys.executable, ['python'] + sys.argv )
#This command allows me to restart the bot should I need to, if the bot is stuck in a loop or is unable to recover from an error.


async def get_difference_in_s(date2, date1):
    timedelta = date2 - date1
    return timedelta.days * 24 * 3600 + timedelta.seconds

async def conv_secs_to_dhms(seconds):
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)
    return [days, hours, minutes, seconds]

@bot.command()
async def uptime(ctx):
    """`This command will send the uptime of the bot. Permission level is: 1`"""
    deaths = [{"hunger":3},{"falling":315569}, {"dirty water":3}, {"malaria":120}, {"pneumonia":39}, {"trauma at birth":315569}, {"diarrhoea from contaminated water supply":65}]
    deaths = deaths[random.randint(1,len(deaths)-1)]
    method = list(deaths)
    seconds = deaths[method[0]]
    print(deaths)
    bot_uptime = relativedelta(datetime.now(), bot_start_time)
    embed=discord.Embed(title=f'I have been online for \n`{bot_uptime.years}` years \n`{bot_uptime.months}` months \n`{bot_uptime.days}` days \n`{bot_uptime.hours}` hours \n`{bot_uptime.minutes}` minutes \n`{bot_uptime.seconds}` seconds!', color=0x00ffff)
    embed.set_footer(text=f"In that time, {int((datetime.now()-bot_start_time).total_seconds()/seconds)} children have died from {method[0]}")
    await ctx.send(embed=embed)
#This command will send a message of the length of time the bot has been online for.


###############################################################################
#################### Manual Cog Loading/ Unloading ############################
###############################################################################

@bot.group()
async def cog(ctx):
    """`Creates the cog subcommands load, unload and reload. Permission level is: 5`"""
    if ctx.invoked_subcommand == None:
        embed = discord.Embed(
            title=f"{emojis['barrier']} That is not how that works! {emojis['barrier']}",
            description = f"You said `{ctx.message.content}`",
            color = 0xff0000
        )
        embed.set_footer(icon_url=ctx.author.avatar_url, text=f"Attempted by {ctx.author}")
        embed.add_field(name="Here is how to properly use that command:", value=f"{(await determine_prefix(bot, ctx))[0][0]}cog [load/reload/unload] 'cog_name'")
        await ctx.reply(embed=embed)
#This creates a group of commands called cog, meaning subcommands load, reload and unload can be used.
#If the user doesn't use the right subcommand, it tells them the possible subcommands.


@cog.command()
async def load(ctx, *, extension):
    """`This command will load the cog specified in the arguments. Permission level is: 5`"""
    try:
        bot.load_extension(f'cogs.{extension}')
        embed = discord.Embed(
            title = f"Cog `{extension}` was successfully loaded.",
            color = 0x00ff00
        )
        embed.set_footer(text=f"Loaded by {ctx.author}", icon_url=ctx.author.avatar_url)
        await ctx.reply(embed=embed)
        print(Fore.BLUE + f'Cog ~~~{extension}~~~ loaded successfully by {ctx.author.name}')
    except Exception as e:
        embed = discord.Embed(
            title = f"{emojis['barrier']} I can't load that. There is an error in either that cog or the spelling {emojis['warning']}.",
            description = f"The cog you tried to load is `{extension}`",
            color = 0xff0000
        )
        embed.add_field(name=f"**`{e}`**", value=f"{emojis['barrier']}{emojis['warning']}{emojis['barrier']}{emojis['warning']}{emojis['barrier']}{emojis['warning']}{emojis['barrier']}{emojis['warning']}{emojis['barrier']}{emojis['warning']}{emojis['barrier']}{emojis['warning']}{emojis['barrier']}{emojis['warning']}{emojis['barrier']}{emojis['warning']}{emojis['barrier']}{emojis['warning']}{emojis['barrier']}{emojis['warning']}")
        await ctx.send(embed=embed)
        print(Fore.RED + f"""Cog ~~~{extension}~~~ could not be loaded - attempted by {ctx.author.name} but it errored. This was the error:
        {e}""")
#This will attempt to load the cog and tell the user it was loaded, if there is an error, it logs the error and tells the user the error.



@cog.command()
async def reload(ctx, *, extension):
    """`This command will reload the cog specified in the arguments. Permission level is: 5`"""
    try:
        bot.reload_extension(f'cogs.{extension}')
        embed = discord.Embed(
            title = f"Cog `{extension}` was successfully reloaded.",
            color = 0x00ff00
        )
        embed.set_footer(text=f"Reloaded by {ctx.author}", icon_url=ctx.author.avatar_url)
        await ctx.reply(embed=embed)
        print(Fore.BLUE + f'Cog ~~~{extension}~~~ reloaded successfully by {ctx.author.name}')
    except Exception as e:
        embed = discord.Embed(
            title = f"{emojis['barrier']} I can't reload that. There is an error in either that cog or the spelling {emojis['warning']}.",
            description = f"The cog you tried to load is `{extension}`",
            color = 0xff0000
        )
        embed.add_field(name=f"**`{e}`**", value=f"{emojis['barrier']}{emojis['warning']}{emojis['barrier']}{emojis['warning']}{emojis['barrier']}{emojis['warning']}{emojis['barrier']}{emojis['warning']}{emojis['barrier']}")
        await ctx.send(embed=embed)
        print(Fore.RED + f"""Cog ~~~{extension}~~~ could not be reloaded - attempted by {ctx.author.name} but it errored. This was the error:
        {e}""")
#This will attempt to reload the cog and tell the user it was reloaded, if there is an error, it logs the error and tells the user the error. 



@cog.command()
async def unload(ctx, *, extension):
    """`This command will unload the cog specified in the arguments. Permission level is: 5`"""
    try:
        bot.unload_extension(f'cogs.{extension}')
        embed = discord.Embed(
            title = f"Cog `{extension}` was successfully unloaded.",
            color = 0x00ff00
        )
        embed.set_footer(text=f"Unloaded by {ctx.author}", icon_url=ctx.author.avatar_url)
        await ctx.reply(embed=embed)
        print(Fore.BLUE + f'Cog ~~~{extension}~~~ reloaded successfully by {ctx.author.name}')
    except Exception as e:
        embed = discord.Embed(
            title = f"{emojis['barrier']} I can't unload that. Is the cog loaded, or have you spelt it wrong? {emojis['warning']}",
            description = f"The cog you tried to load is `{extension}`",
            color = 0xff0000
        )
        embed.add_field(name=f"**`{e}`**", value=f"{emojis['barrier']}{emojis['warning']}{emojis['barrier']}{emojis['warning']}{emojis['barrier']}{emojis['warning']}{emojis['barrier']}{emojis['warning']}{emojis['barrier']}")
        await ctx.send(embed=embed)
        print(Fore.RED + f"""Cog ~~~{extension}~~~ could not be unloaded - attempted by {ctx.author.name} but it errored. This was the error:
        {e}""")
#This will attempt to unload the cog and tell the user it was unloaded, if there is an error, it logs the error and tells the user the error.


################################################################################################################
##################################### LOCKDOWN COMMANDS GROUP ##################################################
################################################################################################################

@bot.group()
async def lockdown(ctx):
    if ctx.invoked_subcommand == None:
        await ctx.reply(f"{await determine_prefix(bot, ctx.message)}lockdown start/stop")
#This initialises the lockdown command group, with subcommands start/stop. These will be used to start the lockdown process of the bot.

@lockdown.command()
async def start(ctx):
    """`This command will start the lockdown sequence of the bot. Permission Level is: 5`"""
    def check(reaction, user):
        return user == ctx.author
    #I declare this here as I will need a slightly different check in other commands. This check just checks whether the user who used the reaction 
    #was also the person who sent the original message.
    embed=discord.Embed(title="Are you sure about that?", description="React below.")
    lockdown_start_msg = await ctx.reply(embed=embed)
    await lockdown_start_msg.add_reaction(emojis["greentick"])
    await lockdown_start_msg.add_reaction(emojis["redtick"])
    try:
        reaction, user = await bot.wait_for('reaction_add', check=check)
    except asyncio.TimeoutError:
        await ctx.send("I've cancelled the request.") 
    if reaction.emoji == emojis["greentick"] and user == ctx.author:
        await db_commit(f"""UPDATE `config` SET `value` = "True" WHERE `key` = "locked_down";""")
        print(Fore.RED + f"The bot has been put into a locked down state by {ctx.author.name}")
        embed=discord.Embed(
            title = f"{emojis['barrier']}{emojis['warning']}BOT HAS BEEN LOCKED DOWN{emojis['warning']}{emojis['barrier']}",
            description= f"Lockdown started by {ctx.author.name} at {datetime.now().strftime('%d-%m-%Y @ %H:%M.%S')}",
            color = 0xff0000
        )
        embed.set_footer(
            text=f"Only exempt users will now be able to use commands.", 
            icon_url=ctx.author.avatar_url
        )
        await ctx.reply(embed=embed)
    else:
        pass
#This will start the lockdown procedure of the bot and prevent users from executing commmands.

@lockdown.command()
async def stop(ctx):
    """`This command will stop the lockdown sequence of the bot. Permission Level is: 5`"""
    def check(reaction, user):
        return user == ctx.author
    #I declare this here as I will need a slightly different check in other commands. This check just checks whether the user who used the reaction 
    #was also the person who sent the original message.
    embed=discord.Embed(title="Are you sure about that?", description="React below.")
    lockdown_start_msg = await ctx.reply(embed=embed)
    await lockdown_start_msg.add_reaction(emojis["greentick"])
    await lockdown_start_msg.add_reaction(emojis["redtick"])
    try:
        reaction, user = await bot.wait_for('reaction_add', check=check, timeout=15)
    except asyncio.TimeoutError:
        await ctx.send("I've cancelled the request.") 
    if reaction.emoji == emojis["greentick"] and user == ctx.author:
        await db_commit(f"""UPDATE `config` SET `value` = "False" WHERE `key` = "locked_down";""")
        print(Fore.GREEN + f"The bot has been put into a normal state by {ctx.author.name}")
        await ctx.reply(f"Okay, {ctx.author.name}, the bot has been unlocked and now people can execute commands up to their permission level.")
    else:
        pass
#This will end the lockdown procedure of the bot and allow users to execute commmands.



@lockdown.group()
async def exempt(ctx):
    """`This initialises the subcommands add/remove for the lockdown exemption. Permission level is: 5`"""
    if ctx.invoked_subcommand == None:
        embed=discord.Embed(title=f"{emojis['barrier']}Thats now how to use that command, {ctx.author.name}!\nHere's how to use it properly.", description=f"`{(await determine_prefix(bot, ctx.message))[0][0]}lockdown exempt [add/remove] [user_id]`", color=0xff000)
        await ctx.reply(embed=embed)
#This creates the exempt group that allows me to add or remove users that will be exempt to the lockdown, which prevents anyone from executing commands if they are not exempt.

@exempt.command()
async def add(ctx, user:discord.Member):
    """`This will add members to the lockdown exempt list- allowing them to use commands while the bot is locked down. Permission Level is: 5`"""
    if ctx.author.id == 538838470727172117:
        try:
            await db_commit(f"""UPDATE `users` SET `lockdown_exempt` = "True" WHERE `user_snowflake_id` LIKE "{user.id}";""")
            print(Fore.GREEN + f"{user.name} has been made exempt from lockdowns by {ctx.author.name}")
            await ctx.reply(f"{user.name} has been made exempt from lockdowns.")
        except aiomysql.IntegrityError:
            await ctx.reply(f"{user.name} is already exempt from lockdown.")
#This will be used to add users to the lockdown exemption list, for reasons such as testing.

@exempt.command()
async def remove(ctx, user:discord.Member):
    """`This will remove members from the exempt list- preventing them from executing commands while the bot is locked down. Permission Level is: 5`"""
    if ctx.author.id == 538838470727172117:
        try:
            await db_commit(f"""UPDATE `users` SET `lockdown_exempt` = "False" WHERE `user_snowflake_id` LIKE "{user.id}";""")
            print(Fore.GREEN + f"{user.name} has been successfully removed from the lockdown exemption list by {ctx.author.name}")
            await ctx.reply(f"{user.name} is no longer exempt from lockdowns.")
        except Exception as e:
            commands.CommandInvokeError(e)
#This will be used to remove members from the lockdown exemption list, preventing them from using commands while the bot is locked down.



@bot.command()
async def adduser(ctx, member:discord.Member):
    """`This allows a user to manually be added to the database. Permission Level is: 5`"""
    result = await add_user(member, "manual")
    embed = discord.Embed(
        title = f"{member} has been added to the database" if result != "Already Exists" else f"{emojis['barrier']}{member} already exists in the database{emojis['warning']}",
        color = 0x00ff00 if result != "Already Exists" else 0xff0000
    )
    embed.set_footer(text=f"{member} given permission level 1." if result != "Already Exists" else f"Attempted by {ctx.author}", icon_url=member.avatar_url if result != "Already Exists" else ctx.author.avatar_url)
    await ctx.send(embed=embed)
#This command allows me to manually add users to the database.



@bot.check
async def permscheck(ctx):
    if ctx.command.qualified_name == "perms user" and ctx.author.id == 538838470727172117:
        print(Fore.GREEN + "perms user [5] Executed by Harrison. Permissions check was bypassed.")
        return True
        #This means if my permission level is decreased by another person with level 5 permissions, I can put my permission level back up, bypassing the permission level.
    owner = bot.get_user(538838470727172117)
    #Gets the owner user as an object.
    def check(reaction, user):
        return user == owner
    #This checks if the user is the bot owner.
    try:
        exempt_users = (await db_select(f"""SELECT `user_snowflake_id` FROM `users` WHERE `lockdown_exempt` = "True";"""))[0]
        #Finds all users that are exempt from the lockdown in the database.
    except IndexError:
        exempt_users = []
        #If no users are exempt it returns an empty list, otherwise it throws an error.
    
    locked_down = (await db_select(f"""SELECT `value` FROM `config` WHERE `key` LIKE "locked_down";"""))[0][0]
    
    try:
        user_perm_level = (await db_select(f"""SELECT `permission_level` FROM `users` WHERE `user_snowflake_id` LIKE "{ctx.author.id}";"""))[0][0]
        #Checks the users permission level.
    except:
        await add_user(ctx.author)
        print(Fore.RED + f"{ctx.author} was not part of the users database but has now been added.")
        user_perm_level = 1
        #This adds them to the database if they are not found.

    try:
        command_perm_level = (await db_select(f"""SELECT `command_permission_level` FROM `commands` WHERE `command_name` LIKE "{ctx.command.name}";"""))[0][0]
        #Finds the command permission level in the database.
    except: 
        embed = discord.Embed(
            title = f"{emojis['barrier']} Uh oh, {ctx.author.name}, something went wrong there. {emojis['warning']}",
            description = f"The bot owner has been informed!",
            color = 0xff0000
            )
        await ctx.reply("There has been an error with this. The bot owner has been informed.")
        await command_permission_set(ctx.command.name, owner, bot, ctx)
        return False
        #If command permission level is not there, a message is sent to the owner to fix it.

    if locked_down == "True":
        if str(ctx.author.id) not in exempt_users:
            embed=discord.Embed(title="Sorry!", description=f"{emojis['barrier']}{emojis['warning']}The bot is currently locked down and is not taking commands right now. Try again later!{emojis['warning']}{emojis['barrier']}", color=0xff0000)
            await ctx.reply(embed=embed)
            if ctx.command == ctx.command.qualified_name:
                print(Fore.RED + f"{ctx.command} [{command_perm_level}] Attempted by {ctx.author} [{user_perm_level}] at {datetime.now().strftime('%d-%m-%Y @ %H:%M.%S')} -> Bot locked down")
            return False
            #This fails the bot check and doesn't allow the command to be executed.
        else:
            print(Fore.GREEN + f"{ctx.command.qualified_name} [{command_perm_level}] Attempted by {ctx.author} [{user_perm_level}] at {datetime.now().strftime('%d-%m-%Y @ %H:%M.%S')} -> Bot locked down but user is exempt.")
            return True
            #If the user is in exempt_users the bot check is passed even if the bot is locked down. This allows any debugging to happen by the trusted users.
    elif locked_down == "False":
        if user_perm_level >= command_perm_level:
            if ctx.command == ctx.command.qualified_name:
                
                print(Fore.GREEN + f"{ctx.command} [{command_perm_level}] -> Attempted by {ctx.author} [{user_perm_level}] at {datetime.now().strftime('%d-%m-%Y @ %H:%M.%S')} -> Permissions are sufficient.")
            return True
        else:
            embed = discord.Embed(title=f"{emojis['warning']} Uh oh, You can't do that! {emojis['warning']}", color=0x7289DA)
            embed.add_field(name = "Your permissions are insufficient.", value=f"Permission Level required is **{command_perm_level} - {permissions[f'{command_perm_level}']}**\nBut your permission level is **{user_perm_level} - {permissions[f'{user_perm_level}']}**")
            await ctx.reply(embed=embed) 
            if ctx.command == ctx.command.qualified_name:
                
                print(Fore.RED + f"{ctx.command} [{command_perm_level}] -> Attempted by {ctx.author} [{user_perm_level}] at {datetime.now().strftime('%d-%m-%Y @ %H:%M.%S')} -> Permissions were insufficient.")
            return False


@bot.command(aliases = ['halp', 'helph', 'halph'])
async def help(ctx, *cog):
    """`Shows this command. Permission Level is: 1`"""
    show_hidden = False

    # Do i show hidden commands

    if not cog:

        # For when only the command is invoked
        # Lists all cogs and uncategorized commands
        if ctx.guild:
            prefix = " / ".join((await db_select(f"""SELECT `guild_prefix` FROM `guilds` WHERE `guild_snowflake_id` = "{ctx.guild.id}";"""))[0][0].split("-"))
        else:
            prefix = " / ".join((await db_select(f"""SELECT `dm_prefix` FROM `users` WHERE `user_snowflake_id` = "{ctx.author.id}";"""))[0][0].split("-"))
        halp=discord.Embed(
            description = f'My prefix here is `{prefix}`\nUse `{prefix}help **cog**` for the commands\nIf you know the command name use `{prefix}help **command**`\nThe cog name must be exactly what is listed below',
            colour = 0xff0000)
        halp.set_author(name='Cogs and uncategorized commands.')
        cogs_desc = ''
        for x in bot.cogs:
            if not len(bot.cogs[x].get_commands()) == 0 or show_hidden:
                try:
                    cog_help = bot.cogs[x].__doc__.split('\n')[0]
                except AttributeError:
                    cog_help = 'No help text for this command'
                cogs_desc += (f'{x} - {cog_help}'.format(x,bot.cogs[x].__doc__)+'\n')
        if cogs_desc:
            halp.add_field(name='Cogs',value=cogs_desc,inline=False)
        cmds_desc = ''
        for y in bot.walk_commands():
            if not y.cog_name and not y.parent:
                if show_hidden:
                    try:
                        command_help = y.help.split('\n')[0]
                    except AttributeError:
                        command_help = 'No help text for this command'
                    cmds_desc += f"{y.name} - {command_help}\n"
                else:
                    if not y.hidden:
                        try:
                            command_help = y.help.split('\n')[0]
                        except AttributeError:
                            command_help = 'No help text for this command'
                        cmds_desc += f"{y.name} - {command_help}\n"
        if cmds_desc:
            halp.add_field(name='Uncatergorized Commands',value=cmds_desc,inline=False)
        await ctx.send(embed=halp)

    elif len(cog) == 1 and cog[0] in bot.cogs:

        # If only a cog is selected
        # Lists the commands in selected cog
        
        commands = bot.cogs[cog[0]].get_commands()
        cog_commands = ''
        for command in bot.cogs[cog[0]].walk_commands():
            if not command.parent:
                if show_hidden:
                    try:
                        command_help = command.help.split('\n')[0]
                    except AttributeError:
                        command_help = 'No help text for this command'
                    cog_commands += f"{command.name} - {command_help}\n"
                else:
                    if not command.hidden:
                        try:
                            command_help = command.help.split('\n')[0]
                        except AttributeError:
                            command_help = 'No help text for this command'
                        cog_commands += f"{command.name} - {command_help}\n"
        if cog_commands:
            embed = discord.Embed(colour = 0xff0000, title = f'Use {await bot.get_prefix(ctx.message)}help **command** for more detailed help and subcommands', description = f'{bot.cogs[cog[0]].description}')
            embed.set_author(name = f'Commands in the cog {cog[0]}')
            embed.add_field(name = 'Commands - Description', value = cog_commands)
        else:
            embed = discord.Embed(colour = 0xff00ff, title = f"You can't do much with this cog.")
            embed.set_author(name = f"This cog only has listeners.")
        if show_hidden:
            listeners = ""
            for listener in bot.cogs[cog[0]].get_listeners():
                listeners += f"{listener[0]} - {listener[1].__doc__}\n"
            if listeners:
                embed.add_field(name = 'Listeners', value = listeners)
        await ctx.send(embed=embed)

    elif cog[0] not in bot.cogs:

        # If not a cog
        # Shows help for command and subcommands if applicable

        for command in bot.walk_commands():
            if not command.parent and command.name == cog[0]:
                if show_hidden:
                    if len(cog) >= 1:
                        cog = list(cog)
                        del cog[0]
                        for subcommand in cog:
                            # try:
                            try:
                                for sub_subcommand in command.commands:
                                    if sub_subcommand.name == subcommand:
                                        command = sub_subcommand
                            except AttributeError as e:
                                print(e)
                            # except:
                            #     pass

                    embed = discord.Embed(description = f'```{command.help}```', colour = 0xff0000)
                    if command.aliases:
                        embed.set_author(name=f'{await bot.get_prefix(ctx.message)}{command} in cog {command.cog_name}\nAliases = {", ".join(command.aliases)}')
                    else:
                        embed.set_author(name=f'{await bot.get_prefix(ctx.message)}{command} in cog {command.cog_name}')
                    try:
                        for subcommand in command.commands:
                            try:
                                _help = subcommand.help.split("\n")[0]
                            except AttributeError:
                                embed.add_field(name=f'Subcommand: **{subcommand.name}**', value=f'This command has no help text')
                            else:    
                                embed.add_field(name=f'Subcommand: **{subcommand.name}**', value=f'{_help}')
                    except AttributeError as e:
                        embed.description += '\n\n**This command has no subcommands**'
                    await ctx.send(embed=embed)
                    return
                else:
                    if not command.hidden:
                        if len(cog) >= 1:
                            cog = list(cog)
                            del cog[0]
                            for subcommand in cog:
                                # try:
                                try:
                                    for sub_subcommand in command.commands:
                                        if sub_subcommand.name == subcommand:
                                            command = sub_subcommand
                                except AttributeError as e:
                                    print(e)
                                # except:
                                #     pass

                        embed = discord.Embed(description = f'```{command.help}```', colour = 0xff0000)
                        if command.aliases:
                            embed.set_author(name=f'{await bot.get_prefix(ctx.message)}{command} in cog {command.cog_name}\nAliases = {", ".join(command.aliases)}')
                        else:
                            embed.set_author(name=f'{await bot.get_prefix(ctx.message)}{command} in cog {command.cog_name}')
                        try:
                            for subcommand in command.commands:
                                try:
                                    _help = subcommand.help.split("\n")[0]
                                except AttributeError:
                                    embed.add_field(name=f'Subcommand: **{subcommand.name}**', value=f'This command has no help text')
                                else:    
                                    embed.add_field(name=f'Subcommand: **{subcommand.name}**', value=f'{_help}')
                        except AttributeError as e:
                            embed.description += '\n\n**This command has no subcommands**'
                        await ctx.reply(embed=embed)
                        return
        await ctx.reply(f"{emojis['barrier']} Looks like that doesn't exist {emojis['barrier']}", f"Check the base {await bot.get_prefix(ctx.message)}help command for the correct capitalisation and spelling.")
        

    else:
        raise ctx.reply(f"{emojis['barrier']} You managed to break something {emojis['barrier']}", "Please tell me what you did thanks")

    
    
token=config['token']
bot.run(token)
