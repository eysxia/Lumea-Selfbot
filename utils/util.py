import colorama, requests
import json, asyncio
import os, shutil
import re, spotipy
import datetime


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


def parse_duration(duration_str: str) -> datetime.timedelta:
    parts = re.findall(r"(\d+)([smhd])", duration_str.lower())
    if not parts:
        if duration_str.isdigit():
            return datetime.timedelta(minutes=int(duration_str))
        else:
            return datetime.timedelta(minutes=int(10))

    total = datetime.timedelta()
    for value, unit in parts:
        value = int(value)
        if unit == 's':
            total += datetime.timedelta(seconds=value)
        elif unit == 'm':
            total += datetime.timedelta(minutes=value)
        elif unit == 'h':
            total += datetime.timedelta(hours=value)
        elif unit == 'd':
            total += datetime.timedelta(days=value)
        else:
            pass

    return total


async def handle_spotify_auth(self, ctx):
    try:
        playback = self.spotify_client.current_playback()
        devices = self.spotify_client.devices().get("devices", [])

        if not playback or not playback.get("device") or not playback["device"]["is_active"]:
            last_device = playback["device"] if playback and playback.get("device") else None
            last_device_id = last_device["id"] if last_device else None

        if last_device_id and any(d["id"] == last_device_id for d in devices):
            target_id = last_device_id
        elif devices:
            target_id = devices[0]["id"]
        else:
            target_id = None

        if target_id:
            self.spotify_client.transfer_playback(device_id=target_id, force_play=False)
    except spotipy.SpotifyException as e:
        if e.http_status == 401:
            if self.lumea.spotify.get("refresh_token"):
                response = requests.post(self.lumea.manifest.get("spotify_auth_url"), data={"refresh_token": self.lumea.spotify["refresh_token"]})
                access_token = response.json().get("access_token")
                if access_token:
                    self.lumea.spotify["access_token"] = access_token
                    save_config(self, "spotify")
                    self.spotify_client = spotipy.Spotify(auth=self.lumea.spotify.get("access_token"))
                    return True
                
            await ctx.send("**[!] Youre spotify token is invalid or unset!")
            await ctx.send(f"Get your token **[here]({self.lumea.manifest.get("spotify_auth_url")}**, and set it using `{self.lumea.data.get("prefix")}sauth [access_token] [refresh_token]` or manulally set them in the config files.")
            return False