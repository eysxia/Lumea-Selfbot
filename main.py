import colorama
import datetime
import json
import os
from discord.ext import commands
from utils.util import clear_console, print_centered


with open("./manifest.json", "r") as f:
    manifest = json.loads(f.read())

with open("./config/data.json", "r") as f:
    data = json.loads(f.read())

with open("./config/config.json", "r") as f:
    config = json.loads(f.read())


lumea = commands.Bot(command_prefix=data.get("prefix"), help_command=None, self_bot=True)


@lumea.event
async def on_ready():
    lumea.uptime = datetime.datetime.now(datetime.UTC)
    lumea.manifest = manifest
    lumea.data = data
    lumea.config = config
    await load_cogs()
    
    clear_console()
    print_centered(f"{colorama.Fore.CYAN} ___ {colorama.Fore.WHITE}     _                                    {colorama.Fore.CYAN} ___ \n" 
                   f"{colorama.Fore.CYAN}|  _|{colorama.Fore.WHITE}    | |                                   {colorama.Fore.CYAN}|_  |\n"
                   f"{colorama.Fore.CYAN}| |  {colorama.Fore.WHITE}    | |    _   _ _ __ ___   ___  __ _     {colorama.Fore.CYAN}  | |\n"
                   f"{colorama.Fore.CYAN}| |  {colorama.Fore.WHITE}    | |   | | | | '_ ` _ \ / _ \/ _` |    {colorama.Fore.CYAN}  | |\n"
                   f"{colorama.Fore.CYAN}| |  {colorama.Fore.WHITE}    | |___| |_| | | | | | |  __/ (_| |    {colorama.Fore.CYAN}  | |\n"
                   f"{colorama.Fore.CYAN}| |_ {colorama.Fore.WHITE}    \_____/\__,_|_| |_| |_|\___|\__,_|    {colorama.Fore.CYAN} _| |\n"
                   f"{colorama.Fore.CYAN}|___|{colorama.Fore.WHITE}                                          {colorama.Fore.CYAN}|___|")
    print_centered(f"{colorama.Fore.CYAN}[ Lumea Version {manifest.get("lumea").get("version")} ]")
    print_centered(f"{colorama.Fore.CYAN}[ Lumea Commands: {len(lumea.commands)} ]")
    print()
    print_centered(f"{colorama.Fore.WHITE}Logged in as: {colorama.Fore.CYAN}{lumea.user.name}")
    print_centered(f"{colorama.Fore.WHITE}Total Guilds {colorama.Fore.CYAN}{len(lumea.guilds)}")
    print()
    print_centered(f"{colorama.Fore.CYAN}========================================")
    print()


async def load_cogs():
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py"):
            await lumea.load_extension(f"cogs.{filename[:-3]}")


lumea.run(data.get("token"))
