import discord
from discord.ext import commands
import traceback
import sys
from database import emojis

class error_handler(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        """The event triggered when an error is raised while invoking a command.
        Parameters
        ------------
        ctx: commands.Context
            The context used for command invocation.
        error: commands.CommandError
            The Exception raised.
        """

        # This prevents any commands with local handlers being handled here in on_command_error.
        if hasattr(ctx.command, 'on_error'):
            return

        # This prevents any cogs with an overwritten cog_command_error being handled here.
        cog = ctx.cog
        if cog:
            if cog._get_overridden_method(cog.cog_command_error) is not None:
                return

        ignored = (commands.CommandNotFound, commands.CheckFailure)

        # Allows us to check for original exceptions raised and sent to CommandInvokeError.
        # If nothing is found. We keep the exception passed to on_command_error.
        error = getattr(error, 'original', error)

        # Anything in ignored will return and prevent anything happening.
        if isinstance(error, ignored):
            return

        if isinstance(error, commands.DisabledCommand):
            await ctx.send(f'{ctx.command} has been disabled.')

        elif isinstance(error, commands.NoPrivateMessage):
            embed = discord.Embed(
                title=f"{emojis['barrier']} That command cannot be used in DMs!",
                color = 0xff0000
            )
            embed.set_footer(text="Try using that command in a server!", icon_url=ctx.author.avatar_url)
            try:
                await ctx.author.send(embed=embed)
            except discord.HTTPException:
                pass

        elif isinstance(error, commands.PrivateMessageOnly):
            embed = discord.Embed(
                title=f"{emojis['barrier']} That command can only be used in DMs!",
                color = 0xff0000
            )
            embed.set_footer(text="Try using that command in our DM's!", icon_url=ctx.author.avatar_url)
            try:
                await ctx.author.send(embed=embed)
            except discord.HTTPException:
                pass

        elif isinstance(error, commands.MissingRequiredArgument):
            embed = discord.Embed(
                title=f"{emojis['warning']} Woah, you missed an argument there buddy!",
                color = 0xff0000
            )
            embed.set_footer(text="Try that one again!", icon_url=ctx.author.avatar_url)
            await ctx.reply(embed=embed)

        elif isinstance(error, commands.MaxConcurrencyReached):
            embed = discord.Embed(
                title = f"{emojis['warning']}`{ctx.command.qualified.name}` is already being used right now! Wait a few moments and try again.{emojis['barrier']}",
                color = 0xff0000
            )
            await ctx.reply(embed=embed)

        else:
            # All other Errors not returned come here. And we can just print the default TraceBack.
            print('Ignoring exception in command {}:'.format(ctx.command), file=sys.stderr)
            traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)
            #print(error)

def setup(bot):
    bot.add_cog(error_handler(bot))