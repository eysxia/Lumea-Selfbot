import discord, time
from datetime import datetime
from discord.ext import commands
from utils.util import send_log_message, parse_duration


class Moderation(commands.Cog):
    def __init__(self, lumea):
        self.lumea = lumea


    @commands.command(brief="Moderation", usage="(channel) (seconds)", aliases=["slowmo", "slow", "sm"])
    async def slowmode(self, ctx, channel: discord.Channel=None, seconds: int=0):
        channel = channel or ctx.channel

        if seconds == 0:
            msg = f"Disabled slowmode for {channel.mention}"
        else:
            msg = f"Set slowmode in {channel.mention} to `{seconds}` second(s)"

        await ctx.channel.edit(slowmode_delay=seconds)
        await send_log_message(self, ctx, f"[?] {msg}")


    @commands.command(brief="Moderation", usage="(channel)", aliases=["lockdown", "l"])
    async def lock(self, ctx, channel: discord.TextChannel=None):
        channel = channel or ctx.channel
        overwrite = channel.overwrites_for(ctx.guild.default_role)

        currently_locked = overwrite.send_messages is False
        overwrite.send_messages = None if currently_locked else False

        await channel.set_permissions(ctx.guild.default_role, overwrite=overwrite)
        return await send_log_message(self, ctx, f"[?] {channel.mention} " + "unlocked" if currently_locked else "locked")
    

    @commands.command(brief="Moderation", usage="[user]", aliases=["softb", "sb"])
    async def softban(self, ctx, user: discord.Member=None):
        if user is None:
            if ctx.message.reference:
                user = await ctx.channel.fetch_message(ctx.message.reference.message_id).author
            else:
                return

        await user.ban(delete_message_days=1)
        await ctx.guild.unban(user)
        await send_log_message(self, ctx, f"[?] Soft Banned {user.mention}")


    @commands.command(brief="Moderation", usage="[user] (reason)", aliases=["b"])
    async def ban(self, ctx, user: discord.Member=None, *, reason=None):
        if user is None:
            if ctx.message.reference:
                user = await ctx.channel.fetch_message(ctx.message.reference.message_id).author
            else:
                return

        await user.ban(reason=reason)
        await send_log_message(self, ctx, f"[?] Banned {user.mention} " + f"for: `{reason}`" if reason else "")
    

    @commands.command(brief="Moderation", usage="[user]", aliases=["unb", "ub"])
    async def unban(self, ctx, user: discord.User=None):
        if user is None:
            if ctx.message.reference:
                user = await ctx.channel.fetch_message(ctx.message.reference.message_id).author
            else:
                return
            
        await ctx.guild.unban(user)
        await send_log_message(self, ctx, f"[?] Unbanned {user.mention}")


    @commands.command(brief="Moderation", usage="[user] (reason)", aliases=["k"])
    async def kick(self, ctx, user: discord.Member=None, *, reason=None):
        if user is None:
            if ctx.message.reference:
                user = await ctx.channel.fetch_message(ctx.message.reference.message_id).author
            else:
                return
            
        await user.kick(reason=reason)
        await send_log_message(self, ctx, f"[?] Kicked {user.mention} " + f"for: `{reason}`" if reason else "")


    @commands.command(brief="Moderation", usage="[user] (duration)", aliases=["mute", "m"])
    async def timeout(self, ctx, user: discord.Member=None, *, duration=None):
        if user is None:
            if ctx.message.reference:
                user = await ctx.channel.fetch_message(ctx.message.reference.message_id).author
            else:
                return
            
        if duration is None:
            await user.edit(timed_out_until=None)
            return await send_log_message(self, ctx, f"[?] Unmuted {user.mention}")
        
        await user.edit(timed_out_until=datetime.now(datetime.UTC) + parse_duration(duration))
        await send_log_message(self, ctx, f"[?] Muted {user.mention} for: `{duration}`")
    

    @commands.command(brief="Moderation", usage="[user] (nickname)", aliases=["nickname", "renick"])
    async def nick(self, ctx, user: discord.Member=None, *, nickname=None):
        if user is None:
            if ctx.message.reference:
                user = await ctx.channel.fetch_message(ctx.message.reference.message_id).author
            else:
                return
            
        await user.edit(nick=nickname)
        if nickname == None:
            msg = f"Reset nickname for {user.mention}"
        else:
            msg = f"Set nickname for {user.mention} to `{nickname}`"
        await send_log_message(self, ctx, f"[?] {msg}")


    @commands.command(brief="Moderation", usage="[role] [user]", aliases=["unrole", "r"])
    async def role(self, ctx, role: discord.Role, user: discord.Member=None):
        if user is None:
            if ctx.message.reference:
                user = await ctx.channel.fetch_message(ctx.message.reference.message_id).author
            else:
                return
            
        if role in user.roles:
            await user.remove_roles(role)
            msg = f"Removed role {role.mention} from {user.mention}"
        else:
            await user.add_roles(role)
            msg = f"Added role {role.mention} to {user.mention}"

        return await send_log_message(self, ctx, f"[?] {msg}")


async def setup(lumea):
    await lumea.add_cog(Moderation(lumea))