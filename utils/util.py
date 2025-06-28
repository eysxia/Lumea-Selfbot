import colorama
import json
import asyncio
import os
import shutil
import re
from datetime import datetime, timedelta


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


async def send_log_message(self, ctx, message, print=True):
    if message.startswith("[?"):
        color = colorama.Fore.CYAN
    elif message.startswith("[!"):
        color = colorama.Fore.YELLOW
    elif message.startswith("[#"):
        color = colorama.Fore.RED

    if print:
        if self.lumea.config.get("log_to_console") is True:
            print_centered(f"{color}{message}")
        
    message = await ctx.send(f"> **{message[:3]}**{message[3:].replace("<@", "<@!")}")
    await asyncio.sleep(3)
    await message.delete()


def save_config(self, file):
    with open(f"../config/{file}.json", "w") as f:
        f.write(json.dumps(getattr(self.lumea, file, None)))


def parse_duration(duration_str: str) -> timedelta:
    parts = re.findall(r"(\d+)([smhd])", duration_str.lower())
    if not parts:
        if duration_str.isdigit():
            return timedelta(minutes=int(duration_str))
        else:
            return timedelta(minutes=int(10))

    total = timedelta()
    for value, unit in parts:
        value = int(value)
        if unit == 's':
            total += timedelta(seconds=value)
        elif unit == 'm':
            total += timedelta(minutes=value)
        elif unit == 'h':
            total += timedelta(hours=value)
        elif unit == 'd':
            total += timedelta(days=value)
        else:
            pass

    return total