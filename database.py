import asyncio
import aiomysql
from datetime import datetime, timezone
import calendar
import discord
from colorama import Fore, Back, Style, init
import json
import os 
from discord import user
from discord.ext.commands.core import command
import pytz

init()

def initiate_config():
    with open(f"config.json", 'r') as conf_file:
        conf = conf_file.read()
        return (conf)
        #Loads config from a text file which has token and API keys in.
    #Loads this into a json object for easier use later
global config
config = (json.loads(initiate_config()))

class databases():

    def __init__(self):
        loop = asyncio.get_event_loop()
        #This allows me to use async.

        loop.run_until_complete(self.create_database())
        #This runs the create_database function to create all databases if they do not exist.

        loop.run_until_complete(self.create_pool())
        #This runs the create_pool function to connect to the database and assign it to a variable 
        

    async def create_pool(self):
        #This creates the pool and connects to it. It uses a global variable so that it can be used throughout this file, which will be important for the functions later
        global pool 
        pool = await aiomysql.create_pool(host = '127.0.0.1', port = 3306, user = 'harrison', password = r"ha43RE15", db = "neabot", autocommit = True)
        

    async def create_database(self):
        #This connects to the database and creates the databases if they have not been made yet. 
        database = "neabot"
        async with aiomysql.connect(host = '127.0.0.1', port = 3306, user = 'harrison', password = r"ha43RE15", db = "neabot", autocommit = True) as conn:
            #Initial connection using async.

            cursor = await conn.cursor()
            #This is getting a cursor for the queries.

            try:
                await cursor.execute(f"""CREATE SCHEMA IF NOT EXISTS `{database}`;""")
            except aiomysql.IntegrityError:
                pass
            #This creates the schema (database) if it doesn't exist
            
            try:
                await cursor.execute(f"""USE `{database}`;""")
            except aiomysql.IntegrityError:
                pass
            #This ensures that the database just made is used for all further queries
            
            try:
                await cursor.execute(f"""CREATE TABLE IF NOT EXISTS users(
                `log_id` INT PRIMARY KEY AUTO_INCREMENT,
                `name` TEXT NOT NULL,
                `user_snowflake_id` VARCHAR(18) NOT NULL UNIQUE,
                `last_online` DATETIME,
                `last_message_time` DATETIME,
                `permission_level` INT DEFAULT 1 CHECK (permission_level <= 5 AND permission_level > 0),
                `lockdown_exempt` TEXT,
                `balance` DECIMAL(65,2),
                `last_claim` DATE,
                `claim_streak` INT DEFAULT 0,
                `dm_prefix` TEXT DEFAULT "£"
                );""")
                print(Fore.MAGENTA + "DATABASE : Users table has been created / loaded")
            except Exception as e:
                print(Fore.RED + f"DATABASE : CRITICAL ERROR -> Users table COULD NOT BE CREATED / LOADED! The Error is:\n{e}")
            #This is creating the users table, where things such as permission level and the Users Unique Discord ID is stored.

            try:
                await cursor.execute(f"""CREATE TABLE IF NOT EXISTS commands(
                `log_id` INT PRIMARY KEY AUTO_INCREMENT,
                `command_name` VARCHAR(256) UNIQUE,
                `command_permission_level` INT DEFAULT 5 CHECK (command_permission_level <= 5 AND command_permission_level > 0)
                );""")
                print(Fore.MAGENTA + "DATABASE : Commands table has been created / loaded")
            except Exception as e:
                print(Fore.RED + f"DATABASE : CRITICAL ERROR -> Commands table COULD NOT BE CREATED / LOADED! The Error is:\n{e}")
            #This is creating the commands table, where command names and the command permission level will be stored.
            
            try:
                await cursor.execute(f"""CREATE TABLE IF NOT EXISTS guilds(
                `log_id` INT PRIMARY KEY AUTO_INCREMENT,
                `guild_name` TEXT NOT NULL,
                `guild_snowflake_id` VARCHAR(18) NOT NULL UNIQUE,
                `guild_prefix` TEXT DEFAULT NULL,
                `guild_join_time` DATETIME NOT NULL,
                `guild_leave_time` DATETIME, 
                `guild_casino_jackpot` DECIMAL(65,2) DEFAULT 200 CHECK (guild_casino_jackpot >= 200),
                `snake_highscore` INT DEFAULT 0,
                `fastest_claim_date` VARCHAR(10) DEFAULT NULL,
                `fastest_claim_seconds` TEXT DEFAULT NULL,
                `connected_to_vc` VARCHAR(18) DEFAULT NULL
                );""")
                print(Fore.MAGENTA + "DATABASE : Guilds table has been created / loaded")
            except Exception as e:
                print(Fore.RED + f"DATABASE : CRITICAL ERROR -> Guilds table COULD NOT BE CREATED / LOADED! The Error is:\n{e}")
            #This is creating the guild (servers) table, where information about the guild will be stored, such as the Guild Name, Guild ID and Guild Jackpot.
            
            try:
                await cursor.execute(f"""CREATE TABLE IF NOT EXISTS config(
                `key` VARCHAR(255) UNIQUE,
                `value` VARCHAR(255)
                );""")
                print(Fore.MAGENTA + "DATABASE : Config table has been created / loaded")
            except Exception as e:
                print(Fore.RED + f"DATABASE : CRITICAL ERROR -> Config table COULD NOT BE CREATED / LOADED! The Error is:\n{e}")
            #This is creating the config table, where basic information such as the Bot's Run Token is stored, along with the Default Prefix
            
            for key,value in config.items():
                try:    
                    await cursor.execute(f"""INSERT INTO `config`(`key`, `value`) VALUES ("{key}","{value}");""")
                    print(Fore.MAGENTA + f"DATABASE : Config has been loaded into the config table (Key = {key}, Value = {value})")
                except aiomysql.IntegrityError:
                    print(Fore.CYAN + f"DATABASE : INFO -> CONFIG VALUES (Key = {key}, Value = {value}) ALREADY EXIST IN THE CONFIG TABLE.")
                except Exception as e:
                    print(Fore.RED + f"DATABASE : CRITICAL ERROR ->  CONFIG VALUES (Key = {key}, Value = {value}) COULD NOT BE LOADED INTO THE CONFIG TABLE! The Error is:\n{e}")
                #This inserts all of the default configs into the database
            #This is in a try except because if the config is already loaded into the database then it is not necessary to re-add them.
            
            try:
                await cursor.execute(f"""CREATE TABLE IF NOT EXISTS messages(
                `log_id` INT PRIMARY KEY AUTO_INCREMENT,
                `message_snowflake_id` VARCHAR(18) NOT NULL UNIQUE,
                `message_time_sent` DATETIME,
                `message_guild_name` TEXT,
                `message_guild_snowflake_id` VARCHAR(18),
                `message_channel_name` TEXT,
                `message_channel_snowflake_id` VARCHAR(18),
                `message_author_name` TEXT,
                `message_author_snowflake_id` VARCHAR(18),
                `message_content` TEXT
                );""")
                print(Fore.MAGENTA + "DATABASE : Messages table has been created / loaded")
            except Exception as e:
                print(Fore.RED + f"DATABASE : CRITICAL ERROR -> Messages table COULD NOT BE CREATED / LOADED! The Error is:\n{e}")
            #This creates the table where information about every message will be saved.

            try:
                await cursor.execute(f"""CREATE TABLE IF NOT EXISTS edits(
                `log_id` INT PRIMARY KEY AUTO_INCREMENT,
                `message_snowflake_id` VARCHAR(18) NOT NULL,
                `message_time_sent` DATETIME,
                `message_guild_name` TEXT,
                `message_guild_snowflake_id` VARCHAR(18),
                `message_channel_name` TEXT,
                `message_channel_snowflake_id` VARCHAR(18),
                `message_author_name` TEXT,
                `message_author_snowflake_id` VARCHAR(18),
                `message_content_before` TEXT,
                `message_content_after` TEXT,
                `message_edit_time` DATETIME
                );""")
                print(Fore.MAGENTA + "DATABASE : Edited Messages table has been created / loaded")
            except Exception as e:
                print(Fore.RED + f"DATABASE : CRITICAL ERROR -> Edited Messages table COULD NOT BE CREATED / LOADED! The Error is:\n{e}")
            #This creates the table where information about any messages that are edited will be saved, such as edit time.

            try:
                await cursor.execute(f"""CREATE TABLE IF NOT EXISTS deletes(
                `log_id` INT PRIMARY KEY AUTO_INCREMENT,
                `message_snowflake_id` VARCHAR(18) NOT NULL UNIQUE,
                `message_time_sent` DATETIME,
                `message_guild_name` TEXT,
                `message_guild_snowflake_id` VARCHAR(18),
                `message_channel_name` TEXT,
                `message_channel_snowflake_id` VARCHAR(18),
                `message_author_name` TEXT,
                `message_author_snowflake_id` VARCHAR(18),
                `message_delete_time` DATETIME
                );""")
                print(Fore.MAGENTA + "DATABASE : Deleted Messages table has been created / loaded")
            except Exception as e:
                print(Fore.RED + f"DATABASE : CRITICAL ERROR -> Deleted Messages table COULD NOT BE CREATED / LOADED! The Error is:\n{e}")
            #This creates the table where information about any messages that are deleted will be saved, such as delete time.

            try:
                await cursor.execute(f"""CREATE TABLE IF NOT EXISTS transactions(
                `log_id` INT PRIMARY KEY AUTO_INCREMENT,
                `type` TEXT,
                `payor_name` TEXT,
                `payor_snowflake_id` VARCHAR(18),
                `payor_balance_before` DECIMAL(65, 2),
                `payor_balance_after` DECIMAL(65, 2),
                `payee_name` TEXT,
                `payee_snowflake_id` VARCHAR(18),
                `payee_balance_before`DECIMAL(65, 2),
                `payee_balance_after` DECIMAL(65, 2),
                `amount_paid` DECIMAL(65, 2),
                `time_paid` DATETIME,
                `description` TEXT
                );""")
                print(Fore.MAGENTA + "DATABASE : Transactions table has been created / loaded")
            except Exception as e:
                print(Fore.RED + f"DATABASE : CRITICAL ERROR -> Transactions table COULD NOT BE CREATED / LOADED! The Error is:\n{e}")
            #This creates the table where information about transactions such as the Pay command will be saved, such as the amount paid

            try:
                await cursor.execute(f"""CREATE TABLE IF NOT EXISTS casino_log(
                `log_id` INT PRIMARY KEY AUTO_INCREMENT,
                `game` TEXT,
                `game_time` DATETIME,
                `outcome_of_game` TEXT,
                `player_outcome` TEXT,
                `player_name` TEXT,
                `player_snowflake_id` VARCHAR(18),
                `bet_amount` DECIMAL(65, 2),
                `paid_out_amount` DECIMAL(65, 2),
                `guild_name` TEXT,
                `channel_name` TEXT,
                `description` TEXT
                );""")
                print(Fore.MAGENTA + "DATABASE : Casino Log table has been created / loaded")
            except Exception as e:
                print(Fore.RED + f"DATABASE : CRITICAL ERROR -> Casino Log table COULD NOT BE CREATED / LOADED! The Error is:\n{e}")
            #This creates the table where casino logs will be stored.

            try:
                await cursor.execute(f"""CREATE TABLE IF NOT EXISTS covid_text_channels(
                    `log_id` INT PRIMARY KEY AUTO_INCREMENT,
                    `channel_name` TEXT,
                    `channel_snowflake_id` VARCHAR(18) UNIQUE, 
                    `guild_owner_name` TEXT,
                    `guild_owner_snowflake_id` VARCHAR(18),
                    `guild_name` TEXT,
                    `guild_snowflake_id` VARCHAR(18),
                    `date_subscribed` DATETIME
                )""")
                print(Fore.MAGENTA + "DATABASE : covid guilds table has been created / loaded")
            except Exception as e:
                print(Fore.RED + f"DATABASE : CRITICAL ERROR -> covid text channels table COULD NOT BE CREATED / LOADED! The Error is:\n{e}")

            try:
                await cursor.execute(f"""CREATE TABLE IF NOT EXISTS covid_users(
                    `log_id` INT PRIMARY KEY AUTO_INCREMENT,
                    `user_name` TEXT,
                    `user_snowflake_id` VARCHAR(18) UNIQUE,
                    `date_subscribed` DATETIME
                )""")
                print(Fore.MAGENTA + "DATABASE : covid users table has been created / loaded")
            except Exception as e:
                print(Fore.RED + f"DATABASE : CRITICAL ERROR -> covid users table COULD NOT BE CREATED / LOADED! The Error is:\n{e}")

            try:
                await cursor.execute(f"""CREATE TABLE IF NOT EXISTS covid_logs(
                    `log_id` INT PRIMARY KEY AUTO_INCREMENT,
                    `date` VARCHAR(10) UNIQUE,
                    `daily_cases` INT,
                    `cumulative_cases` INT,
                    `daily_deaths` INT,
                    `cumulative_deaths` INT
                )""")
                print(Fore.MAGENTA + "DATABASE : covid logs has been created / loaded")
            except Exception as e:
                print(Fore.RED + f"DATABASE : CRITICAL ERROR -> covid logs table COULD NOT BE CREATED / LOADED! The Error is:\n{e}")

            try:
                await cursor.execute(f"""CREATE TABLE IF NOT EXISTS covid_voice_channels(
                    `log_id` INT PRIMARY KEY AUTO_INCREMENT,
                    `channel_name` TEXT,
                    `channel_snowflake_id` VARCHAR(18) UNIQUE,
                    `guild_owner_name` TEXT,
                    `guild_owner_snowflake_id` VARCHAR(18),
                    `guild_name` TEXT,
                    `guild_snowflake_id` VARCHAR(18),
                    `date_subscribed` DATETIME
                    )""")
                print(Fore.MAGENTA + "DATABASE : covid voice channels table has been created / loaded")
            except Exception as e:
                 print(Fore.RED + f"DATABASE : CRITICAL ERROR -> covid voice channels table COULD NOT BE CREATED / LOADED! The Error is:\n{e}")

