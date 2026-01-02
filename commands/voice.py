import discord

# Keep track of the bot joining voice channels
async def setup(bot):
    # MY_GUILD = discord.Object(id=GUILD_ID)

    async def ensure_voice(interaction: discord.Interaction):
        """Helper function to connect the bot to user's voice channel."""
        if not interaction.user.voice or not interaction.user.voice.channel:
            await interaction.followup.send("❌ You must be in a voice channel.", ephemeral=True)
            return None

        channel = interaction.user.voice.channel
        vc = interaction.guild.voice_client

        if not vc or not vc.is_connected():
            try:
                vc = await channel.connect(timeout=20)
            except Exception as e:
                await interaction.followup.send("❌ Failed to join voice channel.", ephemeral=True)
                print(e)
                return None
        else:
            if vc.channel != channel:
                await vc.move_to(channel)
        return vc

    # ---------------- /join ----------------
    @bot.tree.command(name="join", description="Join your voice channel")
    async def join(interaction: discord.Interaction):
        await interaction.response.defer()
        vc = await ensure_voice(interaction)
        if vc:
            await interaction.followup.send(f"🔊 Joined **{vc.channel.name}**")

    # ---------------- /leave ----------------
    @bot.tree.command(name="leave", description="Leave the voice channel")
    async def leave(interaction: discord.Interaction):
        vc = interaction.guild.voice_client
        if vc:
            await vc.disconnect()
            await interaction.response.send_message("Left the voice channel 👋")
        else:
            await interaction.response.send_message("I am not in a voice channel!", ephemeral=True)
