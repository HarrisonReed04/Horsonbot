from json.decoder import JSONDecodeError
from database import emojis
from discord.ext import commands
import discord
from discord import Spotify
from datetime import datetime, timedelta
from pathlib import Path
import pathlib
import json
import os
import uuid
class spotify(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    async def remove_microseconds(self, ms):
        return ms - timedelta(microseconds=ms.microseconds)

    @commands.group(invoke_without_command=True)
    async def spotify(self, ctx, user:discord.Member=None):
        if ctx.invoked_subcommand == None:
            user = user or ctx.author
            for activity in user.activities:
                if isinstance(activity, discord.Spotify):
                    embed=discord.Embed(title=f"{user.display_name} is currently vibing to:", color=0xf0ff0f)
                    embed.add_field(name="Song:", value=f"`{activity.title}`", inline=False)
                    embed.add_field(name="Artist:" if len(activity.artists) == 1 else "Artists:", value=f"`{', '.join(artist for artist in activity.artists)}`", inline=False)
                    embed.add_field(name="Album:", value=f"`{activity.album}`", inline=False)
                    embed.set_image(url=activity.album_cover_url)
                    embed.add_field(name="Started at:", value=f"`{(await utc_to_locat(activity.start)).strftime('%H:%M:%S')}`", inline=True)
                    embed.add_field(name="Duration:", value=f"`{await self.remove_microseconds(activity.duration)}`", inline=True)
                    embed.add_field(name="Time remaining", value=f"`{await self.remove_microseconds((await utc_to_locat(activity.end)) - (await utc_to_locat(datetime.now())))}`")
                    await ctx.send(embed=embed)
                    return
            await ctx.send(embed=discord.Embed(title=f"{user.display_name} is not currently vibing on spotify!", color=0xf0ff0f))
        
    @spotify.command()
    async def link(self, ctx, user:discord.Member=None):
        user = user or ctx.author
        for activity in user.activities:
            if isinstance(activity, discord.Spotify):
                embed=discord.Embed(colour=0xf0fff0)
                embed.set_author(url=f"https://open.spotify.com/track/{activity.track_id}", name="Click me to take you to spotify!")
                embed.set_thumbnail(url=activity.album_cover_url)
                embed.add_field(name="Song:", value=f"`{activity.title}`", inline=False)
                embed.add_field(name="Artist:" if len(activity.artists) == 1 else "Artists:", value=f"`{', '.join(artist for artist in activity.artists)}`", inline=False)
                embed.add_field(name="Album:", value=f"`{activity.album}`", inline=False)
                embed.add_field(name="Duration:", value=f"`{await self.remove_microseconds(activity.duration)}`", inline=False)
                await ctx.send(embed=embed)
                return
        await ctx.send(embed=discord.Embed(title=f"{user.display_name} isn't currently vibing on spotify.", color=0xf0ff0f))

    @spotify.command()
    async def small(self, ctx, user:discord.Member=None):
        user = user or ctx.author
        for activity in user.activities:
            if isinstance(activity, discord.Spotify):
                embed=discord.Embed(title=f"{user.display_name} is currently vibing to:", color=0xf0ff0f)
                embed.add_field(name="Song:", value=f"`{activity.title}`", inline=False)
                embed.add_field(name="Artist:" if len(activity.artists) == 1 else "Artists:", value=f"`{', '.join(artist for artist in activity.artists)}`", inline=False)
                embed.add_field(name="Album:", value=f"`{activity.album}`", inline=False)
                embed.set_thumbnail(url=activity.album_cover_url)
                embed.add_field(name="Started at:", value=f"`{(await utc_to_locat(activity.start)).strftime('%H:%M:%S')}`", inline=True)
                embed.add_field(name="Duration:", value=f"`{await self.remove_microseconds(activity.duration)}`", inline=True)
                embed.add_field(name="Time remaining", value=f"`{await self.remove_microseconds((await utc_to_locat(activity.end)) - (await utc_to_locat(datetime.now())))}`")
                await ctx.send(embed=embed)
                return
        await ctx.send(embed=discord.Embed(title=f"{user.display_name} is not currently vibing on spotify!", color=0xf0ff0f))


    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        prev, now = None, None
        for activity in before.activities:
            if isinstance(activity, Spotify):
                prev = activity
                break
                
        for activity in after.activities:
            if isinstance(activity, Spotify):
                now = activity
                break

        if now == None:
            print("Return")
            return

        x = {}

        for attr in list(reversed(dir(now))):
            if str(attr) in ["album", "artists", "title", "track_id"]:
                x[str(attr)] = getattr(now, attr)


        track_id = x["track_id"]
                
        path = pathlib.Path(__file__).parent.resolve()
        path = path.parents[0]
        file = f"{path}/spotify/{after.guild.id}-spotify.json"



        if not Path(file).is_file():
            with open(file, 'x') as f:
                guild_file = {}
                print(f"Created {file}")

        else:
            with open(file, 'rt') as f:
                try:
                    guild_file = json.load(f)
                except JSONDecodeError:
                    guild_file = {}

        #guild_file[track_id] = {"info":x, "users":y, "total_plays":z}

        if guild_file != {}:

            try:
                guild_file[track_id]
                plays = int(guild_file[track_id]['plays']) + 1
                guild_file[track_id]['plays'] = plays
                guild_has_played = True

            except KeyError:
                guild_has_played = False

            if guild_has_played:
                try:
                    print("0")
                    user_plays = int(guild_file[track_id]['users'][str(after.id)]['total_plays']) + 1
                    print("1")
                    guild_file[track_id]['users'][str(after.id)]['total_plays'] = user_plays
                    print("2")
                    user_has_played = True

                except KeyError as e:
                    print(e)
                    user_has_played = False

            if guild_has_played == False:
                guild_file[track_id] = {"info":x,"users":{after.id:{"total_plays":1, "last_play":f"{datetime.now().strftime('%m')}/{datetime.now().strftime('%Y')}"}},"plays":1}
            elif user_has_played == False:
                guild_file[track_id] = {"info":x,"users":{after.id:{"total_plays":1, "last_play":f"{datetime.now().strftime('%m')}/{datetime.now().strftime('%Y')}"}},"plays":plays}


        else:
            guild_file[track_id] = {"info":x,"users":{after.id:{"total_plays":1, "last_play":f"{datetime.now().strftime('%m')}/{datetime.now().strftime('%Y')}"}},"plays":1}
            print("Inserted new track details")

            print(guild_file)

        with open(file, "w") as q:
            json.dump(guild_file,q,indent=4)

    @spotify.command()
    async def top_song(self, ctx, user:discord.Member=None):
        user = ctx.author
        await ctx.send(embed=discord.Embed(title="Havent coded that yet"))

        path = pathlib.Path(__file__).parent.resolve()
        path = path.parents[0]
        file = f"{path}/spotify/{ctx.guild.id}-spotify.json"

        with open(file, 'rt') as f:
            try:
                guild_file = json.load(f)
            except JSONDecodeError:
                await ctx.send(embed=discord.Embed(title="no song yet"))   
                print("brok")  
                return

        highest = {}
        highest_total_plays = 0

        for key in guild_file:
            if guild_file[key]['plays'] > highest_total_plays:
                highest = guild_file[key]['info']
                highest_total_plays = guild_file[key]['plays']
                print(highest)
        
        embed=discord.Embed(title=f"Top song in {ctx.guild.name}", description=f"{highest}")
        await ctx.send(embed=embed)

            





def setup(bot):
    bot.add_cog(spotify(bot))