async def determine_prefix(bot, message):
    try:
        if message.guild != None:
            try:
                prefix = (await db_select(f"""SELECT `guild_prefix` FROM `guilds` WHERE `guild_snowflake_id` = "{message.guild.id}";"""))[0][0].split("-")
                for x in prefix:
                    if message.content[0] == x:
                        return x
                return "debug "
            except IndexError:
                return config['default_prefix']
            except Exception as e:
                print(e)
        else:
            try:
                prefix = (await db_select(f"""SELECT `dm_prefix` FROM `users` WHERE `user_snowflake_id` = "{message.author.id}";"""))[0][0].split("-")
                for x in prefix:
                    if message.content[0] == x:
                        return x
                return "debug "
            except IndexError:
                return config['default_prefix']
            except Exception as e:
                print(e)
    except Exception as e:
        print(e)

async def utc_to_locat(utc_dt):
    return utc_dt.replace(tzinfo=timezone.utc).astimezone(tz=pytz.timezone("Europe/London"))

async def already_exists(what, tuples_tuples):
    return False if (any(str(what) in i for i in tuples_tuples)) else True

async def db_select(query):
    #This allows me to query the database. I will import this in other files to avoid having to write it out several times.
    global pool
    async with pool.acquire() as conn:
        cursor = await conn.cursor()
        await cursor.execute(query)
        result = await cursor.fetchall()
        return result

