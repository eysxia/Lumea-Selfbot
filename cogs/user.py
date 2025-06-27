import discord, typing
import aiohttp, io
from discord.ext import commands
from utils.util import save_config, send_log_message


class User(commands.Cog):
    def __init__(self, lumea):
        self.lumea = lumea


    @commands.command(brief="User", usage="[name]")
    async def username(self, ctx, username):
        try:
            await self.lumea.user.edit(username=username.strip().replace("@", ""))
            return await send_log_message(self, ctx, "[?] Successfully changed username!")
        except:
            return await send_log_message(self, ctx, "[!] Failed to update username!")
            

    @commands.command(brief="User", usage="(user) (file)", aliases=["av"])
    async def avatar(self, ctx, user: typing.Union[discord.Member, discord.User]=None):
        if user == None:
            user = self.lumea.user

        if ctx.message.attachments:
            attachment = ctx.message.attachments[0]
            image = await attachment.read()
            try:
                await self.lumea.user.edit(avatar=image)
                return await send_log_message(self, ctx, "[?] Successfully changed avatar!")
            except:
                return await send_log_message(self, ctx, "[!] Failed to update avatar!")
            
        async with aiohttp.ClientSession() as session:
            async with session.get(user.display_avatar.url) as resp:
                if resp.status != 200:
                    return await send_log_message(self, ctx, "[!] Failed to retrieve avatar!")
                data = await resp.read()

        file = discord.File(io.BytesIO(data), filename=f"avatar.png")
        await ctx.send(file=file)
            

    @commands.command(brief="User", usage="(user)", aliases=["displayavatar"])
    async def displayav(self, ctx, user: typing.Union[discord.Member, discord.User]=None):
        if user == None:
            user = self.lumea.user

        user = ctx.guild.get_member(user.id)
        avatar_url = user.avatar.url if user.avatar else user.display_avatar.url

        async with aiohttp.ClientSession() as session:
            async with session.get(avatar_url) as resp:
                if resp.status != 200:
                    return await send_log_message(self, ctx, "[!] Failed to retrieve users server avatar!")
                data = await resp.read()

        file = discord.File(io.BytesIO(data), filename=f"avatar.png")
        await ctx.send(file=file)


    @commands.command(brief="User", usage="(user)", aliases=["bnr"])
    async def banner(self, ctx, user: typing.Union[discord.Member, discord.User]=None):
        if user == None:
            user = self.lumea.user

        if user.banner == None:
            return await send_log_message(self, ctx, "[!] Failed to retrieve users banner!")
        
        async with aiohttp.ClientSession() as session:
            async with session.get(user.banner.url) as resp:
                if resp.status != 200:
                    return await send_log_message(self, ctx, "[!] Failed to retrieve users banner!")
                data = await resp.read()

        file = discord.File(io.BytesIO(data), filename=f"banner.png")
        await ctx.send(file=file)


async def setup(lumea):
    await lumea.add_cog(User(lumea))