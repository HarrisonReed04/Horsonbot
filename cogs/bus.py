import asyncio
from typing import Union

import requests
import aiomysql
from database import db_commit, db_select, determine_prefix, get_current_covid_date, emojis
import discord
from discord.ext import commands, tasks
from datetime import datetime
from colorama import Fore, init
from requests import get

class bus(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.baseurl = "http://harrisonreed.tech/api/v1/findbus?"
        self.routes = ["1","2","3","4","5","5a","6","7","8","9","11","12","16","17","18","U1A","U1E","U1C","U2B","U2C","U6C","U6H","U9"]
        self.directions = {
        "1":"Inbound: Towards Southampton\nOutbound: Towards Winchester",
        "2":"Inbound: Towards Southampton\nOutbound: Towards Eastleigh",
        "3":"Inbound: Towards Southampton\nOutbound: Towards Eastleigh",
        "4":"Inbound: Towards Southampton\nOutbound: Towards Romsey",
        "5":"Inbound: Towards Boyatt Wood\nOutbound: Towards Romsey",
        "5a":"Inbound: Towards Boyatt Wood\nOutbound: Towards Romsey",
        "6":"Inbound: Towards Southampton\nOutbound: Towards Lymington",
        "7":"Inbound: Towards Lordshill\nOutbound: Towards Sholing",
        "8":"Inbound: Towards Southampton\nOutbound: Towards Calshot",
        "9":"Inbound: Towards Southampton\nOutbound: Towards Fawley/Langely",
        "11":"Inbound: Towards Southampton\nOutbound: Towards West Totton",
        "12":"Inbound: Towards Southampton\nOutbound: Towards Calmore",
        "16":"Inbound: Towards Southampton\nOutbound: Towards Townhill Park",
        "17":"Inbound: Towards Weston\nOutbound: Towards Adanac Park",
        "18":"Inbound: Towards Millbrook\nOutbound: Towards Thornhill",
        "U1A":"Outbound: Towards Airport Parkway",
        "U1E":"Outbound: Towards Eastleigh",
        "U1C":"Inbound: Towards Southampton",
        "U2B":"Outbound: Towards Glen Eyre Halls",
        "U2C":"Inbound: Towards Southampton",
        "U6C":"Inbound: Towards Southampton",
        "U6H":"Outbound: Towards General Hospital",
        "U9":"Inbound: Towards Townhill Park\nOutbound: Towards General Hospital"}
        self.running = {}

    @commands.command()
    async def travel(self, ctx, route):
        def reset_user(usr_id):
            self.running[str(usr_id)] = {}
        route = route.upper()
        reset_user(ctx.author.id)
        if not route in self.routes:
            embed = discord.Embed(title="That is not one of the routes that I have here... Please try a different one.", colour=0xff0000)
            await ctx.send(embed=embed); return
        embed = discord.Embed(title="Which direction do you want to travel?", description=f"The options I have for your route are:\n{self.directions[route]}", color=0x0f0f0f)
        direction_msg = await ctx.send(embed=embed)
        if "Inbound" in self.directions[route]:
            await direction_msg.add_reaction(emojis["I"])
        if "Outbound" in self.directions[route]:
            await direction_msg.add_reaction(emojis["O"])
        def check(reaction, user):
            return user == ctx.author and str(reaction.emoji) in [emojis["I"], emojis["O"]]
        try:
            direction, user = await self.bot.wait_for("reaction_add", check=check, timeout=30)
        except asyncio.TimeoutError:
            reset_user(ctx.author.id)
            embed = discord.Embed(title=f"Timed out, Cancelling {emojis['redtick']}", color=0xff0000)
            await direction_msg.edit(embed=embed); return
        else:
            if str(direction.emoji) == emojis["O"]:
                direction = "Outbound"
            elif str(direction.emoji) == emojis["I"]:
                direction = "Inbound"
            else:
                await ctx.send(embed=discord.Embed(title="Caught a pretty big problem error here, can't be having that tbh.", color=0xff0f0f))
                reset_user(ctx.author.id); return
            self.running[str(ctx.author.id)]["Direction"] = direction


        embed=discord.Embed(title="Great, What stop do you want to start from?", color=0xf0ff0f)
        startmsg = await ctx.send(embed=embed)

        def msgcheck(m):
            return m.author == ctx.author and m.channel == ctx.channel

        try:
            user_start_message = await self.bot.wait_for("message", check=msgcheck, timeout=30)
        except asyncio.TimeoutError:
            embed = discord.Embed(title="Timed out, cancelling...", color=0xff0000)
            await startmsg.edit(embed=embed); return
        else:
            start = user_start_message.content
            self.running[str(ctx.author.id)]["start"] = start

        embed=discord.Embed(title="Okay, What stop do you want to stop at?", color=0xf0ff0f)
        stopmsg = await ctx.send(embed=embed)

        try:
            user_stop_message = await self.bot.wait_for("message", check=msgcheck, timeout=30)
        except asyncio.TimeoutError:
            embed = discord.Embed(title="Timed out, cancelling...", color=0xff0000)
            await stopmsg.edit(embed=embed); return
        else:
            stop = user_stop_message.content
            self.running[str(ctx.author.id)]["stop"] = stop

        embed = discord.Embed(title="Do you want busses from now, or at a different time / date", description = f"{emojis['alarmclock']} - Different Time\n{emojis['clock']} - Different Date\n{emojis['greentick']} - Now", color=0xff00ff)
        timings_msg = await ctx.send(embed=embed)

        def choice_check(reaction, user):
            print(user, str(reaction.emoji))
            return user == ctx.author and str(reaction.emoji) in [emojis['alarmclock'],emojis['clock'],emojis['greentick']]
        try:
            reaction, user = await self.bot.wait_for("reaction_add", check=choice_check, timeout=30)
        except asyncio.TimeoutError:
            embed = discord.Embed(title="Timed out, cancelling.", color=0xff0000)
            await timings_msg.edit(embed=embed); return
        else:
            print("here")
            if str(reaction.emoji) == emojis["greentick"]:
                self.running[str(ctx.author.id)]['day'] = "today"
                self.running[str(ctx.author.id)]['after'] = "now"

        usrdict = self.running[str(ctx.author.id)]
        print(usrdict)
        url = self.baseurl + f"start={usrdict.get('start').replace(' ', '%20')}&stop={usrdict.get('stop').replace(' ', '%20')}&after={usrdict.get('after')}&day={usrdict.get('day')}"
        print(url)
        data = await self.get_data(url)

        await ctx.send(data)

    async def get_data(self, url):
        response = requests.get(url=url, timeout=10)
        print(response.json())
        return response.json()



def setup(bot):
    bot.add_cog(bus(bot))
