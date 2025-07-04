from discord.ext import commands
from spotipy.exceptions import SpotifyException
from utils.util import print_centered, send_log_message


class Events(commands.Cog):
    def __init__(self, lumea):
        self.lumea = lumea


    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await send_log_message(self, ctx, f"[!] Missing command params for {ctx.command.name}: {error.param.name}")
            
        elif isinstance(error, commands.MissingPermissions):
            perms = ', '.join(error.missing_perms)
            await send_log_message(self, ctx, f"[!] Missing permissions to do that!")

        elif isinstance(error, commands.BotMissingPermissions):
            perms = ', '.join(error.missing_perms)
            await send_log_message(self, ctx, f"[!] Missing permissions to do that!")

        elif isinstance(error, SpotifyException):
            if error.http_status == 403 and "premium" in str(error).lower():
                await send_log_message(self, ctx, "[!] This command requires Spotify Premium!")
            

    @commands.Cog.listener()
    async def on_command(self, ctx):
        if ctx.author.id != self.lumea.user.id:
            return
        
        await ctx.message.delete()
        print_centered(f"[?] Command ran: `{ctx.command.name}`")


    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.id != self.lumea.user.id:
            return

        if self.lumea.config.get("auto_edit_message"):
            await message.edit(message.content + " ")


    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        if before.author.id != self.lumea.user.id:
            return

        if self.lumea.config.get("process_edited_commands"):
            try:
                await self.lumea.process_commands(after)
            except:
                pass


async def setup(lumea):
    await lumea.add_cog(Events(lumea))