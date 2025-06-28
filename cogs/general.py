import time
from discord.ext import commands
from utils.util import send_log_message


class General(commands.Cog):
    def __init__(self, lumea):
        self.lumea = lumea


    @commands.command(brief="General", usage="(category)", aliases=["h"])
    async def help(self, ctx, category=None):
        if category is None:
            await ctx.send(f"```ini\n"
                           f"       [ Lumea Help ]\n"
                           f"  Use {self.lumea.data.get('prefix')}help (category)\n"
                           f"  Params: [] = Required, () = Optional\n"
                           f"\n"
                           f"  -- [Categories] --\n"
                           f"  - General\n"
                           f"  - Server\n"
                           f"  - User\n"
                           f"  - Moderation\n"
                           f"  - Config\n"
                           f"```")
        else:
            category = category.lower().capitalize()
            cmds = []
            for cmd in self.lumea.commands:
                if not cmd.hidden and cmd.brief == category:
                    cmds.append(f"  - {cmd.name.capitalize() if cmd.name else cmd.capitalize()} {cmd.usage if cmd.usage else ""}")

            if len(cmds) == 0:
                return await send_log_message(self, ctx, f"[!] Cateogry `{category}` not found!")
            
            await ctx.send("```ini\n"
                           f"       [ Lumea - {category} ]\n"
                           f"  Use {self.lumea.data.get('prefix')}help (category)\n"
                           f"  Params: [] = Required, () = Optional\n"
                           f"\n"
                           f"  -- [Commands] --\n"
                           f"{"\n".join(cmd for cmd in cmds)}"
                           "```")


    @commands.command(brief="General")
    async def ping(self, ctx):
        websocket_latency = round(self.lumea.latency * 1000)
        message = await ctx.send(f">>> 🏓 Pong!\n"
                                 f"WebSocket Latency: `{websocket_latency}ms`")

        start_time = time.time()
        end_time = time.time()
        api_latency = round((end_time - start_time) * 1000)

        await message.edit(content=message.content + f"\nAPI Latency: `{api_latency}ms`")


    @commands.command(brief="General")
    async def uptime(self, ctx):
        await ctx.send(f"> 🕒 **__Uptime:__** <t:{int(self.lumea.uptime.timestamp())}:R>")


async def setup(lumea):
    await lumea.add_cog(General(lumea))