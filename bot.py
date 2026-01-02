import discord
from discord.ext import commands
from config import TOKEN
import asyncio
import random


CHANNEL_ID = 1455171210093789331
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix="!", intents=intents)

initial_extensions = [
    "commands.fun",
    "commands.music",
    "commands.voice"
]

@bot.event
async def on_ready():
    print(f"{bot.user} connected!")

    # Load all extensions
    for ext in initial_extensions:
        try:
            await bot.load_extension(ext)
            print(f"Loaded {ext}")
        except Exception as e:
            print(f"Failed to load {ext}: {e}")

    await asyncio.sleep(1)

    synced = await bot.tree.sync()
    print(f"Global commands synced ({len(synced)})")


@bot.event
async def on_member_join(member):

    text_channels = [ch for ch in member.guild.text_channels if ch.permissions_for(member.guild.me).send_messages]

    if not text_channels:
        return

    channel = random.choice(text_channels)
    embed = discord.Embed(
        title="🎉 Welcome to the Server!",
        description=f"Hello {member.mention}, welcome to **{member.guild.name}**! Enjoy your stay!",
        color=discord.Color.green()
    )

    if member.avatar:
        embed.set_thumbnail(url=member.avatar.url)

    embed.add_field(name="Server Members", value=f"{member.guild.member_count} members", inline=True)
    embed.set_footer(text="Have fun and follow the rules!")
    await channel.send(embed=embed)

@bot.command()
async def sync(ctx):
    """Sync slash commands globally (Owner only)"""
    if ctx.author.id != 613697969514086433:  # Your OWNER_ID
        await ctx.send("❌ You don't have permission to use this command.")
        return
    
    try:
        synced = await bot.tree.sync()
        await ctx.send(f"✅ Synced **{len(synced)}** commands globally!")
    except Exception as e:
        await ctx.send(f"❌ Failed to sync commands: {e}")

bot.run(TOKEN)
