import discord
import aiohttp
import io
from discord.ext import commands
from utils.util import send_log_message


class Server(commands.Cog):
    def __init__(self, lumea):
        self.lumea = lumea


    @commands.command(brief="Server", aliases=["server", "serverinfo", "si", "guild"])
    async def sinfo(self, ctx):
        bots = 0
        mbrs = 0
        boosters = 0

        for member in ctx.guild.members:  
            if member.bot:
                bots += 1
            else:
                mbrs += 1 
        
        if ctx.guild.premium_subscriber_role:
            boosters += len(ctx.guild.premium_subscriber_role.members) 

        await ctx.send(f">>> **{ctx.guild.name}** - <t:{int(ctx.guild.created_at.timestamp())}:F>\n"
                       f"**Description:** " + ctx.guild.description if ctx.guild.description else "None" + "\n"
                       f"**Icon:** " + f"[URL]({ctx.guild.icon.url})" if ctx.guild.icon else "None" + "\n"
                       f"**Banner:** " + f"[URL]({ctx.guild.banner.url})" if ctx.guild.banner else "None" + "\n"
                       f"**Splash:** " + f"[URL]({ctx.guild.splash.url})" if ctx.guild.splash else "None" + "\n"
                       f"**Vanity:** {ctx.guild.vanity_url_code}\n\n"
                       f"**__Members:__** ({ctx.guild.member_count})\n"
                       f"**Owner:** {ctx.guild.owner.mention}\n"
                       f"**Boosters:** {boosters}\n"
                       f"**Members:** {mbrs}\n"
                       f"**Bots:** {bots}\n\n"
                       f"**__Channels:__** ({len(ctx.guild.channels)})\n"
                       f"**Categories:** {len(ctx.guild.categories)}\n"
                       f"**Text:** {len(ctx.guild.text_channels)}\n"
                       f"**Voice:** {len(ctx.guild.voice_channels)}\n")


    @commands.command(brief="Server", usage="(invite code) (file)", aliases=["serverav", "sav", "serveravatar"])
    async def savatar(self, ctx, invite_code=None):
        if ctx.message.attachments:
            attachment = ctx.message.attachments[0]
            image = await attachment.read()
            try:
                await ctx.guild.edit(icon=image)
                return await send_log_message(self, ctx, "[?] Successfully changed servers icon!")
            except:
                return await send_log_message(self, ctx, "[!] Failed to update servers icon!")

        if invite_code is not None:
            async with aiohttp.ClientSession() as cs:
                async with cs.get(f"https://discord.com/api/invite/{invite_code}") as r:
                    data = await r.json()
            try: 
                if "a_" in data["guild"]["avatar"]:
                    format = ".gif"
                else:
                    format = ".png"  
                avatar_url = "https://cdn.discordapp.com/avatar/" + data["guild"]["id"] + "/" + data["guild"]["avatar"] + f"{format}?size=1024"
            except:
                avatar_url = ctx.guild.icon.url

        async with aiohttp.ClientSession() as session:
            async with session.get(ctx.guild.icon.url) as resp:
                if resp.status != 200:
                    return await send_log_message(self, ctx, "[!] Failed to retrieve server icon!")
                data = await resp.read()

        file = discord.File(io.BytesIO(data), filename=f"icon.png")
        await ctx.send(file=file)


    @commands.command(brief="Server", usage="(invite code) (file)", aliases=["serverbnr", "sbnr", "serverbanner"])
    async def sbanner(self, ctx, invite_code=None):
        if ctx.message.attachments:
            attachment = ctx.message.attachments[0]
            image = await attachment.read()
            try:
                await ctx.guild.edit(banner=image)
                return await send_log_message(self, ctx, "[?] Successfully changed servers banner!")
            except:
                return await send_log_message(self, ctx, "[!] Failed to update servers banner!")

        if invite_code is not None:
            async with aiohttp.ClientSession() as cs:
                async with cs.get(f"https://discord.com/api/invite/{invite_code}") as r:
                    data = await r.json()
            try: 
                if "a_" in data["guild"]["banner"]:
                    format = ".gif"
                else:
                    format = ".png"
                banner_url = "https://cdn.discordapp.com/banners/" + data["guild"]["id"] + "/" + data["guild"]["banner"] + f"{format}?size=1024"
            except:
                banner_url = ctx.guild.banner.url

        async with aiohttp.ClientSession() as session:
            async with session.get(banner_url) as resp:
                if resp.status != 200:
                    return await send_log_message(self, ctx, "[!] Failed to retrieve server banner!")
                data = await resp.read()

        file = discord.File(io.BytesIO(data), filename=f"banner.png")
        await ctx.send(file=file)


    @commands.command(brief="Server", usage="(invite code) (file)", aliases=["serversplash"])
    async def ssplash(self, ctx, invite_code=None):
        if ctx.message.attachments:
            attachment = ctx.message.attachments[0]
            image = await attachment.read()
            try:
                await ctx.guild.edit(splash=image)
                return await send_log_message(self, ctx, "[?] Successfully changed servers splash!")
            except:
                return await send_log_message(self, ctx, "[!] Failed to update servers splash!")
        
        if invite_code is not None:
            async with aiohttp.ClientSession() as cs:
                async with cs.get(f"https://discord.com/api/invite/{invite_code}") as r:
                    data = await r.json()
            try: 
                if "a_" in data["guild"]["splash"]:
                    format = ".gif"
                else:
                    format = ".png"
                splash_url = "https://cdn.discordapp.com/splash/" + data["guild"]["id"] + "/" + data["guild"]["splash"] + f"{format}?size=1024"
            except:
                splash_url = ctx.guild.splash.url

        async with aiohttp.ClientSession() as session:
            async with session.get(splash_url) as resp:
                if resp.status != 200:
                    return await send_log_message(self, ctx, "[!] Failed to retrieve server splash!")
                data = await resp.read()

        file = discord.File(io.BytesIO(data), filename=f"splash.png")
        await ctx.send(file=file)


    @commands.command(brief="Server", usage="(page)")
    async def boosters(self, ctx, page: int = 1):
        boosted = [mbr for mbr in ctx.guild.members if mbr.premium_since]
        if not boosted:
            return await send_log_message(self, ctx, "[!] This server has no boosters!")

        boosted = sorted(boosted, key=lambda mbr: mbr.premium_since, reverse=False)

        pages = []
        current_page = ""
        count = 1

        for member in boosted:
            line = f"{count}. {member} - <t:{int(member.premium_since.timestamp())}:R>\n"
            if len(current_page) + len(line) > 1800:
                pages.append(current_page)
                current_page = ""
            current_page += line
            count += 1

        if current_page:
            pages.append(current_page)

        page = max(1, min(page, len(pages)))
        await ctx.send(f">>> [?] Boosters for `{ctx.guild.name}`\n"
                        f"Page {page}/{len(pages)} | Total: {len(boosted)}\n\n"
                        f"{pages[page - 1]}")


async def setup(lumea):
    await lumea.add_cog(Server(lumea))