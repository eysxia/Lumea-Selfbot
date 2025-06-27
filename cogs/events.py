from discord.ext import commands
from utils.util import print_centered


class Events(commands.Cog):
    def __init__(self, lumea):
        self.lumea = lumea


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