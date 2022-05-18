import asyncio
from multiprocessing.dummy import current_process
import os
from unicodedata import name 
import discord
from discord.ext import commands, tasks
from matplotlib.pyplot import title 
from database import emojis
from datetime import datetime
from colorama import Fore, init
from requests import get
import random
import math
from wordlist import words
init()

class hm(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.hmgames = {}

    global hangman_games
    hangman_games = {}

    @tasks.loop(seconds=5)
    async def hmclear(self):
        try:
            for key in self.hmgames:
                if (datetime.now() - self.hmgames[key]['lastinvolvement']).seconds >= 300:
                    channel = self.bot.get_channel(int(key))
                    await channel.send(embed=discord.Embed(name="Your hangman expired :(", description="**Hangman Expired**\nYou didn't interact for over 5 minutes, so I have deleted the game.", color=0xff0000))
                    del self.hmgames[key]
                    print(Fore.YELLOW + f"| HANGMAN INFO | GAME EXPIRED | Game in `{channel.name}`, `{channel.guild.name}` expired.")
        except RuntimeError:
            pass

    @commands.group(aliases=['hm'])
    async def hangman(self, ctx):
        if ctx.invoked_subcommand == None:
            await ctx.send(embed=discord.Embed(title="Thats not quite right. Use the `£help hangman` command for more info.",color=0xff0000))

    @commands.command()
    async def hm_games_ls(self, ctx):
        await ctx.send(self.hmgames)

    @hangman.command()
    async def start(self, ctx, xtype:str="user"):

        if str(ctx.channel.id) in list(self.hmgames):
            await ctx.send(embed=discord.Embed(title="There is already a hangman game taking place in this server!", color=0xfa3a64))
            return

        if xtype != "user":
            await ctx.send(embed=discord.Embed(title="I assume you meant to play against the computer."))
            player = "computer"
        else:
            player = "user"

        def checkmsg(m):
            return m.channel.type == discord.ChannelType.private and m.author == ctx.author
        def checkreact(r, u):
            if u == ctx.author and str(r.emoji in [emojis['greentick'],emojis['redtick']]):
                return str(r.emoji)
            else:
                return False

        if player != "computer":

            phrase = None
            while not phrase:
                try:
                    msg1 = await ctx.author.send(embed=discord.Embed(title="Please type what you want the channel members to guess!"))
                    msg2 = await ctx.message.reply(embed=discord.Embed(title="Check your DM's!", color=0xf454a1))
                    temp_phrase = await self.bot.wait_for('message', check=checkmsg, timeout=30)
                except discord.Forbidden:
                    await ctx.reply("You don't allow me to message you!")
                    return
                except asyncio.TimeoutError: 
                    await msg2.edit(embed=discord.Embed(title="I messaged you but you didn't respond quick enough!", color=0xff0000))
                    await msg1.edit(embed=discord.Embed(title="Timed Out."))
                    return
                if temp_phrase:
                    wordphrase = "word" if len(temp_phrase.content.split(" ")) == 1 else "phrase"
                    confirm = await ctx.author.send(embed=discord.Embed(title=f"Is this the {wordphrase} you want to be guessed?", description=f"{temp_phrase.content}", color=0xf0ad35))
                    for reaction in [emojis['greentick'], emojis['redtick']]:
                        await confirm.add_reaction(reaction)
                    reaction, user = await self.bot.wait_for('reaction_add', check=checkreact, timeout=30)
                    if str(reaction.emoji) == emojis['greentick']:
                        phrase=temp_phrase.content.lower()
                        current = ""
                        for x in phrase:
                            current += "-" if x != " " else " "
        else:
            x = random.randint(1,1169)
            phrase = words[x].lower()
            current = ""
            for y in phrase:
                current += "-" if y != " " else " "


        gameint = len(self.hmgames) + 1
        author = ctx.author.id if xtype == "user" else "computer"
        self.hmgames[f'{ctx.channel.id}'] = {"gameid":f"{gameint}", "phrase": f"{phrase}", "guesses":[], "stage":0,"current":f"{current}", "starttime":datetime.now(), "lastinvolvement":datetime.now(), "authorid":f"{author}"}
        await ctx.send(embed=discord.Embed(title="We're ready to start!"))
        self.hmgames[f'{ctx.channel.id}']['gameboard'] = discord.Embed(title="Game board", description=f"Here you can see guessed letters")
        self.hmgames[f'{ctx.channel.id}']['gameboard'].add_field(name=f"The word you're looking for!", value=f"{current}")
        await ctx.send(embed=self.hmgames[f'{ctx.channel.id}']['gameboard'])

    @commands.command()
    async def guess(self, ctx, *, guess:str=None):

        accepted_chars = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z', 'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', '1', '2', '3', '4', '5', '6', '7', '8', '9', ' ']


        for char in guess:
            if char not in accepted_chars:
                await ctx.reply(embed=discord.Embed(title="Incorrect guess format. Only numbers, letters or spaces please!"))
                return

        guess = guess.lower()

        PATH = "/mnt/networkdrive/bots/hbot"
        try:
            phrase = self.hmgames[f'{ctx.channel.id}']['phrase']
            current = list(self.hmgames[f'{ctx.channel.id}']['current'])
        except KeyError:
            await ctx.send(embed=discord.Embed(title="No current hangman game going! Start one now!", color=0xfa424d))
            return

        self.hmgames[f'{ctx.channel.id}']['lastinvolvement'] = datetime.now()

        if ctx.author == self.hmgames[f'{ctx.channel.id}']['authorid']:
            await ctx.send(embed=discord.Embed(title="Can't let you cheat!", description="Let your peers guess, not you!", color=0xff0000))
            return

        if len(guess) > len(phrase):
            await ctx.send(embed=discord.Embed(title="Your guess is too many letters!", description="Try using less letters", color=0xff0000))
            return

        if guess in self.hmgames[f'{ctx.channel.id}']['guesses']:
            already_guessed=discord.Embed(title="That has already been guessed!", description=f"{''.join(current)}", color=0xff0000)
            File = discord.File(f"{PATH}/cogs/stages/stage{self.hmgames[f'{ctx.channel.id}']['stage']}.png", filename="hangman.png")
            already_guessed.set_image(url=f"attachment://stage{self.hmgames[f'{ctx.channel.id}']['stage']}.png")
            await ctx.send(embed=already_guessed, file=File)
            return
        else:
            if self.hmgames[f'{ctx.channel.id}']['stage'] != 8:
                self.hmgames[f'{ctx.channel.id}']['guesses'].append(guess) 

        win = False
        def wincheck(cur, stg, d):
            if stg > 7:
                return "los"
            if stg <= 7 and "-" in cur and d == 1:
                return "int,l" if len(self.hmgames[f'{ctx.channel.id}']['phrase']) != 1 else "int,w"
            if stg <= 7 and "-" in cur and d > 1:
                return "int,w"
            if stg <= 7 and "-" not in cur:
                return "win"
            

        if len(guess) == 1:
            guess_type = "letter"
        else:
            guess_type = "word"

        if self.hmgames[f'{ctx.channel.id}']['stage'] == 8:
            if len(guess) != len(self.hmgames[f'{ctx.channel.id}']['phrase']):
                await ctx.reply("You're on your final guess, you need to guess the word now!")
                return

        if guess_type == "letter":

            if guess not in phrase:
                pass

            for pos, let in enumerate(phrase):
                if guess == let: 
                    current[pos] = let

        elif guess_type == "word":

            if guess == phrase:
                win, res = True, "win"

        current = "".join(current)
        self.hmgames[f'{ctx.channel.id}']['current'] = current



        if not win:
            res = wincheck(current, self.hmgames[f'{ctx.channel.id}']['stage'], len(guess))

        if res == "win":
            timetaken = (datetime.now() - self.hmgames[f'{ctx.channel.id}']['starttime']).seconds
            m, s = divmod(timetaken, 60)
            newline = "\n"
            embed=discord.Embed(title="Winner!", description=f"You guessed it with {self.hmgames[f'{ctx.channel.id}']['stage']} wrong guess(es)!{newline}You took {m} minute(s) and {s} second(s)", color=0xff0000)
            File = discord.File(f"{PATH}/cogs/stages/stage{self.hmgames[f'{ctx.channel.id}']['stage']}win.png", filename="hangman.png")
            embed.add_field(name="What you were guessing", value=f"{phrase}")
            embed.set_image(url=f"attachment://stage{self.hmgames[f'{ctx.channel.id}']['stage']}.png")

            print(Fore.CYAN + f"| GAMES INFO | Hangman Finished in a WIN in {ctx.channel.id} | The word was {self.hmgames[f'{ctx.channel.id}']['phrase']} by {self.hmgames[f'{ctx.channel.id}']['authorid']}")


        elif res == "int,w":
            embed=discord.Embed(title=f"`{guess}` is not the answer!", description=f"{current}", color=0x0f0f0f)
            self.hmgames[f'{ctx.channel.id}']['stage'] += 1 if guess != phrase else 0
            File = discord.File(f"{PATH}/cogs/stages/stage{self.hmgames[f'{ctx.channel.id}']['stage']}.png", filename="hangman.png")
            embed.set_image(url=f"attachment://{self.hmgames[f'{ctx.channel.id}']['stage']}.png")

        elif res == "int,l":
            embed=discord.Embed(title=f"`{guess}` is {'not in' if guess not in phrase else 'in'} the answer!", description=f"{current}", color=0x0f0f0f)
            self.hmgames[f'{ctx.channel.id}']['stage'] += 1 if guess not in phrase else 0
            File = discord.File(f"{PATH}/cogs/stages/stage{self.hmgames[f'{ctx.channel.id}']['stage']}.png", filename="hangman.png")
            embed.set_image(url=f"attachment://{self.hmgames[f'{ctx.channel.id}']['stage']}.png")


        elif res == "los":
            self.hmgames[f'{ctx.channel.id}']['stage'] += 1
            embed=discord.Embed(title=f"You Lose! The word you were guessing was", description=f"`{phrase}`", color=0xff0000)
            File = discord.File(f"{PATH}/cogs/stages/stage{self.hmgames[f'{ctx.channel.id}']['stage']}.png", filename="hangman.png")
            embed.set_image(url=f"attachment://{self.hmgames[f'{ctx.channel.id}']['stage']}.png")

            print(Fore.MAGENTA + f"| GAMES INFO | Hangman Finished in a LOSS in {ctx.channel.id} | The word was '{self.hmgames[f'{ctx.channel.id}']['phrase']}' by {self.hmgames[f'{ctx.channel.id}']['authorid']}")


        if len(self.hmgames[f'{ctx.channel.id}']['guesses']) > 0:
            newline = "\n"
            embed.add_field(name="Your guesses", value=f"""{f'{newline}'.join(x for x in self.hmgames[f'{ctx.channel.id}']['guesses'])}""", inline=False)

        await ctx.send(embed=embed, file=File)

        if res == "los" or res == "win":
            del self.hmgames[f'{ctx.channel.id}']

    @commands.Cog.listener()
    async def on_ready(self):
        if datetime.now().second > 0:
            await asyncio.sleep(60-datetime.now().second)
        try:
            print(Fore.MAGENTA + "| HANGMAN CLEAR LOOP STARTING |")
            await self.hmclear.start()
        except Exception as e:
            print(e)


def setup(bot):
    bot.add_cog(hm(bot))