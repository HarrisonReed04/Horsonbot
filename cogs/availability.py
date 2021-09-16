import asyncio
import discord
from discord.ext import commands
from database import emojis, alphabet, availability_messages
from random import randint  
import typing
from datetime import datetime
class availability(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.group(aliases=['available', 'whoissavailable', 'whoisfree', 'free', "who'sfree","check"], invoke_without_command=True)
    async def availability_check(self, ctx, *, when):
        loading = self.bot.get_emoji(882039644345212948)
        identifier = f"{alphabet[randint(1,26)]}{alphabet[randint(1,26)]}{alphabet[randint(1,26)]}{alphabet[randint(1,26)]}"
        embed=discord.Embed(title=f"Availability Checker - Reference `{identifier}`", description=f"When: `{when.capitalize()}`", color=0x00ffff)

        for member in ctx.channel.members:
            embed.add_field(name=f"{member} - {loading}", value=f"Pending Response",inline=False) if member.bot == False else 0

        msg = await ctx.send(embed=embed)
        availability_messages[f'{identifier}'] = msg.id

        for reaction in [emojis['greentick'],emojis['?'],emojis['redtick'],emojis['clock'],emojis['alarmclock']]:
            await msg.add_reaction(reaction)

        await asyncio.sleep(86400)
        
        try:
            availability_messages.pop(f"{identifier}")
        except:
            pass

    @commands.command()
    async def poiut(self, ctx):
        await ctx.send(availability_messages)

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        def check(message):
            try:
                datetime.strptime(message.content, '%H:%M')
                return message.author == user and isinstance(message.channel, discord.abc.PrivateChannel) 
            except:pass
        if not payload.message_id in availability_messages.values(): return
        if payload.user_id == self.bot.user.id: return
        if str(payload.emoji) not in [emojis['greentick'],emojis['?'],emojis['redtick'],emojis['clock'], emojis['alarmclock']]: return
        def find(lst, key, value):
            for i, dic in enumerate(lst):
                if value == (dic[key].split())[0]:
                    return i
            return None
        channel = await self.bot.fetch_channel(payload.channel_id)
        message = await channel.fetch_message(payload.message_id)
        user = await channel.guild.fetch_member(payload.user_id)
        if str(payload.emoji) == str(emojis['clock']):
            msg = await user.send(embed=discord.Embed(title="What time are you free FROM?",description="Reply to this message in 24hour format. For example\n16:20", color=0x00ffff))
            try:
                usrinput = await self.bot.wait_for('message', check=check, timeout=60)
                await msg.edit(embed=discord.Embed(title=f"Great, I've noted that you are free FROM {datetime.strptime(usrinput.content,'%H:%M').strptime('%H:%M')}.", color=0xf0fff0))
            except asyncio.TimeoutError:
                await msg.edit(embed=discord.Embed(title="You didn't reply in time.", color=0xff0000))
                return
        if str(payload.emoji) == str(emojis['alarmclock']):
            msg = await user.send(embed=discord.Embed(title="What time are you free UNTIL?", description="Reply to this message in 24hour format. For example\n16:20", color=0x00ffff))
            try:
                usrinput = await self.bot.wait_for('message', check=check, timeout=60)
                await msg.edit(embed=discord.Embed(title=f"Great, I've noted that you are free UNTIL {datetime.strptime(usrinput.content,'%H:%M').strftime('%H:%M')}.", color=0xf0fff0))
            except asyncio.TimeoutError:
                await msg.edit(embed=discord.Embed(title="You didn't reply in time.", color=0xff0000))
                return
        embed = message.embeds[0]
        embedx = embed.to_dict()
        if find(embed.to_dict()['fields'],"name",f"{user}") == None:
            embed.add_field(name =f"Available" if str(payload.emoji) == emojis['greentick'] else "Unsure" if str(payload.emoji) == emojis['?'] else f"Available from `{datetime.strptime(usrinput.content,'%H:%M').strftime('%H:%M')}`" if str(payload.emoji) == emojis['clock'] else "Unavailable" if str(payload.emoji) == emojis['redtick'] else f"Available until `{datetime.strptime(usrinput.content,'%H:%M').strftime('%H:%M')}`" if str(payload.emoji) == emojis['alarmclock'] else "Somehow you've messed up properly",inline=False)    
        else:
            index = find(embed.to_dict()['fields'], "name", f"{user}")  
            name = f"{user} - {emojis['alarmclock']}" if " until " in embedx['fields'][index]['value'] and str(payload.emoji) in [emojis['clock'], emojis['alarmclock']] else f"{user} - {payload.emoji}"      
        if "Available from" in embedx['fields'][index]['value'] and str(payload.emoji) == emojis['alarmclock']:
            if " until " not in embedx['fields'][index]['value']:
                await self.edit_embed(message.id, channel, index,name=name,value=f"{embedx['fields'][index]['value']} until `{datetime.strptime(usrinput.content,'%H:%M').strftime('%H:%M')}`",inline=False)
            else:
                await self.edit_embed(message.id, channel, index,name=name,value=f"{(' '.join((embedx['fields'][index]['value'].split(' '))[:-2]))} until `{datetime.strptime(usrinput.content,'%H:%M').strftime('%H:%M')}`",inline=False)      
        elif " until " in embedx['fields'][index]['value'] and str(payload.emoji) == emojis['clock']:
            if "Available from" not in embed['fields'][index]['value']:
                await self.edit_embed(message.id, channel, index,name=name,value=f"Available from `{datetime.strptime(usrinput.content,'%H:%M').strftime('%H:%M')}` {embedx['fields'][index]['value'][10:]}",inline=False)
            else:
                await self.edit_embed(message.id, channel, index,name=name,value=f"Available from `{datetime.strptime(usrinput.content,'%H:%M').strftime('%H:%M')}` {' '.join((embedx['fields'][index]['value'].split(' '))[3:])}",inline=False)
        else:
            await self.edit_embed(msgid=message.id, channel=channel, index=index,name=name,value=f"Available" if str(payload.emoji) == emojis['greentick'] else "Unsure" if str(payload.emoji) == emojis['?'] else f"Available from `{datetime.strptime(usrinput.content,'%H:%M').strftime('%H:%M')}`" if str(payload.emoji) == emojis['clock'] else "Unavailable" if str(payload.emoji) == emojis['redtick'] else f"Available until `{datetime.strptime(usrinput.content,'%H:%M').strftime('%H:%M')}`" if str(payload.emoji) == emojis['alarmclock'] else "Somehow you've messed up properly",inline=False) 
        try:
            await message.remove_reaction(payload.emoji, user)
        except:
            pass
        
    async def edit_embed(self, msgid, channel, index, name, value, inline):
        msg = await channel.fetch_message(msgid)
        embed = msg.embeds[0]
        embed.set_field_at(index=index,name=name,value=value,inline=inline)
        await msg.edit(embed=embed)

    @commands.command()
    async def append(self, ctx, ref, id:int):
        availability_messages[f'{ref}'] = id

    @availability_check.command()
    async def remove_user(self, ctx, ref: typing.Union[int, str], index: typing.Union[discord.Member, int]):
        if isinstance(ref, int):
            msg = await ctx.channel.fetch_message(ref)
        else:
            try:
                msg = await ctx.channel.fetch_message(availability_messages[ref])
            except:
                await ctx.send("nope")
        embed = msg.embeds[0].to_dict()
        if isinstance(index, discord.Member):
            def find(lst, key, value):
                for i, dic in enumerate(lst):
                    if value == (dic[key].split())[0]:
                        return i
            index = find(embed['fields'], "name", f"{index}")
            embed = discord.Embed.from_dict(embed)
            embed.remove_field(index)
        else:
            embed=discord.Embed.from_dict(embed)
            embed.remove_field(index+1)
        await msg.edit(embed=embed)

    @availability_check.command()
    async def resend(self, ctx, ref: str):
        try:
            msg = await ctx.channel.fetch_message(availability_messages[ref])
        except:
            await ctx.send("nope")
            return
        embed=msg.embeds[0]
        msg = await ctx.send(embed=embed)
        for reaction in [emojis['greentick'],emojis['?'],emojis['redtick']]:
            await msg.add_reaction(reaction)  
        availability_messages[f'{ref}']=msg.id
        await asyncio.sleep(86400)
        try:
            availability_messages.pop(f"{ref}")
        except:
            pass

    @availability_check.command()
    async def reset(self, ctx, ref: typing.Union[int, str], index: discord.Member):
        member = index
        loading = self.bot.get_emoji(882039644345212948)
        if isinstance(ref, int):
            try:
                msg = await ctx.channel.fetch_message(ref)
            except:
                await ctx.send("nope")
                return
        else:
            try:
                msg = await ctx.channel.fetch_message(availability_messages[ref])
            except:
                await ctx.send("nope")
        embed = msg.embeds[0].to_dict()
        if isinstance(index, discord.Member):
            def find(lst, key, value):
                for i, dic in enumerate(lst):
                    if value == (dic[key].split())[0]:
                        return i
            index = find(embed['fields'], "name", f"{index}")


            embed = discord.Embed.from_dict(embed)


        embed.set_field_at(index, name=f"{member} - {loading}", value=f"Pending Response",inline=False)
        await msg.edit(embed=embed)



def setup(bot):
    bot.add_cog(availability(bot))