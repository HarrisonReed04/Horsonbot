import asyncio
from typing import Union
import aiomysql
from database import db_commit, db_select, determine_prefix, get_current_covid_date, emojis, alphabet
import discord
from discord.ext import commands, tasks
from datetime import datetime
from colorama import Fore, init
from requests import get
import matplotlib.pyplot as plt
import random

init()

class coronavirus(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        await self.covid_dates_init_check()
        

    def create_graph(self, data):
        def randstr(count):
            retr = ""
            for x in range(count):
                retr += alphabet[random.randint(1,26)]
            return retr
        instance = randstr(random.randint(10,15))

        data = data['data']

        casesthisweek = []
        caseslastweek = []
        dates = []

        for x in range(6,-1,-1):
            casesthisweek.append(data[x]['dailyCases'])

        for x in range(14,7,-1):
            caseslastweek.append(data[x]['dailyCases'])

        for x in range(0,7):
            dates.append(datetime.strptime(data[6-x]['date'],'%Y-%m-%d').strftime("%d/%m"))

        color = "red" if int(data[1]['dailyCases']) <= int(data[0]['dailyCases']) else "green" 
        plt.figure(facecolor="#2f3136")
        ax = plt.axes()
        ax.plot(dates, caseslastweek, color="white", label="Last Week Cases", alpha=0.5, linewidth=0.5)
        ax.plot(dates, casesthisweek, color=color, label="This Week Cases", linewidth=2.5)
        ax.set_facecolor("#2f3136")
        ax.yaxis.label.set_color('white')
        ax.xaxis.label.set_color('white')
        ax.spines['bottom'].set_color('white')
        ax.spines['top'].set_color('white')
        ax.spines['left'].set_color('white')
        ax.spines['right'].set_color('white')
        ax.tick_params(axis='x', colors='white')
        ax.tick_params(axis='y', colors='white')
        plt.ylabel("Cases")
        plt.margins(0.05)
        plt.xticks(rotation=90)
        plt.legend()
        plt.savefig(f"covidgraphs/{instance}")      
        return instance


    async def coronavirus_daily_update(self, channelid=None):
        url = 'https://api.coronavirus.data.gov.uk/v1/data?filters=areaType=overview&structure={"date":"date","dailyCases":"newCasesByPublishDate","cumulativeCases":"cumCasesByPublishDate","dailyDeaths":"newDeaths28DaysByPublishDate","cumulativeDeaths":"cumDeaths28DaysByPublishDate"}'
        data = await self.get_data(url)

        identifier = self.create_graph(data)

        file = discord.File(f"/mnt/networkdrive/bots/hbot/covidgraphs/{identifier}.png", filename=f"{identifier}.png")
        
        embed = discord.Embed(
            color = 0x00ff00,
            description = f"Horson Bot's daily covid update! - {datetime.now().strftime('%d-%m-%Y')}"
        )


        if not channelid:
            date = data['data'][0]['date']
            cases = data['data'][0]['dailyCases']
            cumcases = data['data'][0]['cumulativeCases']
            deaths = data['data'][0]['dailyDeaths']
            cumdeaths = data['data'][0]['cumulativeDeaths']
            await db_commit(f"""INSERT INTO `covid_logs`(`date`,`daily_cases`,`cumulative_cases`,`daily_deaths`,`cumulative_deaths`) VALUES (
                "{date}",     
                {cases},
                {cumcases},
                {deaths if deaths != "null" else 0},
                {cumdeaths if cumdeaths != "null" else 0}               
            )""")


        ######
        ######IF NEEDED TO DISABLE COVID ANNOUNCEMENTS UNCOMMENT HERE
        ######


        #print(Fore.CYAN + f"DAILY COVID UPDATES HAVE BEEN DISABLED")
        #channels = (await db_select(f"""SELECT `update_channel_snowflake_id` FROM `covid_guilds`"""))
        #embed=discord.Embed(title=f"Sorry, Daily COVID announcements are currently under maintenence.", description = "They should return soon...", color=0xff0000)
        #embed.set_footer(text="Blame Harrison...")
        #if channelid is not None and channelid != "all":
        #    try:
        #        channel = self.bot.get_channel(int(channelid))
        #    except:
        #        channel = self.bot.get_user(int(channelid))
        #    await channel.send(embed=embed)
        #    return
        #for channel in channels:
        #    channel = self.bot.get_channel(int(channel[0]))
        #    await channel.send(embed=embed)
        #users = (await db_select(f"""SELECT `user_snowflake_id` FROM `covid_users`"""))
        #for user in users:
        #    user = self.bot.get_user(int(user[0]))
        #    await user.send(embed=embed)


        if channelid == None:
            print(Fore.CYAN + f"INFO : COVID INFORMATION FOR " + Fore.YELLOW + f"{data['data'][0]['date']}" + Fore.CYAN + " HAS BEEN RELEASED AND ADDED TO THE DATABASE.")
        elif channelid == "all":
            print(Fore.MAGENTA + f"INFO : COVID ANNOUNCEMENT MANUALLY RELEASED ")
        else:
            channel = self.bot.get_channel(int(channelid))
            print(Fore.CYAN + f"INFO : COVID ANNOUNCEMENT REQUESTED IN " + Fore.RED + f"{channel.name}" + Fore.CYAN + " IN "  + Fore.RED + f"{channel.guild.name}")
        url = 'https://api.coronavirus.data.gov.uk/v1/data?filters=areaType=overview&structure={"date":"date","dailyCases":"newCasesByPublishDate","cumulativeCases":"cumCasesByPublishDate","dailyDeaths":"newDeaths28DaysByPublishDate","cumulativeDeaths":"cumDeaths28DaysByPublishDate"}'
        data = await self.get_data(url)
        embed = discord.Embed(
            color = 0xFDE5DA,
            title = f"""Horson Bot's daily covid update\n{f'`Today, {datetime.now().strftime("%d-%m-%Y")}`' if datetime.now().strftime('%d-%m-%Y') == data['data'][0]['date'] else f"Date: `{datetime.strptime(data['data'][0]['date'],'%Y-%m-%d').strftime('%d-%m-%Y')}`" }"""
        )

        embed.set_image(url=f"attachment://{identifier}.png")

        newcases, cumcases, newdeaths, cumdeaths = data['data'][0]['dailyCases'] , data['data'][0]['cumulativeCases'] , data['data'][0]['dailyDeaths'] , data['data'][0]['cumulativeDeaths']

        yesterdaycases, yesterdaydeaths = data['data'][1]['dailyCases'], data['data'][1]['dailyDeaths']
        
        casesdifference, deathsdifference = yesterdaycases-newcases , yesterdaydeaths-newdeaths
        
        yesterdaycasesdiff, yesterdaydeathsdiff = "{:,}".format(abs((data['data'])[1]['dailyCases']-(data['data'][0]['dailyCases']))),"{:,}".format(abs(data['data'][1]['dailyDeaths']-(data['data'][0]['dailyDeaths']))) 
        
        weekagocases, weekagodeaths = data['data'][6]['dailyCases'], data['data'][6]['dailyDeaths']
        
        weekcasesdifference, weekdeathsdifference = weekagocases-newcases , weekagodeaths-newdeaths
        
        weekcasesdiff, weekdeathsdiff = "{:,}".format(abs(int(data['data'][6]['dailyCases'])-int(data['data'][0]['dailyCases']))),"{:,}".format(abs(int(data['data'][6]['dailyDeaths'])-int(data['data'][0]['dailyDeaths']))) 
        
        
        embed.add_field(
            name = "Cases:",
            value = f"""\nNew cases today: `{"{:,}".format(newcases)}`\n
Compared to yesterday: `{('-' if casesdifference > 0 else '+')}{yesterdaycasesdiff}` `({"{:,}".format(yesterdaycases)})`
Compared to 7 days ago: `{('-' if weekcasesdifference > 0 else '+')}{weekcasesdiff}` `({"{:,}".format(weekagocases)})`\n
Cumulative cases in the UK: `{'{:,}'.format(cumcases)}`\n""",
            inline = False
        )
        embed.add_field(
            name = "Deaths:",
            value = f"""\nNew deaths today: `{"{:,}".format(newdeaths)}`\n
Compared to yesterday: `{("-" if deathsdifference > 0 else "+")}{yesterdaydeathsdiff}` `({"{:,}".format(yesterdaydeaths)})`
Compared to 7 days ago: `{('-' if weekdeathsdifference > 0 else '+')}{weekdeathsdiff}` `({"{:,}".format(weekagodeaths)})`\n
Cumulative deaths in the UK: `{'{:,}'.format(cumdeaths)}`"""
        )

        embed.set_footer(text="Covid updates are back! Also, a new command is going to be released soon with more in depth details that a daily announcement cant quite do. Keep your eyes peeled!")
        embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/854449129476063255/859423644341895178/COVID-19-iCON-scaled-removebg-preview.png")
        embed.set_image(url=f"attachment://{identifier}.png")
        if channelid is not None and channelid != "all":
            try:
                channel = self.bot.get_channel(int(channelid))
                if isinstance(channel, discord.TextChannel):
                    embed.description = f"Here is your daily covid update, in `{channel.name}, {channel.guild.name}`"
                    print(Fore.YELLOW + f"Coronavirus daily update sent to {channel.guild.name} - {channel.name}")
                else:
                    to_say = f"""Daily Coronavirus Update. New cases today are {newcases}... New deaths today are {newdeaths}""" 
                    await self.tts(channel, to_say)
                    return                    
            except:
                channel = self.bot.get_user(int(channelid))
                embed.description = f"Here is your daily covid update, `{channel.name}`"
                print(Fore.YELLOW + f"Coronavirus daily update sent to {channel.name}")
            if isinstance(channel, discord.TextChannel):
                await channel.send(embed=embed, file=file) 
            return

        channels = (await db_select(f"""SELECT `channel_snowflake_id` FROM `covid_text_channels`"""))
        for channel in channels:
            channel = self.bot.get_channel(int(channel[0]))
            embed.description = f"Here is your daily covid update, in `{channel.name}`"
            #await channel.send(embed=embed,file=file)
            #print(Fore.YELLOW + f"Coronavirus daily update sent to {channel.guild.name} - {channel.name}")
        users = (await db_select(f"""SELECT `user_snowflake_id` FROM `covid_users`"""))
        for user in users:
            user = self.bot.get_user(int(user[0]))
            embed.description = f"Hi, {user.name}! Here is your daily covid update!"
            #await user.send(embed=embed,file=file)
            #print(Fore.YELLOW + f"Coronavirus daily update sent to {user.name}")
    
    @tasks.loop(seconds=10)
    async def covid_date_check(self):
        url = 'https://api.coronavirus.data.gov.uk/v1/data?filters=areaType=overview&structure={%22date%22:%22date%22,%22cases%22:%22newCasesByPublishDate%22}'
        data = (await self.get_data(url))
        if data['data'][0]['date'] == (await get_current_covid_date()):
            pass
        else:
            print(Fore.YELLOW + f"The government have released their daily covid figures for " + Fore.BLUE + f"{datetime.now().strftime('%d-%m-%Y @ %H:%M.%S')}" + Fore.YELLOW + ". Releasing the daily update now")
            await self.coronavirus_daily_update()
    
    async def covid_dates_init_check(self):
        try:
            data = (await self.get_data('https://api.coronavirus.data.gov.uk/v1/data?filters=areaType=overview&structure={"date":"date","dailyCases":"newCasesByPublishDate","cumulativeCases":"cumCasesByPublishDate","dailyDeaths":"newDeaths28DaysByPublishDate","cumulativeDeaths":"cumDeaths28DaysByPublishDate"}'))
            print(Fore.YELLOW + "COVID Information has been located, adding any dates necessary now.")
            for x in range((int(data['length'])-1), -1, -1):
                if x == 0:
                    if not data['data'][x]['date'] == (await get_current_covid_date()):
                        await self.coronavirus_daily_update()
                try:
                    date = data['data'][x]['date']
                    try:
                        dates = (await db_select(f"""SELECT `date` FROM `covid_logs`"""))
                    except IndexError:
                        dates = []
                    if not date in dates:
                        cases = data['data'][x]['dailyCases']
                        cumcases = data['data'][x]['cumulativeCases']
                        deaths = data['data'][x]['dailyDeaths']
                        cumdeaths = data['data'][x]['cumulativeDeaths']
                        await db_commit(f"""INSERT INTO `covid_logs`(`date`,`daily_cases`,`cumulative_cases`,`daily_deaths`,`cumulative_deaths`) VALUES (
                            "{date}",     
                            {cases},
                            {cumcases},
                            {deaths if deaths != "null" else 0},
                            {cumdeaths if cumdeaths != "null" else 0}         
                        )""")
                        print(Fore.MAGENTA + f"Covid information for {data['data'][x]['date']} has been added to the logs.")
                except aiomysql.IntegrityError:
                    pass
                except aiomysql.InternalError:
                    pass
                except Exception as e:
                    print(f"{type(e)}, {e} @ {x} Len {len(data['data'][x]['date'])} Date {data['data'][x]['date']}")
        finally:
            await self.covid_date_check.start()

    @commands.group()
    async def covid(self, ctx):
        if ctx.invoked_subcommand == None:
            embed=discord.Embed(
                color = 0xff0000,
                title = "Nope"
            )
            await ctx.send(embed=embed)
    
    @covid.group(aliases=['announce'])
    async def announcement(self, ctx):
        if ctx.invoked_subcommand == None:
            embed = discord.Embed(
                color = 0xff0000,
                title = "Nope"
            )
            await ctx.send(embed=embed)

    @covid.command()
    async def test(self, ctx):
        if ctx.author.id == 546780798661951512:
            await ctx.reply(embed=discord.Embed(title="Covid test results", description="Nope, not covid. Gay though.", color=0xff0000))
        else:
            await ctx.reply(embed=discord.Embed(title="Covid test results", description="You have tested positive" if random.randint(0,1000) <= 200 else "You have tested negative.", color=0x00ff00))

    @announcement.command()
    async def release(self, ctx, channel):
        await self.coronavirus_daily_update(channel)

    @announcement.command()
    async def subscribe(self, ctx, channelid:Union[discord.TextChannel, discord.VoiceChannel]=None):
        try:
            if ctx.guild:
                if not ctx.author == ctx.guild.owner and ctx.author.id != 538838470727172117:
                    embed = discord.Embed(
                        color = 0xff0000,
                        title = f"{emojis['barrier']}You can't do that!",
                        description = f"You need to get {ctx.guild.owner.mention} to do that!"
                    )
                    await ctx.send(embed=embed)
                    return 
                def check(msg, author):
                    return msg.author == author
                if channelid is None:
                    await db_commit(f"""INSERT INTO `covid_text_channels`(`guild_name`,`guild_snowflake_id`,`channel_name`,`channel_snowflake_id`,`guild_owner_name`,`guild_owner_snowflake_id`,`date_subscribed`) VALUES (
                        "{ctx.guild.name}",
                        "{ctx.guild.id}",
                        "{ctx.channel.name}",
                        "{ctx.channel.id}",
                        "{ctx.guild.owner.name}",
                        "{ctx.guild.owner.id}",
                        "{datetime.now()}"
                    )""")
                    embed = discord.Embed(
                        color = 0x00ff00,
                        title = f"`{ctx.channel.guild.name} - {ctx.channel.name}` will now receieve daily covid updates!",
                        description = "And here comes the first update now!"
                    )
                    embed.set_footer(text=f"Unsubscribe with `{(await determine_prefix(self.bot, ctx.message))[0][0]}covid announcement unsubscribe`")
                    await ctx.send(embed=embed)
                    await self.coronavirus_daily_update(ctx.channel.id)
                else:
                    channel = self.bot.get_channel(channelid.id)
                    print(channel)
                    guild = channel.guild
                    if isinstance(channel, discord.TextChannel):
                        await db_commit(f"""INSERT INTO `covid_text_channels`(`guild_name`,`guild_snowflake_id`,`update_channel_name`,`update_channel_snowflake_id`,`guild_owner_name`,`guild_owner_snowflake_id`,`date_subscribed`) VALUES (
                            "{channel.guild.name}",
                            "{channel.guild.id}",
                            "{channel.name}",
                            "{channel.id}",
                            "{channel.guild.owner.name}",
                            "{channel.guild.owner.id}",
                            "{datetime.now()}"
                        )""")
                    elif isinstance(channel, discord.VoiceChannel):
                        await db_commit(f"""INSERT INTO `covid_voice_channels`(`guild_name`,`guild_snowflake_id`,`update_channel_name`,`update_channel_snowflake_id`,`guild_owner_name`,`guild_owner_snowflake_id`,`date_subscribed`) VALUES (
                            "{channel.guild.name}",
                            "{channel.guild.id}",
                            "{channel.name}",
                            "{channel.id}",
                            "{channel.guild.owner.name}",
                            "{channel.guild.owner.id}",
                            "{datetime.now()}"
                        )""")
                    embed = discord.Embed(
                        color = 0x00ff00,
                        title = f"`{channel.guild} - {channel.name}` will now receieve daily covid updates!",
                        description = "And here comes the first update now!"
                    )
                    embed.set_footer(text=f"Unsubscribe with `{(await determine_prefix(self.bot, ctx.message))[0][0]}covid announcement unsubscribe`")
                    await ctx.send(embed=embed)
                    await self.coronavirus_daily_update(channel.id)
                    print(Fore.CYAN + "INFO : " + Fore.RED + f"{channel.name}" + Fore.CYAN + f" HAS SUBSCRIBED TO DAILY CORONAVIRUS UPDATES. SUBSCRIBED BY " + Fore.CYAN + f"{ctx.author.name}")
            else:
                try:
                    await db_commit(f"""INSERT INTO `covid_users`(`user_name`,`user_snowflake_id`,`date_subscribed`) VALUES (
                        "{ctx.author}",
                        "{ctx.author.id}",
                        "{datetime.now()}"
                    )""")
                    embed = discord.Embed(
                        color = 0x00ff00,
                        title = f"`{ctx.author.name}`, you will now receieve daily covid updates in your DMs!"
                    )
                    print(Fore.CYAN + "INFO : " + Fore.RED + f"{ctx.author}" + Fore.CYAN + f" HAS SUBSCRIBED TO DAILY CORONAVIRUS UPDATES.")
                except aiomysql.IntegrityError:
                    embed = discord.Embed(
                        color = 0xff0000,
                        title = f"{ctx.author.name}, you are already subscribed to covid announcements!"
                    )
                embed.set_footer(text=f"Unsubscribe with `{(await determine_prefix(self.bot, ctx.message))[0][0]}covid announcement unsubscribe`")
                await ctx.message.reply(embed=embed)
        except aiomysql.IntegrityError:
            channel = self.bot.get_channel(channelid)
            embed=discord.Embed(color=0xff0000,title=f"{channel.name} is already subscribed to covid announcements.!", description=f"Unsubscribe at any time with {(await determine_prefix(self.bot,ctx.message))[0]}covid announcement unsubscribe")
            await ctx.reply(embed=embed)

    async def get_data(self, url):
        response = get(url=url)
        if response.status_code not in [200, 204]:
            print(Fore.RED + f"CRITICAL : COULD NOT CONNECT TO " + Fore.CYAN + f"{url}" + Fore.RED + f", ERROR STATUS CODE: " + Fore.CYAN + f"{response.status_code} " + Fore.RED + "WITH TEXT: " + Fore.CYAN + f"{response.text}", Fore.YELLOW + "\nWaiting 1 Second before attempting again")
            await asyncio.sleep(1)
            await self.get_data(url)
        else:
            return (response.json())

    @announcement.command()
    async def unsubscribe(self, ctx, channelid:float=None):
        pass
        
    @commands.command()
    async def add_dates(self, ctx):
        data = (await self.get_data('https://api.coronavirus.data.gov.uk/v1/data?filters=areaType=overview&structure={"date":"date","dailyCases":"newCasesByPublishDate","cumulativeCases":"cumCasesByPublishDate","dailyDeaths":"newDeaths28DaysByPublishDate","cumulativeDeaths":"cumDeaths28DaysByPublishDate"}'))
        for x in range((int(data['length'])-1), -1, -1):
            try:
                date = data['data'][x]['date']
                try:
                    dates = (await db_select(f"""SELECT `date` FROM `covid_logs`"""))
                    print(dates)
                except IndexError:
                    dates = []
                if not date in dates:
                    cases = data['data'][x]['dailyCases']
                    cumcases = data['data'][x]['cumulativeCases']
                    deaths = data['data'][x]['dailyDeaths']
                    cumdeaths = data['data'][x]['cumulativeDeaths']
                    await db_commit(f"""INSERT INTO `covid_logs`(`date`,`daily_cases`,`cumulative_cases`,`daily_deaths`,`cumulative_deaths`) VALUES (
                        "{date}",     
                        {cases},
                        {cumcases},
                        {deaths if deaths != "null" else 0},
                        {cumdeaths if cumdeaths != "null" else 0}         
                    )""")
                    print(Fore.MAGENTA + f"Covid information for {data['data'][x]['date']} has been added to the logs.")
            except aiomysql.IntegrityError:
                pass
            except aiomysql.InternalError:
                pass
            except Exception as e:
                print(f"{type(e)}, {e} @ {x} Len {len(data['data'][x]['date'])} Date {data['data'][x]['date']}")



    @commands.command()
    #@commands.max_concurrency(1, commands.BucketType.default, wait=True)
    async def thenewandimprovedcovidcommandthathasbeenindevelopmentforquiteawhilenow(self, ctx):
        data = (await self.get_data("https://api.coronavirus.data.gov.uk/v1/data"))
        page1 = discord.Embed(title="Coronavirus Cases Information:", description=f"Today, {datetime.strptime(data['data'][0]['date'], '%Y-%m-%d').strftime('%d-%m-%Y')}" if data['data'][0]['date'] == datetime.now().strftime("%Y-%m-%d") else f"{data['data'][0]['date']}", color=0x7289DA)
        page1.add_field(name="Daily Covid Cases:", value=f"`{data['data'][0]['casesDaily']}`")
        page1.add_field(name="Cumulative Cases", value=f"`{data['data'][0]['casesCumulative']}`")
        await ctx.send(embed=page1)

def setup(bot):
    bot.add_cog(coronavirus(bot))
    