import discord, typing
import asyncio
from discord.ext import commands
from utils.util import save_config, send_log_message, handle_spotify_auth


class Spotify(commands.Cog):
    def __init__(self, lumea):
        self.lumea = lumea


    @commands.command(brief="Spotify", usage="[access_token] [refresh_token]", aliases=["spotifyauth"])
    async def sauth(self, ctx, access_token: str=None, refresh_token: str=None):
        if access_token is None or refresh_token is None:
            return await ctx.send("")
        
        self.lumea.spotify["access_token"] = access_token
        self.lumea.spotify["refresh_token"] = refresh_token
        save_config(self, "spotify")
        await send_log_message(self, ctx, "[?] Successfully set Spotify data!")
        

    @commands.command(brief="Spotify", usage="(user)", aliases=["listening"])
    async def playing(self, ctx, user: typing.Optional[typing.Union[discord.Member, discord.User]]=None):
        user = user or self.lumea.user

        if user == self.lumea.user:
            try:
                spotify_client = await handle_spotify_auth(self, ctx)
                if spotify_client is None:
                    raise

                current = spotify_client.current_playback()
                if current and current.get('is_playing'):
                    track = current['item']
                    name = track['name']
                    artist = ", ".join(f"**{a['name']}**" for a in track['artists'])
                    url = track['external_urls']['spotify']
                    return await ctx.send(f"**__[{name}]({url})__** by {artist}")
            except:
                pass

        is_listening = next((a for a in getattr(user, "activities", []) if isinstance(a, discord.Spotify)), None)

        if is_listening:
            base = f"{user.mention} is listening to: " if user != self.lumea.user else ""
            return await ctx.send(f"{base}**__[{is_listening.title}](https://open.spotify.com/track/{is_listening.track_id})__** by **{is_listening.artist}**")
        else:
            if user == self.lumea.user:
                return await send_log_message(self, ctx, f"[!] You're not currently listening to anything.")
            await send_log_message(self, ctx, f"[?] {user.mention} is not listening to Spotify.")


    @commands.command(brief="Spotify", usage="[url/name]", aliases=["resume", "p"])
    async def play(self, ctx, *, song=None):
        spotify_client = await handle_spotify_auth(self, ctx)
        if spotify_client is None:
            return

        if song:
            try:
                track_uri = None
                track_name = None
                track_url = None

                if song.startswith("https://open.spotify.com/") or song.startswith("spotify:"):
                    song = song.replace("https://open.spotify.com/", "").split("?")[0]
                    if "/" not in song:
                        raise ValueError("Invalid Spotify URL format.")
                    url_type, uri_id = song.split("/")
                    track_uri = f"spotify:{url_type}:{uri_id}"

                    if url_type == "track":
                        spotify_client.start_playback(uris=[track_uri])
                        track = spotify_client.track(track_uri)
                        track_name = track['name']
                        track_url = track['external_urls']['spotify']
                        artist = ", ".join(f"**{a['name']}**" for a in track['artists'])
                    elif url_type == "playlist":
                        spotify_client.start_playback(context_uri=track_uri)
                        playlist = spotify_client.playlist(track_uri)
                        track_name = playlist['name']
                        track_url = playlist['external_urls']['spotify']
                        artist = None
                    else:
                        pass
                else:
                    results = spotify_client.search(q=song, type='track', limit=1)
                    tracks = results.get('tracks', {}).get('items', [])
                    if tracks:
                        track = tracks[0]
                        track_uri = track['uri']
                        track_name = track['name']
                        track_url = track['external_urls']['spotify']
                        artist = ", ".join(f"**{a['name']}**" for a in track['artists'])
                        spotify_client.start_playback(uris=[track_uri])
                    else:
                        results = spotify_client.search(q=song, type='playlist', limit=1)
                        playlists = results.get('playlists', {}).get('items', [])
                        if not playlists:
                            return await send_log_message(self, ctx, f"[!] `{song}` could not be found as a song or playlist.")
                        playlist = playlists[0]
                        track_uri = playlist['uri']
                        track_name = playlist['name']
                        track_url = playlist['external_urls']['spotify']
                        artist = None
                        spotify_client.start_playback(context_uri=track_uri)

                msg = f"**[?]** Now playing **__[{track_name}]({track_url})__**"
                if artist:
                    msg += f" by {artist}"
                return await ctx.send(msg)
            except:
                return await send_log_message(self, ctx, "[!] Invalid input or playback failed.")

        current = spotify_client.current_playback()
        if not current:
            return await send_log_message(self, ctx, "[!] No active Spotify session found.")

        if current['is_playing']:
            return await send_log_message(self, ctx, "[?] Spotify is already unpaused.")
        spotify_client.start_playback()
        await send_log_message(self, ctx, "[?] Spotify Resumed.")


    @commands.command(brief="Spotify", aliases=["stop"])
    async def pause(self, ctx):
        spotify_client = await handle_spotify_auth(self, ctx)
        if spotify_client is None:
            return

        current = spotify_client.current_playback()
        if not current:
            return await send_log_message(self, ctx, "[!] No active Spotify session found.")

        if current['is_playing']:
            spotify_client.pause_playback()
            return await send_log_message(self, ctx, "[?] Spotify Paused.")
        await send_log_message(self, ctx, "[?] Spotify already paused.")


    @commands.command(brief="Spotify", usage="[url/name]", aliases=["q"])
    async def queue(self, ctx, *, song):
        spotify_client = await handle_spotify_auth(self, ctx)
        if spotify_client is None:
            return
        
        current = spotify_client.current_playback()
        if not current:
            return await send_log_message(self, ctx, "[!] No active Spotify session found.")

        track_uri = None
        track_name = None
        track_url = None

        if song.startswith("https://open.spotify.com/track/") or song.startswith("spotify:track:"):
            try:
                if song.startswith("https://open.spotify.com/track/"):
                    track_id = song.replace("https://open.spotify.com/track/", "").split("?")[0]
                    track_uri = f"spotify:track:{track_id}"
                else:
                    track_uri = song

                track = spotify_client.track(track_uri)
                track_name = track['name']
                track_url = track['external_urls']['spotify']

            except:
                return await send_log_message(self, ctx, "[!] Failed to queue: Invalid Spotify link.")
        else:
            results = spotify_client.search(q=song, type="track", limit=1)
            tracks = results.get('tracks', {}).get('items', [])
            if not tracks:
                return await send_log_message(self, ctx, f"[!] `{song}` song/playlist could not be found.")
            
            track = tracks[0]
            track_uri = track['uri']
            track_name = track['name']
            track_url = track['external_urls']['spotify']

        try:
            spotify_client.add_to_queue(track_uri)
            await ctx.send(f"**[?]** Added to queue: **__[{track_name}]({track_url})__**")
        except:
            await send_log_message(self, ctx, f"[!] Failed to add song to queue.")


    @commands.command(brief="Spotify", aliases=["replay", "r"])
    async def restart(self, ctx):
        spotify_client = await handle_spotify_auth(self, ctx)
        if spotify_client is None:
            return
        
        current = spotify_client.current_playback()
        if not current:
            return await send_log_message(self, ctx, "[!] No active Spotify session found.")

        spotify_client.seek_track(0)
        track = current['item']
        name = track['name']
        artist = ", ".join(f"**{a['name']}**" for a in track['artists'])
        url = track['external_urls']['spotify']
        await ctx.send(f"**[?]** Now playing **__[{name}]({url})__** by {artist}")


    @commands.command(brief="Spotify", aliases=["skip"])
    async def next(self, ctx):
        spotify_client = await handle_spotify_auth(self, ctx)
        if spotify_client is None:
            return
        
        current = spotify_client.current_playback()
        if not current:
            return await send_log_message(self, ctx, "[!] No active Spotify session found.")
        
        spotify_client.next_track()
        await asyncio.sleep(1)
        current = spotify_client.current_playback()
        track = current['item']
        name = track['name']
        artist = ", ".join(f"**{a['name']}**" for a in track['artists'])
        url = track['external_urls']['spotify']
        await send_log_message(self, ctx, f"[?] Skipped to next song.")
        await ctx.send(f"**[?]** Now playing **__[{name}]({url})__** by {artist}")


    @commands.command(brief="Spotify", aliases=["prev", "back"])
    async def previous(self, ctx):
        spotify_client = await handle_spotify_auth(self, ctx)
        if spotify_client is None:
            return
        
        current = spotify_client.current_playback()
        if not current:
            return await send_log_message(self, ctx, "[!] No active Spotify session found.")

        spotify_client.previous_track()
        await asyncio.sleep(1)
        current = spotify_client.current_playback()
        track = current['item']
        name = track['name']
        artist = ", ".join(f"**{a['name']}**" for a in track['artists'])
        url = track['external_urls']['spotify']
        await send_log_message(self, ctx, f"[?] Returned to previous song.")
        await ctx.send(f"**[?]** Now playing **__[{name}]({url})__** by {artist}")


    @commands.command(brief="Spotify", usage="[url/name]", aliases=["playplaylist", "pplaylist", "plist", "pp"])
    async def playlist(self, ctx, *, song):
        spotify_client = await handle_spotify_auth(self, ctx)
        if spotify_client is None:
            return

        current = spotify_client.current_playback()
        if not current:
            return await send_log_message(self, ctx, "[!] No active Spotify session found.")

        playlist_uri = None
        playlist_name = None
        playlist_url = None

        if song.startswith("https://open.spotify.com/playlist/") or song.startswith("spotify:playlist:"):
            try:
                if song.startswith("https://open.spotify.com/playlist/"):
                    playlist_id = song.replace("https://open.spotify.com/playlist/", "").split("?")[0]
                    playlist_uri = f"spotify:playlist:{playlist_id}"
                else:
                    playlist_uri = song

                playlist = spotify_client.playlist(playlist_uri)
                playlist_name = playlist['name']
                playlist_url = playlist['external_urls']['spotify']
            except:
                return await send_log_message(self, ctx, "[!] Invalid Spotify playlist link.")
        else:
            results = spotify_client.search(q=song, type='playlist', limit=10)
            playlists = results.get('playlists', {}).get('items', [])

            match = next((pl for pl in playlists if pl['name'].lower() == song.lower()), None)
            if not match:
                return await send_log_message(self, ctx, f"[!] `{song}` playlist could not be found.")
            
            playlist_uri = match['uri']
            playlist_name = match['name']
            playlist_url = match['external_urls']['spotify']

        spotify_client.start_playback(context_uri=playlist_uri)
        await ctx.send(f"**[?]** Now playing playlist: **__[{playlist_name}]({playlist_url})__**")


    @commands.command(brief="Spotify", usage="(on/off)", aliases=["s"])
    async def shuffle(self, ctx, mode: str=None):
        spotify_client = await handle_spotify_auth(self, ctx)
        if spotify_client is None:
            return

        if not mode:
            current = spotify_client.current_playback()
            if not current:
                return await send_log_message(self, ctx, "[!] No active Spotify session found.")
        
            state = "ON" if current.get("shuffle_state") else "OFF"
            return await send_log_message(self, ctx, f"[?] Shuffle is currently **{state}**.")

        if mode.lower() in ["on", "true"]:
            spotify_client.shuffle(state=True)
            return await send_log_message(self, ctx, "[?] Shuffle mode enabled.")
        elif mode.lower() in ["off", "false"]:
            spotify_client.shuffle(state=False)
            return await send_log_message(self, ctx, "[?] Shuffle mode disabled.")
        else:
            return await send_log_message(self, ctx, "[!] Invalid option. Use `on` or `off`.")
        

    @commands.command(brief="Set Spotify repeat mode", usage="(off/track/playlist)", aliases=["rp"])
    async def repeat(self, ctx, mode: str = None):
        spotify_client = await handle_spotify_auth(self, ctx)
        if spotify_client is None:
            return

        if not mode:
            current = spotify_client.current_playback()
            if not current:
                return await send_log_message(self, ctx, "[!] No active Spotify session found.")
            
            state = current.get("repeat_state", "off")
            return await send_log_message(self, ctx, f"[?] Repeat is currently **{state.upper()}**.")

        mode = mode.lower()
        if mode not in ["off", "track", "playlist"]:
            return await send_log_message(self, ctx, "[!] Invalid repeat mode. Use `off`, `track`, or `playlist`.")

        spotify_client.repeat(state=mode if mode != "playlist" else "context")
        return await send_log_message(self, ctx, f"[?] Repeat mode set to **{mode.upper()}**.")


    @commands.command(brief="Spotify", usage="(vol)", aliases=["vol", "v"])
    async def volume(self, ctx, vol: int=None):
        spotify_client = await handle_spotify_auth(self, ctx)
        if spotify_client is None:
            return

        current = spotify_client.current_playback()
        if not current:
            return await send_log_message(self, ctx, "[!] No active Spotify session found.")

        device = current['device']
        if vol is None:
            return await send_log_message(self, ctx, f"[?] Current Volume: **{device['volume_percent']}**")

        if not 0 <= vol <= 100:
            return await send_log_message(self, ctx, "[!] Volume must be between 0 and 100.")

        try:
            spotify_client.volume(volume_percent=vol)
            return await send_log_message(self, ctx, f"[?] Volume set to: **{device['volume_percent']}**")
        except:
            await send_log_message(self, ctx, "[!] Failed to set volume.")


async def setup(lumea):
    await lumea.add_cog(Spotify(lumea))