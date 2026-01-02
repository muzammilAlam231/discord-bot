import discord
from discord import app_commands
import asyncio
from config import YTDL_OPTIONS, FFMPEG_OPTIONS
from utils.music_utils import yt_search, get_audio_url, ensure_voice, music_queue

current_song = None  # Track currently playing song globally

async def setup(bot):
    # MY_GUILD = discord.Object(id=GUILD_ID)
    # Create guild objects for instant command registration

    # ---------------- BUTTONS ----------------
    class SongButton(discord.ui.Button):
        def __init__(self, label: str, song: dict):
            # Truncate label to 80 chars
            label = label[:80]
            super().__init__(label=label, style=discord.ButtonStyle.primary)
            self.song = song

        async def callback(self, interaction: discord.Interaction):
            await interaction.response.defer()
            vc = await ensure_voice(interaction)
            if not vc:
                return

            audio_url, title = await asyncio.to_thread(get_audio_url, self.song["webpage_url"])
            song_data = {"title": title, "webpage_url": self.song["webpage_url"], "url": audio_url}

            global current_song
            if not vc.is_playing() and not vc.is_paused():
                source = discord.FFmpegPCMAudio(audio_url, **FFMPEG_OPTIONS)

                def after_playing(error):
                    if error:
                        print("Playback error:", error)
                    bot.loop.create_task(play_next(interaction.guild))

                vc.play(source, after=after_playing)
                current_song = song_data
                await interaction.followup.send(f"▶️ **Now Playing:** {title}")
            else:
                music_queue.append(song_data)
                await interaction.followup.send(f"➕ **Added to queue:** {title}")

    # ---------------- VIEW ----------------
    class SongSelectView(discord.ui.View):
        def __init__(self, songs, timeout=None):
            super().__init__(timeout=timeout)
            self.songs = songs
            for i, song in enumerate(songs[:5], start=1):
                label = f"{i}. {song['title']}"
                self.add_item(SongButton(label=label, song=song))

    # ---------------- PLAY NEXT ----------------
    async def play_next(guild):
        global current_song
        if not music_queue:
            current_song = None
            return

        vc = guild.voice_client
        if not vc:
            return

        song = music_queue.pop(0)
        current_song = song
        audio_url, title = await asyncio.to_thread(get_audio_url, song["webpage_url"])
        source = discord.FFmpegPCMAudio(audio_url, **FFMPEG_OPTIONS)

        def after_playing(error):
            if error:
                print("Playback error:", error)
            bot.loop.create_task(play_next(guild))

        vc.play(source, after=after_playing)
        if guild.text_channels:
            await guild.text_channels[0].send(f"▶️ **Now Playing:** {title}")

    # ---------------- /play ----------------
    @bot.tree.command(name="play", description="Play or queue a song")
    async def play(interaction: discord.Interaction, query: str):
        await interaction.response.defer()
        vc = await ensure_voice(interaction)
        if not vc:
            return await interaction.followup.send("❌ Could not join a voice channel.")

        results = await asyncio.to_thread(yt_search, query, YTDL_OPTIONS)
        entries = results.get("entries") or [results]
        entries = [r for r in entries if isinstance(r, dict)][:5]

        if not entries:
            return await interaction.followup.send("❌ No results found.")

        view = SongSelectView(entries, timeout=None)
        await interaction.followup.send("🎵 **Choose a song:**", view=view)

    # ---------------- /skip ----------------
    @bot.tree.command(name="skip", description="Skip current song")
    async def skip(interaction: discord.Interaction):
        vc = interaction.guild.voice_client
        if vc and vc.is_playing():
            vc.stop()
            await interaction.response.send_message("⏭️ Skipped!")
        else:
            await interaction.response.send_message("❌ Nothing is playing.", ephemeral=True)

    # ---------------- /pause ----------------
    @bot.tree.command(name="pause", description="Pause music")
    async def pause(interaction: discord.Interaction):
        vc = interaction.guild.voice_client
        if vc and vc.is_playing():
            vc.pause()
            await interaction.response.send_message("⏸️ Music paused")
        else:
            await interaction.response.send_message("❌ No music is playing.", ephemeral=True)

    # ---------------- /resume ----------------
    @bot.tree.command(name="resume", description="Resume music")
    async def resume(interaction: discord.Interaction):
        vc = interaction.guild.voice_client
        if vc and vc.is_paused():
            vc.resume()
            await interaction.response.send_message("▶️ Music resumed")
        else:
            await interaction.response.send_message("❌ Music is not paused.", ephemeral=True)

    # ---------------- /stop ----------------
    @bot.tree.command(name="stop", description="Stop music")
    async def stop(interaction: discord.Interaction):
        vc = interaction.guild.voice_client
        if vc:
            vc.stop()
            await interaction.response.send_message("⏹️ Music stopped")
        else:
            await interaction.response.send_message("❌ Nothing is playing.", ephemeral=True)

    # ---------------- /queue ----------------
    @bot.tree.command(name="queue", description="Show song queue")
    async def queue_cmd(interaction: discord.Interaction):
        msg = ""
        if current_song:
            msg += f"▶️ **Now Playing:** {current_song['title']}\n\n"
        if not music_queue:
            msg += "📭 Queue is empty."
        else:
            msg += "🎶 **Up Next:**\n"
            for i, song in enumerate(music_queue, start=1):
                msg += f"{i}. {song['title']}\n"
        await interaction.response.send_message(msg)
