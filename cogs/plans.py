import asyncio
import discord
from discord.ext import commands
from database import emojis, determine_prefix, alphabet
from database import suggestion_messages
import typing
from random import randint

class plans(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.group(aliases=['suggestion'])
    async def suggest(self, ctx):
        if ctx.invoked_subcommand == None:
            embed=discord.Embed(title="You didn't invoke a subcommand.",description=f"Looking to start a new suggestion? Use \n{await determine_prefix(self.bot, ctx.message)}{ctx.command.name} new `topic` `:` `suggestion(s)`\nLooking to add to a suggestion? Use \n{await determine_prefix(self.bot, ctx.message)}{ctx.command.name} add `message_id` `suggestion(s)`", color=0x00ffff)
            embed.set_footer(text="Separate suggestions with `/`")
            await ctx.send(embed=embed)

    @suggest.command()
    async def new(self ,ctx, *, suggestion):
        identifier = f"{alphabet[randint(1,26)]}{alphabet[randint(1,26)]}{alphabet[randint(1,26)]}{alphabet[randint(1,26)]}"
        temp = suggestion.partition(":")
        topic = temp[0].lstrip().rstrip()
        if temp[1] == "":
            suggestion = None
        else:
            suggestion = temp[2] if temp[2] != "" else None
        embed=discord.Embed(title=f"{ctx.author.display_name} wants suggestions. - Identifier {identifier}", description=f"Topic: `{topic.capitalize()}`", color=0x00ffff)
        embed.set_footer(text=f"Use this command to add a suggestion: \n{await determine_prefix(self.bot, ctx.message)}suggestion add {identifier} `your suggestion`")
        if suggestion == None:
            msg = await ctx.send(embed=embed)
        else:
            temp = suggestion.split("/")
            for x in temp:
                await ctx.send(f"`{x}`")
                if not x.isspace() and x != '': embed.add_field(name=f"{emojis[f'{len(embed.fields)+1}']} > `{x.lstrip().rstrip()}`", value=f"Suggested by {ctx.author.display_name}", inline=False)
            msg = await ctx.send(embed=embed)
        suggestion_messages[f'{identifier}'] = msg.id
        for x in range(1, len(embed.fields)+1):
            await msg.add_reaction(emojis[f'{x}'])
        await asyncio.sleep(86400)
        try:
            suggestion_messages.pop(f"{identifier}")
        except:
            pass

    @suggest.command()
    async def add(self, ctx, identifier: typing.Union[int, str], * ,suggestion):
        if isinstance(identifier, int):
            try:
                msg = await ctx.fetch_message(identifier)
            except discord.NotFound:
                await ctx.send(embed=discord.Embed(title="I couldn't find that suggestions message, was it deleted or did you use the wrong ID?", color=0x00ffff))
                return
            suggestions = suggestion.split("/")
            embed = msg.embeds[0]
            embed_fields = len(embed.fields)
            for suggestion2 in suggestions:
                if suggestion2 != "" and not suggestion2.isspace() and len(embed.fields) < 20: embed.add_field(name=f"{emojis[f'{len(embed.fields)+1}']} > `{suggestion2.lstrip().rstrip()}`", value=f"Suggested by {ctx.author.display_name}", inline=False)
            await msg.edit(embed=embed)
            for x in range(embed_fields+1, embed_fields+1+len(suggestions)):
                await msg.add_reaction(emojis[f'{x}'])
        else:
            try:
                msg_id = suggestion_messages[f'{identifier}']
                try:
                    msg = await ctx.fetch_message(msg_id)
                    suggestions = suggestion.split("/")
                    embed = msg.embeds[0]
                    embed_fields = len(embed.fields)
                    for suggestion2 in suggestions:
                        if suggestion2 != "" and not suggestion2.isspace() and len(embed.fields) < 20: embed.add_field(name=f"{emojis[f'{len(embed.fields)+1}']} > `{suggestion2.lstrip().rstrip()}`", value=f"Suggested by {ctx.author.display_name}", inline=False)
                    await msg.edit(embed=embed)
                    for x in range(embed_fields+1, embed_fields+1+len(suggestions)):
                        await msg.add_reaction(emojis[f'{x}'])
                except discord.NotFound:
                    await ctx.send(embed=discord.Embed(title="I couldn't find that suggestions message, was it deleted?", color=0x00ffff))
                    try:
                        suggestion_messages.pop(f'{identifier}')
                    except:
                        pass
                    return
            except:
                await ctx.send(embed=discord.Embed(title="I couldn't find that suggestions identifier, Did you spell it right?", color=0x00ffff))
                return

    @suggest.command()
    async def remove(self, ctx, identifier: typing.Union[int, str], index:int):
        if isinstance(identifier, int):
            try:
                msg = await ctx.fetch_message(identifier)
                if ctx.author != msg.author and ctx.author.id != 538838470727172117:
                    await ctx.send(embed=discord.Embed(title="You are not the owner of that suggestions message.", color=0x00ffff))
                    return
            except discord.NotFound:
                await ctx.send(embed=discord.Embed(title="I couldn't find that suggestions message, was it deleted or did you use the wrong ID?", color=0x00ffff))
                return
            embed = msg.embeds[0].to_dict()
            embed['fields'].pop(index-1)
            try:
                await msg.clear_reaction(emojis[f'{index}'])
            except:
                pass
            embed = discord.Embed.from_dict(embed)
            await msg.edit(embed=embed)
        else:
            try:
                msg_id = suggestion_messages[f'{identifier}']
                try:
                    msg = await ctx.fetch_message(msg_id)
                    if ctx.author != msg.author and ctx.author.id != 538838470727172117:
                        await ctx.send(embed=discord.Embed(title="You are not the owner of that suggestions message.", color=0x00ffff))
                        return
                    embed = msg.embeds[0].to_dict()
                    embed['fields'].pop(index-1)
                    try:
                        await msg.clear_reaction(emojis[f'{index}'])
                    except:
                        pass
                    embed = discord.Embed.from_dict(embed)
                    await msg.edit(embed=embed)
                except discord.NotFound:
                    await ctx.send(embed=discord.Embed(title="I couldn't find that suggestions message, although the identifier was right. Was the suggestions message deleted?", color=0x00ffff))
                    try:
                        suggestion_messages.pop(f'{identifier}')
                    except:
                        pass
                    return
            except:
                await ctx.send(embed=discord.Embed(title="I couldn't find that suggestions identifier, Did you spell it right?", color=0x00ffff))
                return        

    @commands.command()
    async def wasd(self, ctx):
        await ctx.send(suggestion_messages)
        
    @commands.command()
    async def plans_append(self, ctx, ref, id:int):
        suggestion_messages[f'{ref}'] = id

def setup(bot):
    bot.add_cog(plans(bot))