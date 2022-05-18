from json.decoder import JSONDecodeError

from discord import guild
from database import emojis, utc_to_locat, last_songs
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
    async def big(self, ctx, user:discord.Member=None):
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
    async def small(self, ctx, user:discord.Member=None):
        await ctx.invoke(self.bot.get_command('spotify'), user=user)

    @commands.command()
    async def show_last_songs(self, ctx, user:discord.Member=None):
        user = user or ctx.author
        await ctx.send(last_songs[user.id])

    @commands.Cog.listener()
    async def on_member_update(self, before, after):

        prev = None

        for activity in before.activities:
            if isinstance(activity, Spotify):
                prev = activity
                break

        now = None
                
        for activity in after.activities:
            if isinstance(activity, Spotify):
                now = activity
                break


        if now == None:
            return

        x = {}

        for attr in list(reversed(dir(now))):
            if str(attr) in ["album", "artists", "title", "track_id", "album_cover_url", "start"]:
                if str(attr) == "start":
                    x[str(attr)] = str(await utc_to_locat(getattr(now, attr)))
                else:
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


        if guild_file != {}:

            try:
                guild_file[track_id]
                plays = int(guild_file[track_id]['plays']) + 1
                guild_file[track_id]['plays'] = plays
                if plays == 100:
                    #embed=discord.Embed(title="Wow, 100 total plays!", description=f"Between everyone here in {after.guild.name}, you have listened to {x['title']} 100 times on spotify!", color=0xff00ff)
                    #embed.add_field()
                    pass
                guild_has_played = True

            except KeyError:
                guild_has_played = False

            if guild_has_played:
                try:
                    try:
                        if last_songs[after.id]['id'] == now.track_id and after.guild.id in last_songs[after.id]['guilds']:
                            return

                    except KeyError:
                        pass

                    user_plays = int(guild_file[track_id]['users'][str(after.id)]['total_plays']) + 1

                    guild_file[track_id]['users'][str(after.id)]['total_plays'] = user_plays

                    user_has_played = True

                except KeyError as e:

                    user_has_played = False

            if guild_has_played == False:
                guild_file[track_id] = {"info":x,"users":{after.id:{"total_plays":1, "last_play":f"{now.start}"}},"plays":1}

            elif user_has_played == False:
                y= guild_file[track_id]['users']
                y[after.id] = {"total_plays":1, "last_play":f"{now.start}"}
                guild_file[track_id] = {"info":x,"users":y,"plays":plays}



        else:

            guild_file[track_id] = {"info":x,"users":{after.id:{"total_plays":1, "last_play":f"{now.start}"}},"plays":1}
 
        try:
            guilds_done = last_songs[after.id]['guilds']
        except:
            guilds_done = []
            
        guilds_done.append(after.guild.id)
        last_songs[after.id] = {"track_id":now.track_id,"guilds":guilds_done}

        with open(file, "w") as q:
            json.dump(guild_file,q,indent=4)

    @commands.command()
    async def listeners(self, ctx):
        await ctx.send(last_songs)

    @spotify.group(invoke_without_subcommand=True)
    async def top(self, ctx, user:discord.Member=None):
        
        path = (pathlib.Path(__file__).parent.resolve()).parents[0]

        file = f"{path}/spotify/{ctx.guild.id}-spotify.json"

        with open(file, 'rt') as f:
            try:
                guild_file = json.load(f)
            except JSONDecodeError:
                await ctx.send(embed=discord.Embed(title="no song yet"))   
                print("brok")  
                return

        highest = {}
        second_highest = {}
        highest_total_plays = 0
        second_highest_plays = 0
        highest_total_different_user_plays = 0

        for key in guild_file:
            if guild_file[key]['plays'] > highest_total_plays:
                second_highest = highest
                second_highest_plays = highest_total_plays
                highest = guild_file[key]['info']
                highest_total_plays = guild_file[key]['plays']
                highest_total_different_user_plays = len(guild_file[key]['users'])

        
        highest_user_plays_id = 0
        highest_user_plays_total = 0

        highest_key = highest['track_id']

        
        for yousir in guild_file[highest_key]['users']:

            if guild_file[highest_key]['users'][yousir]['total_plays'] > highest_user_plays_total:
                highest_user_plays_total = guild_file[highest_key]['users'][yousir]['total_plays']
                highest_user_plays_id = int(yousir)


        

        embed = discord.Embed(title=f"The top song here in {ctx.guild.name}", colour=0xff00ff)
        embed.add_field(name=f"`{highest['title']}`", value=f"""By `{", ".join(artist for artist in highest['artists'])}`\nFrom the album: `{highest['album']}`\nWith a whopping `{highest_total_plays}` total plays\nFrom a total of `{highest_total_different_user_plays}` different listeners!""", inline = False)
        member = await ctx.guild.fetch_member(highest_user_plays_id)
        embed.add_field(name=f"User `{member.display_name}` has the most listens with {highest_user_plays_total}",value=f"\nThey last played the song: `{datetime.strptime((guild_file[highest_key]['users'][str(highest_user_plays_id)]['last_play']), '%Y-%m-%d %H:%M:%S.%f').strftime('%d-%m-%Y @ %H:%M.%S')}`", inline=False)
        embed.set_thumbnail(url=guild_file[highest_key]['info']['album_cover_url'])
        await ctx.send(embed=embed)
            


def setup(bot):
    bot.add_cog(spotify(bot))