async def db_commit(query):
    #This allows me to commit things to the database. I will import this in the other files to ensure there are no clashes while trying to add to the database.
    global pool
    async with pool.acquire() as conn:
        cursor = await conn.cursor()
        await cursor.execute(query)

async def add_user(user:discord.Member, type:str="normal"):
    try:
        await db_commit(f"""INSERT INTO `users`(`name`,`user_snowflake_id`,`last_online`,`permission_level`,`lockdown_exempt`, `balance`) VALUES ("{user.name}","{user.id}","{datetime.now()}",1,"False",200.00);""")
        print(Fore.GREEN + f"{user.name} has been added to the database as a new user.")
    except aiomysql.IntegrityError:
        print(Fore.RED + f"{user.name} was attempted to be added to the database but already exists.") if not type == "silent" else type
        if type == "manual":
            return "Already Exists"
#This function will be used to add users to the database.

async def add_guild(guild:discord.Guild, type:str="normal"):
    try:
        await db_commit(f"""INSERT INTO `guilds`(`guild_name`,`guild_snowflake_id`,`guild_prefix`,`guild_join_time`) VALUES ("{guild.name}","{guild.id}","£", "{datetime.now()}");""")
        print(Fore.GREEN + f"{guild.name} has been added to the database as a new guild.")
    except aiomysql.IntegrityError:
        print(Fore.RED + f"{guild.name} was attempted to be added to the database but already exists.") if not type == "silent" else type
    
