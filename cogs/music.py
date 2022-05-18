import asyncio

import attr
from database import emojis, playing
import discord
from discord.ext import commands, tasks
import datetime as datetime2
import os
import random
from ffmpeg import FFmpegPCMAudio
import urllib.request
import re
import urllib
import json
from pytube import YouTube
import youtube_dl

class music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    async def get_title(self, id):
        params = {"format":"json","url":"https://www.youtube.com/watch?v=%s" % id}
        url = "https://www.youtube.com/oembed"
        querystring = urllib.parse.urlencode(params)
        url = url + "?" + querystring
        with urllib.request.urlopen(url) as response:
            response_text = response.read()
            data=json.loads(response_text.decode())
            return(data['title'])

    @commands.command(aliases=['join'])
    async def connect(self, ctx):
        if ctx.guild.voice_client is not None:
            if ctx.author != ctx.guild.owner and ctx.author.id != 538838470727172117:
                await ctx.send(embed=discord.Embed(title="The bot is already in a voice channel in this server...", description="An admin can override this though.", color=0xff0000))
                return
            else:
                server = ctx.guild.voice_client
                await server.disconnect()
        await ctx.author.voice.channel.connect()
            
    @commands.command(aliases=['dc'])
    async def disconnect(self, ctx):
        print(ctx.author.voice.channel.id)
        print(self.bot.voice_clients)
        if ctx.author.voice.channel == self.bot.voice.channel:
            vc = ctx.guild.voice_client
            await vc.disconnect()
        else:
            await ctx.send(embed=discord.Embed(title="You are not in the same channel as the bot so you can't kick it.", description="An admin can override this though.",color=0xff0000))

    @commands.command()
    async def play(self, ctx, *, search:str):
        try:
            re.match(r"https://www.youtube.com/watch\?v=(\S{11})", search)
            yt = YouTube(search)
            try:
                filename = yt.streams.filter(only_audio=True).first().download(output_path="cogs/youtube",filename=f"'{yt.title.replace('/', '')}_{random.randint(0,100000)}'.mp3")
                vc = await ctx.author.voice.channel.connect()
                file = FFmpegPCMAudio(filename)
                vc.play(file)
                vc.source = discord.PCMVolumeTransformer(vc.source)
                vc.source.volume = 1
                while vc.is_playing():
                    await asyncio.sleep(0.1)
                await vc.disconnect()
                try:
                    os.remove(filename)
                except FileNotFoundError:
                    pass
            except Exception as e:
                print(e)
        except:
            loading = self.bot.get_emoji(882039644345212948)
            msg = await ctx.send(embed=discord.Embed(title=f"Searching {loading}", description="This shouldn't take too long.", color=0xff00ff))
            search = search.replace(' ', '%20')
            html = urllib.request.urlopen("https://www.youtube.com/results?search_query=" + search)
            embed=discord.Embed(title="Select the file", description=f'If your desired search doesn\'t appear, use £play `full video URL`', color=0x00ffff)
            video_ids = re.findall(r"watch\?v=(\S{11})", html.read().decode())
            titles = [await self.get_title(x) for x in video_ids]
            tx = 0
            for count,title in enumerate(titles[:5]):
                newline = "\n"
                yt = YouTube(f"https://www.youtube.com/watch?v=" + video_ids[count])
                print(yt.views)
                if tx == 0:
                    for attributes in dir(yt):
                        print(attributes)
                        
                    tx+=1
                views = "{:,}".format(yt.views)
                embed.add_field(name=f"{emojis[f'{count+1}']} > {title}", value=f"""Duration: `{str(datetime2.timedelta(seconds=yt.length))}`\n{f'Rating: `{round(yt.rating, 2)} {"⭐" * (int(round(yt.rating)))}`' if yt.rating else f'View count: `{views}`'}""", inline=False)
            await msg.edit(embed=embed)
            for x in ['1','2','3','4','5']:
                await msg.add_reaction(emojis[x])
            def check(reaction, user):
                return reaction.emoji in [emojis['1'],emojis['2'],emojis['3'],emojis['4'],emojis['5'],emojis['right_arrow']] and user == ctx.author
            try:
                reaction, user = await self.bot.wait_for('reaction_add', check=check, timeout=60)
            except asyncio.TimeoutError:
                await msg.edit(embed=discord.Embed(title="You didn't react fast enough, try that again", color=0xff0000))
                try:
                    await msg.clear_reactions()
                    return
                except:
                    return
            emoji = next((name for name, emoji in emojis.items() if emoji == reaction.emoji), None)
            if emoji == "right_arrow":
                #embed = discord.Embed(title="Select the file - Page 2", description="If your desired search doesn't appear, use £play `full video URL`", color=0x00ffff)
                await msg.edit(embed=discord.Embed(title="I haven't actually coded this yet...", description = "Give me a few days", color=0xffffff))
                return
            elif emoji == "1":
                search = "https://www.youtube.com/watch\?v=" + video_ids[0]
                await msg.edit(embed=discord.Embed(title=f"Okay, downloading `{titles[0]}` now, and I will automatically connect.",color=0xf0f0f0))
            elif emoji == "2":
                search = "https://www.youtube.com/watch\?v=" + video_ids[1]
                await msg.edit(embed=discord.Embed(title=f"Okay, downloading `{titles[1]}` now, and I will automatically connect.",color=0xf0f0f0))
            elif emoji == "3":
                search = "https://www.youtube.com/watch\?v=" + video_ids[2]
                await msg.edit(embed=discord.Embed(title=f"Okay, downloading `{titles[2]}` now, and I will automatically connect.",color=0xf0f0f0))
            elif emoji == "4":
                search = "https://www.youtube.com/watch\?v=" + video_ids[3]
                await msg.edit(embed=discord.Embed(title=f"Okay, downloading `{titles[3]}` now, and I will automatically connect.",color=0xf0f0f0))
            elif emoji == "5":
                search = "https://www.youtube.com/watch\?v=" + video_ids[4]
                await msg.edit(embed=discord.Embed(title=f"Okay, downloading `{titles[4]}` now, and I will automatically connect.",color=0xf0f0f0))
            try:
                await msg.clear_reactions()
            except: pass
            yt = YouTube(search)
            print(yt)
            try:
                try:
                    filename = yt.streams.filter(only_audio=True).first().download(output_path="cogs/youtube",filename=f"{yt.title}_{random.randint(0,100000)}.mp3")
                except Exception as e:
                    print(e)
                vc = await ctx.author.voice.channel.connect()
                file = FFmpegPCMAudio(filename)
                vc.play(file)
                vc.source = discord.PCMVolumeTransformer(vc.source)
                vc.source.volume = 1
                playing[ctx.channel.id] = {"title":{title[int(emoji)-1]}, "link":f"https://youtube.com/watch?v={video_ids[int(emoji)-1]}", "id":video_ids[int(emoji)-1]}
                while vc.is_playing():
                    await asyncio.sleep(0.1)
                await vc.disconnect()
                try:
                    os.remove(filename)
                except FileNotFoundError:
                    pass
                try:
                    playing.pop(ctx.channel.id)
                except:
                    pass
            except Exception as e:
                print(e)                
            #stream.download()

    @commands.command()
    async def playing_now(self, ctx):
        embed = discord.Embed(title=f"Currently playing in `{ctx.author.voice.channel.name}`", description=f"`{playing[ctx.author.voice.channel.id]['title']}`")
        await ctx.send(f"{playing[ctx.author.voice.channel.id]['title']}")





def setup(bot):
    bot.add_cog(music(bot))