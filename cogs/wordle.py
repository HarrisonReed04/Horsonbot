import asyncio
import discord
from discord.ext import commands, tasks
from database import emojis, db_commit, db_select, completed_wordle
from datetime import datetime, timedelta
from wordles import options

class wordle(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.users_completed = []
        self.word = None

    @tasks.loop(seconds=1)
    async def new_word(self):
        if datetime.now().strftime("%H:%M:%S") == "00:00:00":
            self.word = await self.new_wordle()
            completed_wordle.clear()
            INJOY = await self.bot.get_channel(674024871579353112)
            await INJOY.send("New wordle out guys!")
        else:
            pass

    async def new_wordle(self):
        try:
            q = (await db_select(f"""SELECT `log_id` FROM wordle WHERE `date` = "{(datetime.now()-timedelta(days=1)).strftime("%d-%m-%Y")}";"""))[0][0]
            x = int(q)
            today = options[x]
        except IndexError:
            today = options[0]
        await db_commit(f"""INSERT INTO wordle(`date`,`word`) VALUES(
            "{datetime.now().strftime("%d-%m-%Y")}",
            "{today}"
        )""")

    @commands.group()
    @commands.dm_only()
    async def wordle(self, ctx):
        try:
            self.word = (await db_select(f"""SELECT `word` FROM `wordle` WHERE `date` = "{datetime.now().strftime("%d-%m-%Y")}";"""))[0][0]
        except IndexError:
            self.word = await self.new_wordle()

        if ctx.author.id in completed_wordle:
            embed=discord.Embed(title="Come back tomorrow for a new word!", color=0xf0a3d4)
            embed.set_footer(text="Once a day buddy!")
            await ctx.send(embed=embed)
            return
        temp_cs = ""

        board = [
        f"{emojis['blacksquare'] * 5}",
        f"{emojis['blacksquare'] * 5}",
        f"{emojis['blacksquare'] * 5}",
        f"{emojis['blacksquare'] * 5}",
        f"{emojis['blacksquare'] * 5}",
        f"{emojis['blacksquare'] * 5}"
        ]

        def board_str(b,gn):
            temp = ""
            for y,x in enumerate(b):
                if y == gn:
                    temp+=x
                    temp+=emojis['left_arrow']
                    temp+="\n"
                else:
                    temp+=x
                    temp+="\n"
            return temp

        def board_win_str(b,gs):
            temp = ""
            for x in range(0,gs+1):
                temp+= b[x]
                temp+="\n"
            return temp

        def board_lose_str(b):
            temp = ""
            for x in b[:-1]:
                temp += x
                temp += "\n"
            temp+=x 
            temp+=emojis['redtick']
            return temp
        def checkmsg(m):
            return m.channel.type == discord.ChannelType.private and m.author == ctx.author

        if ctx.invoked_subcommand == None:
            guessed = False
            guessno = 0
            embed=discord.Embed(title="Welcome to Wordle, where you have a new word to figure out every day!", description="Green means that letter is in the CORRECT position\nYellow means that letter is in the word, in the wrong position\nBlank means that letter is not in the word!", color=0xf0a30d)
            embed.set_footer(text="I am now defaulting to listen to answers from you in this DM. You do not need to use a command to make a guess. To quit at any time, type `quit`")
            embed.add_field(name="The board:", value=f"{board_str(board, guessno)}")
            msg = await ctx.send(embed=embed)
            while guessed == False and guessno < 6:
                correct_format = False
                while not correct_format:
                    guess = None
                    try:
                        guess = (await self.bot.wait_for('message', check=checkmsg, timeout=120))
                        content = guess.content.lower()
                    except asyncio.TimeoutError:
                        await ctx.reply("Timed out.")
                        return
                    if content == "quit":
                        await guess.reply("Okay, quitting. You will need to use the prefix to talk to me from now!")
                        return
                    if not content.isalpha():
                        await guess.reply("Letters only.")
                    elif len(content) > 5:
                        await guess.reply("Too many letters.")
                    elif len(content) < 5:
                        await guess.reply("Not enough letters.")
                    else:
                        correct_format = True

                for x,y in enumerate(content):
                    if y==self.word[x]:
                        temp_cs += f"{emojis['greensquare']}"
                    elif y!=self.word[x] and y in self.word:
                        temp_cs += f"{emojis['yellowsquare']}"
                    elif y not in self.word:
                        temp_cs += f"{emojis['blacksquare']}"
                board[guessno] = temp_cs
                temp_cs = ""
                

                embed.set_field_at(0, name="The board:", value=f"{board_str(board, guessno)}")

                if board[guessno] == f"{emojis['greensquare'] * 5}":
                    print("win")
                    guessed = True
                else:
                    guessno += 1
                    embed.set_field_at(0, name="The board:", value=f"{board_str(board, guessno)}")
                await msg.edit(embed=embed)
            if guessed == True:
                embed=discord.Embed(title="Congrats! You got the wordle", description=f"It took you {guessno+1} attempts!", color=0x00ff00)
                embed.add_field(name="The board:", value=f"{board_win_str(board, guessno)}")
                embed.set_footer(text="Come back tomorrow for a new word!")
                await ctx.send(embed=embed)
            elif guessno > 5:
                embed=discord.Embed(title="Unfortunately, you didn't get the wordle today!", description=f"The word was {self.word}", color=0xff0000)
                embed.add_field(name="The board:", value=f"{board_lose_str(board)}")
                embed.set_footer(text="Hey, there's always tomorrow instead!")
                await ctx.send(embed=embed)
            completed_wordle.append(ctx.author.id)
            return
        else:
            pass

    @wordle.command()
    async def remove(self, ctx):
        try:
            await completed_wordle.remove(ctx.author.id)
        except:
            pass

    @commands.Cog.listener()
    async def on_ready(self):
        try:
            self.word = (await db_select(f"""SELECT `word` FROM `wordle` WHERE `date` = "{datetime.now().strftime("%d-%m-%Y")}";"""))[0][0]
        except IndexError:
            self.word = await self.new_wordle()
        
        await asyncio.sleep(60-datetime.now().second)
        await self.new_word.start()

def setup(bot):
    bot.add_cog(wordle(bot))

