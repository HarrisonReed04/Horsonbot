from database import utc_to_locat
from discord.ext import commands
import discord
from datetime import datetime, timedelta
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
def setup(bot):
    bot.add_cog(spotify(bot))