#This function will allow me to add guilds to the database.

async def reset_user(user:discord.Member):
    await db_commit(f"""DELETE FROM `users` WHERE `user_snowflake_id` LIKE "{user.id}";""")
    await add_user(user)
    print(Fore.MAGENTA + f"{user.name} has successfully been reset to the defaults.")
#This function will be used to reset a user in the database by deleting the information about them and then recreating their profile with the add_user function.

async def command_permission_set(command_name:str, owner:discord.Member, bot, ctx, level:int=None):
    if level is not None and 5 < level > 0:
        await ctx.reply("The permission level can only be between 1-5.")
        return
    try:
        permissionlevel = (await db_select(f"""SELECT `command_permission_level` FROM `commands` WHERE `command_name` = "{command_name}";"""))[0][0]
    except IndexError:
        permissionlevel = 0

    def check(reaction, user):
        return user == owner

    if level == None:
        dm_input = True
        permission_level_message = await owner.send(f"The command `{command_name}` has the permission level {permissionlevel}, select the permission level you want to give it now.")
        for level in ["1","2","3","4","5"]:
            await permission_level_message.add_reaction(emojis[level])
        try:
            reaction, user = await bot.wait_for('reaction_add', check=check, timeout=30)
            level = next((name for name, emoji in emojis.items() if emoji == reaction.emoji), None)
        except asyncio.TimeoutError:
            await permission_level_message.edit("The request has timed out and now you will either need to: \n1: Wait for the command to be attempted again\n2: Commit it to the database manually.")
            return
    else:
        dm_input = False

    if permissionlevel == 0:
        await db_commit(f"""INSERT INTO `commands`(`command_name`,`command_permission_level`) VALUES ("{command_name}", "{level}");""")
    else:
        await db_commit(f"""UPDATE `commands` SET `command_permission_level` = "{level}" WHERE `command_name` = "{command_name}";""")

    if dm_input == True:
        await owner.send(f"Okay, I've made the permission level of `{command_name}` -> `{level}`")
    
    permschannelid = config['permissions_channel']
    permschannel = bot.get_channel(permschannelid)
    embed = discord.Embed(title="Permission level changed", description=f"Changed by `{owner.name}` in `{ctx.guild.name if ctx.guild else 'DMs'}` - `{ctx.channel.name if ctx.guild else 'DMs'}`", color=0x00FF00)
    embed.set_footer(text=f"Permission was changed at: `{datetime.now().strftime('%d-%m-%Y @ %H:%M.%S')}`")
    embed.add_field(name=f"{emojis[f'{permissionlevel}']} -> {emojis[f'{level}']}", value=f"The permision level of `{command_name}` is now `{level}`")
    await permschannel.send(embed=embed)
    print(Fore.MAGENTA + f"COMMAND : Permission level of the command {command_name} changed from {permissionlevel} to {level} by {owner.name} at {datetime.now().strftime('%d-%m-%Y @ %H:%M.%S')}")

