from discord.ext import commands
from utils.util import save_config, send_log_message


class Other(commands.Cog):
    def __init__(self, lumea):
        self.lumea = lumea


    @commands.command(brief="Other")
    async def logging(self, ctx):
        if self.lumea.config.get("log_to_console") is True:
            self.lumea.config["log_to_console"] = False
        else:
            self.lumea.config["log_to_console"] = True

        await send_log_message(self, ctx, f"[?] Console error logging toggled! `({self.lumea.config.get("log_to_console")})`")
        save_config(self, "config")


    @commands.command(brief="Other")
    async def autoedit(self, ctx):
        if self.lumea.config.get("auto_edit_message") is True:
            self.lumea.config["auto_edit_message"] = False
        else:
            self.lumea.config["auto_edit_message"] = True

        await send_log_message(self, ctx, f"[?] Auto message edit toggled! `({self.lumea.config.get("auto_edit_message")})`")
        save_config(self, "config")


    @commands.command(brief="Other")
    async def procedit(self, ctx):
        if self.lumea.config.get("process_edited_commands") is True:
            self.lumea.config["process_edited_commands"] = False
        else:
            self.lumea.config["process_edited_commands"] = True

        await send_log_message(self, ctx, f"[?] Process edited commands toggled! `({self.lumea.config.get("process_edited_commands")})`")
        save_config(self, "config")


async def setup(lumea):
    await lumea.add_cog(Other(lumea))