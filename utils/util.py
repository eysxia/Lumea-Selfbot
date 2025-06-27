import colorama
import json
import asyncio
import os
import shutil
import re


def clear_console():
    os.system('cls' if os.name == 'nt' else 'clear')


def strip_ansi(text):
    ansi_escape = re.compile(r'\x1B\[[0-?]*[ -/]*[@-~]')
    return ansi_escape.sub('', text)


def print_centered(text):
    columns = shutil.get_terminal_size().columns
    for line in text.splitlines():
        line_stripped = line.strip('\n')
        padding = max((columns - len(strip_ansi(line_stripped))) // 2, 0)
        print(' ' * padding + line_stripped)


async def send_log_message(self, ctx, message):
    if message.startswith("[?"):
        color = colorama.Fore.CYAN
    elif message.startswith("[!"):
        color = colorama.Fore.YELLOW
    elif message.startswith("[#"):
        color = colorama.Fore.RED

    if self.lumea.config.get("log_to_console") is True:
        print_centered(f"{color}{message}")
        
    message = await ctx.send(f"> **{message[:3]}**{message[3:]}")
    await asyncio.sleep(3)
    await message.delete()


async def save_config(self, file):
    with open(f".../config/{file}.json", "w") as f:
        f.write(json.dumps(self.lumea.config))