async def user_permission_set(user:discord.Member, bot, ctx, level:int):
    if 5 < level or level < 0:
        await ctx.reply("The permission level can only be between 1-5.")
        return
    try:
        permission_level = (await db_select(f"""SELECT `permission_level` FROM `users` WHERE `user_snowflake_id` = "{user.id}";"""))[0][0]
    except IndexError:
        print(Fore.RED + f"{user} is not part of the database.")
        await ctx.reply(f"That user is not in any mutual servers with me, I can't add them to the database.")
        return
    await db_commit(f"""UPDATE `users` SET `permission_level` = "{level}" WHERE `user_snowflake_id` = "{user.id}";""")
    embed=discord.Embed(
        title = f"{user} is now permission level {level} - {permissions[f'{level}']}",
        color=0x00ff00
    )
    embed.add_field(name=f"**Permission level changed from:**", value=f"**`{permission_level} - {permissions[f'{permission_level}']}`** -> **`{level} - {permissions[f'{level}']}`**")
    embed.set_thumbnail(url=user.avatar_url)
    await ctx.reply(embed=embed)
    permschannelid = config['permissions_channel']
    permschannel = bot.get_channel(permschannelid)
    embed = discord.Embed(title="Permission level changed", description=f"Changed by `{ctx.author}` in `{ctx.guild.name if ctx.guild else 'DMs'}` - `{ctx.channel.name if ctx.guild else 'DMs'}`", color=0x00FF00)
    embed.set_footer(text=f"Permission was changed at: `{datetime.now().strftime('%d-%m-%Y @ %H:%M.%S')}`")
    embed.add_field(name=f"{emojis[f'{permission_level}']} -> {emojis[f'{level}']}", value=f"The permision level of `{user.name}` is now `{level}`")
    await permschannel.send(embed=embed)
    print(Fore.MAGENTA + f"USER : Permission level of {user} changed from {permission_level} to {level} by {ctx.author} at {datetime.now().strftime('%d-%m-%Y @ %H:%M.%S')}")

