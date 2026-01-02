import yt_dlp
import discord
import asyncio

music_queue = []
current_song = None

YTDL_OPTIONS = {
    "format": "bestaudio",
    "quiet": True,
    "no_warnings": True,
    "default_search": "ytsearch",
    "skip_download": True,
    "cachedir": False
}

FFMPEG_OPTIONS = {
    "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
    "options": "-vn"
}

def yt_search(query, ytdl_opts=None):
    ytdl_opts = ytdl_opts or YTDL_OPTIONS
    with yt_dlp.YoutubeDL(ytdl_opts) as ydl:
        return ydl.extract_info(f"ytsearch5:{query}", download=False)

def get_audio_url(video_url):
    with yt_dlp.YoutubeDL(YTDL_OPTIONS) as ydl:
        info = ydl.extract_info(video_url, download=False)
        if "entries" in info:
            info = info["entries"][0]
        return info["url"], info.get("title", "Unknown")

async def ensure_voice(interaction: discord.Interaction):
    if not interaction.user.voice:
        await interaction.followup.send("❌ You must be in a voice channel.")
        return None
    channel = interaction.user.voice.channel
    vc = interaction.guild.voice_client
    if not vc or not vc.is_connected():
        try:
            vc = await channel.connect(timeout=20)
        except Exception as e:
            await interaction.followup.send("❌ Failed to join voice channel.")
            print(e)
            return None
    elif vc.channel != channel:
        await vc.move_to(channel)
    return vc

async def play_next(guild: discord.Guild):
    global current_song
    vc = guild.voice_client
    if not vc or not music_queue:
        current_song = None
        return

    info = music_queue.pop(0)
    current_song = info
    source = discord.FFmpegPCMAudio(info["url"], **FFMPEG_OPTIONS)

    def after_playing(error):
        if error:
            print(f"Error in after callback: {error}")
        # Schedule next song in the main bot loop
        if guild.voice_client:
            bot_loop = guild._state._loop  # get the bot's running loop
            bot_loop.create_task(play_next(guild))

    vc.play(source, after=after_playing)