async def get_current_covid_date():
    try:
        result = await db_select(f"""SELECT `date` FROM `covid_logs` ORDER BY `log_id` DESC""")
        result = result[0][0]
        return result
    except IndexError:
        return "NONE"
    except Exception as e:
        print(Fore.RED + f"CRITICAL : FUNCTION 'get_current_covid_date' ERRORED WITH EXCEPTION {e}")

async def multipage_list(bot, ctx, embed: discord.Embed, items: list, per_page = 10):
    """Makes a multipage embed for a list of per_page amount of items
    Bot for wait_for
    ctx for sending
    embed for a base of what to send - description and title will be overwritten. the list will be in the description so anything will be overwritten
    items, list of items to show on the list
    """
    pages = []
    temp_items = []
    index = 0

    # make lists of items
    if not items:
        embed.title = "There are no results to show."
        await ctx.send(embed = embed)
    else:
        for item in items:
            if len(temp_items) >= per_page:
                pages.append(temp_items)
                temp_items = []
            temp_items.append(item)
        pages.append(temp_items)

        # make embed

        description = "```\n"
        for item in pages[index]:
            description += f"{repr(item)[1:-1]}\n"
        description += "```"
        embed.description = description
        embed.title = f"Showing {1 + (index * per_page)} to {(index * per_page) + (len(pages[index]))} of {len(items)} items\nPage {index + 1} of {len(pages)}"

        # send embed

        msg = await ctx.send(embed = embed)
        if not len(pages) == 1:
            reactions = ['\N{Leftwards Black Arrow}', '\N{Page Facing Up}', '\N{Black Rightwards Arrow}']
            for emoji in reactions:
                await msg.add_reaction(emoji)
            def check(reaction, user):
                if reaction.message.id == msg.id:
                    if reaction.emoji in reactions:
                        if user == ctx.author:
                            return True
            try:
                while True:
                    reaction, user = await bot.wait_for("reaction_add", check = check, timeout = 30)
                    if reaction.emoji == '\N{Leftwards Black Arrow}':
                        # left
                        await reaction.remove(user)

                        if index == 0:
                            index = len(pages) - 1
                        else:
                            index += -1

                        description = "```\n"
                        for item in pages[index]:
                            description += f"{repr(item)[1:-1]}\n"
                        description += "```"
                        embed.description = description
                        embed.title = f"Showing {1 + (index * per_page)} to {(index * per_page) + (len(pages[index]))} of {len(items)} items\nPage {index + 1} of {len(pages)}"

                        await msg.edit(embed = embed)
                    elif reaction.emoji == '\N{Black Rightwards Arrow}':
                        # right
                        await reaction.remove(user)

                        if index == len(pages) - 1:
                            index = 0
                        else:
                            index += 1

                        description = "```\n"
                        for item in pages[index]:
                            description += f"{repr(item)[1:-1]}\n"
                        description += "```"
                        embed.description = description
                        embed.title = f"Showing {1 + (index * per_page)} to {(index * per_page) + (len(pages[index]))} of {len(items)} items\nPage {index + 1} of {len(pages)}"

                        await msg.edit(embed = embed)
                    elif reaction.emoji == '\N{Page Facing Up}':
                        # choose page
                        await reaction.remove(user)

                        def mcheck(message):
                            if message.author == ctx.author:
                                return True

                        x = await ctx.send(f"What page do you want to skip to? A number between 1 and {len(pages)}")

                        message = await bot.wait_for("message", check = mcheck)

                        try:
                            new_page = int(message.content)
                        except:
                            try:
                                await x.delete()
                            except:
                                pass
                            await message.delete()
                            await ctx.send("That wasn't a number", delete_after = 10)
                        else:
                            try:
                                await message.delete()
                                await x.delete()
                            except:
                                pass
                            if new_page >= 1 and new_page <= len(pages):
                                index = int(message.content) - 1

                                description = "```\n"
                                for item in pages[index]:
                                    description += f"{repr(item)[1:-1]}\n"
                                description += "```"
                                embed.description = description
                                embed.title = f"Showing {1 + (index * per_page)} to {(index * per_page) + (len(pages[index]))} of {len(items)} items\nPage {index + 1} of {len(pages)}"

                                await msg.edit(embed = embed)
                            else:
                                x = await ctx.send(f"That wasn't between 1 and {len(pages)}", delete_after = 10)
            except asyncio.TimeoutError:
                try:
                    await msg.clear_reactions()
                except:
                    pass
#While this doesn't make use of the databases, it provides a very useful feature of splitting information into pages 



emojis = {
    "greentick":"✅",
    "redtick":"❌",
    "barrier":"🚫",
    "noentry":"⛔",
    "warning":"⚠️",
    "clown":"🤡",
    "?":"❓",
    "idle":"🌙",
    "0":"0️⃣",
    "1":"1️⃣",
    "2":"2️⃣",
    "3":"3️⃣",
    "4":"4️⃣",
    "5":"5️⃣",
    "6":"6️⃣",
    "7":"7️⃣",
    "8":"8️⃣",
    "9":"9️⃣",
    "A":"🇦",
    "B":"🇧",
    "C":"🇨",
    "D":"🇩",
    "E":"🇪",
    "F":"🇫",
    "G":"🇬",
    "H":"🇭",
    "I":"🇮",
    "J":"🇯",
    "K":"🇰",
    "L":"🇱",
    "M":"🇲",
    "N":"🇳",
    "O":"🇴",
    "P":"🇵",
    "Q":"🇶",
    "R":"🇷",
    "S":"🇸",
    "T":"🇹",
    "U":"🇺",
    "V":"🇻",
    "W":"🇼",
    "X":"🇽",
    "Y":"🇾",
    "Z":"🇿",
    "left_arrow":"⬅️",
    "right_arrow":"➡️",
    "up_arrow":"⬆️",
    "down_arrow":"⬇️",
    "curved_down_arrow":"⤵️",
    "trophy":"🏆",
    "mega":"📢",
    "clock":"🕐",
    "alarmclock":"⏰"
        }
        
#Dictionary of unicode emojis for easy access when imported into other files.

alphabet = {1:'a', 2:'b', 3:'c', 4:'d', 5:'e', 6:'f', 7:'g', 8:'h', 9:'i', 10:'j', 11:'k', 12:'l', 13:'m', 14:'n', 15:'o', 16:'p', 17:'q', 18:'r', 19:'s', 20:'t', 21:'u', 22:'v', 23:'w', 24:'x', 25:'y', 26:'z'} 

suggestion_messages = {}

availability_messages = {}

playing = {}

permissions = {
    "1":"Basic",
    "2":"Trusted",
    "3":"Mod",
    "4":"Administrator",
    "5":"Owner"
}
#Dictionary of permission level and names for easy access when imported into other files.