import discord
from discord.ext import commands
from discord import app_commands
from discord.ui import Button, View
import random
from utils.fun_roast_utils import FLIRTY_ROASTS, GENERAL_ROASTS
from utils.fun_joke_utils import jokes
import asyncio
import time
from PIL import Image, ImageDraw, ImageFont
import io
import requests
from collections import Counter
import re


OWNER_ID = 613697969514086433
ZAINAB_ID = 1433539239357710560
MESSAGE_WINDOW = 10  # Number of recent messages to track
REACTION_FREQUENCY = 5  # React every X messages
IMGFLIP_USER = "muzammil123"  # Optional
IMGFLIP_PASS = "print(\"password123\")"  # Optional
message_count = 0



async def setup(bot):
    # MY_GUILD = discord.Object(id=GUILD_ID)
    # Create guild objects for instant command registration
    @bot.tree.command(name="nigga_juice", description="Replies with your custom message")
    async def nigga_juice(interaction: discord.Interaction):
        await interaction.response.send_message("Here’s your juice! 🥤")

    @bot.tree.command(name="joke", description="Tells a random joke")
    async def joke(interaction: discord.Interaction):

        all_jokes = jokes["clean"] + jokes["dark"] + jokes["double_meaning"]
        await interaction.response.send_message(random.choice(all_jokes))


    @bot.tree.command(name="roast", description="Roast someone (friendly)")
    async def roast(interaction: discord.Interaction, user: discord.Member | None = None):


        target = user or interaction.user
        if (interaction.user.id == OWNER_ID and target.id == ZAINAB_ID) or (interaction.user.id == ZAINAB_ID and target.id == OWNER_ID):
            roast_line = random.choice(FLIRTY_ROASTS)
        else:
            roast_line = random.choice(GENERAL_ROASTS)

        await interaction.response.send_message(
            f"🔥 **{target.mention}**, {roast_line}"
        )




    SLAP_GIFS = [
        "https://media.giphy.com/media/Gf3AUz3eBNbTW/giphy.gif",
        "https://media.giphy.com/media/jLeyZWgtwgr2U/giphy.gif",
        "https://media.giphy.com/media/mEtSQlxqBtWWA/giphy.gif",
        "https://media.giphy.com/media/Zau0yrl17uzdK/giphy.gif",
        "https://media.giphy.com/media/3XlEk2RxPS1m8/giphy.gif",
        "https://media.giphy.com/media/6Fad0loHc6Cbe/giphy.gif"
    ]

    @bot.tree.command(name="slap", description="Slap someone playfully")
    async def slap(interaction: discord.Interaction, user: discord.Member):
        slaps = [
            "slaps you with a giant fish 🐟",
            "gives you a dramatic anime slap 💥",
            "slaps you with a pillow 🛏️",
            "slaps you lightly… emotionally 😭",
            "slaps you using pure disappointment 😐",
            "slaps you and immediately regrets it 😅",
            "slaps you with a flip-flop 🩴"
        ]

        embed = discord.Embed(
            description=f"👋 **{interaction.user.mention}** {random.choice(slaps)} **{user.mention}**",
            color=discord.Color.red()
        )

        embed.set_image(url=random.choice(SLAP_GIFS))

        await interaction.response.send_message(embed=embed)

    # Store active games
    guess_games = {}  # user_id: {"number": int, "attempts": int}

    @bot.tree.command(name="guess", description="Play a number guessing game (1-100)")
    async def guess(interaction: discord.Interaction, number: int):
        user_id = interaction.user.id

        # Start new game
        if user_id not in guess_games:
            secret = random.randint(1, 100)
            guess_games[user_id] = {
                "number": secret,
                "attempts": 7
            }

            await interaction.response.send_message(
                "🎯 **Number Guessing Game Started!**\n"
                "I'm thinking of a number between **1 and 100**.\n"
                "You have **7 attempts**.\n"
                "Use `/guess <number>` to play!"
            )
            return

        game = guess_games[user_id]
        game["attempts"] -= 1

        # Correct guess
        if number == game["number"]:
            del guess_games[user_id]
            await interaction.response.send_message(
                f"🎉 **Correct!** The number was **{number}** 😎"
            )
            return

        # Out of attempts
        if game["attempts"] == 0:
            answer = game["number"]
            del guess_games[user_id]
            await interaction.response.send_message(
                f"❌ **Game Over!** You ran out of attempts.\n"
                f"The number was **{answer}**."
            )
            return

        # Hint
        hint = "🔼 Too high!" if number > game["number"] else "🔽 Too low!"
        await interaction.response.send_message(
            f"{hint}\n"
            f"🧠 Attempts left: **{game['attempts']}**"
        )



#TIC TAC TOE:
    class TicTacToe(View):
        def __init__(self, player1: discord.Member, player2: discord.Member, bot_player: bool):
            super().__init__(timeout=120)
            self.player1 = player1
            self.player2 = player2
            self.bot_player = bot_player
            self.current_player = player1
            self.board = [""] * 9
            self.game_over = False

            # Add 9 buttons for the board
            for i in range(9):
                self.add_item(TicTacToeButton(i))

        # Determine symbol
        def symbol_for(self, user):
            return "❌" if user == self.player1 else "⭕"

        # Check winner
        def check_winner(self, symbol):
            wins = [
                (0, 1, 2), (3, 4, 5), (6, 7, 8),
                (0, 3, 6), (1, 4, 7), (2, 5, 8),
                (0, 4, 8), (2, 4, 6)
            ]
            return any(self.board[a] == self.board[b] == self.board[c] == symbol for a, b, c in wins)

        # Available moves
        def available_moves(self):
            return [i for i, v in enumerate(self.board) if v == ""]

        # Disable all buttons
        def disable_all(self):
            for item in self.children:
                item.disabled = True

        # Minimax AI
        def minimax(self, board, is_bot):
            if self.check_winner_static(board, "⭕"):
                return 1
            if self.check_winner_static(board, "❌"):
                return -1
            if all(board):
                return 0

            if is_bot:
                best_score = -float("inf")
                for i in range(9):
                    if board[i] == "":
                        board[i] = "⭕"
                        score = self.minimax(board, False)
                        board[i] = ""
                        best_score = max(score, best_score)
                return best_score
            else:
                best_score = float("inf")
                for i in range(9):
                    if board[i] == "":
                        board[i] = "❌"
                        score = self.minimax(board, True)
                        board[i] = ""
                        best_score = min(score, best_score)
                return best_score

        def best_move(self):
            move = None
            best_score_val = -float("inf")
            for i in range(9):
                if self.board[i] == "":
                    self.board[i] = "⭕"
                    score = self.minimax(self.board, False)
                    self.board[i] = ""
                    if score > best_score_val:
                        best_score_val = score
                        move = i
            return move

        # Static winner check for minimax
        def check_winner_static(self, board, symbol):
            wins = [
                (0, 1, 2), (3, 4, 5), (6, 7, 8),
                (0, 3, 6), (1, 4, 7), (2, 5, 8),
                (0, 4, 8), (2, 4, 6)
            ]
            return any(board[a] == board[b] == board[c] == symbol for a, b, c in wins)

    # ---------- BUTTON CLASS ----------
    class TicTacToeButton(Button):
        def __init__(self, index: int):
            super().__init__(label="⬜", style=discord.ButtonStyle.secondary, row=index // 3)
            self.index = index

        async def callback(self, interaction: discord.Interaction):
            view: TicTacToe = self.view

            if view.game_over:
                return

            # Validate turn
            if interaction.user != view.current_player:
                await interaction.response.send_message("❌ Not your turn!", ephemeral=True)
                return

            if view.board[self.index]:
                return

            # Player move
            view.board[self.index] = view.symbol_for(interaction.user)
            self.label = view.symbol_for(interaction.user)
            self.disabled = True

            # Check player win
            if view.check_winner(view.symbol_for(interaction.user)):
                view.game_over = True
                view.disable_all()
                await interaction.response.edit_message(
                    content=f"🎉 {interaction.user.mention} wins!", view=view
                )
                return

            # Check draw
            if not view.available_moves():
                view.game_over = True
                view.disable_all()
                await interaction.response.edit_message(
                    content="🤝 It's a draw!", view=view
                )
                return

            # Switch turn
            view.current_player = (
                view.player2 if view.current_player == view.player1 else view.player1
            )

            # Bot move if PvE
            if view.bot_player and view.current_player.bot:
                bot_index = view.best_move()
                view.board[bot_index] = "⭕"
                bot_btn = view.children[bot_index]
                bot_btn.label = "⭕"
                bot_btn.disabled = True

                if view.check_winner("⭕"):
                    view.game_over = True
                    view.disable_all()
                    await interaction.response.edit_message(
                        content="🤖 Bot wins! Better luck next time 😈", view=view
                    )
                    return

                if not view.available_moves():
                    view.game_over = True
                    view.disable_all()
                    await interaction.response.edit_message(
                        content="🤝 It's a draw!", view=view
                    )
                    return

                # Switch back to player
                view.current_player = view.player1
                await interaction.response.edit_message(
                    content=f"🎮 Your turn: {view.player1.mention}", view=view
                )
                return

            await interaction.response.edit_message(
                content=f"🎮 Turn: {view.current_player.mention}", view=view
            )


    @bot.tree.command(
        name="tictactoe", description="Play Tic Tac Toe with a user or bot"
    )
    async def tictactoe(interaction: discord.Interaction, opponent: discord.Member):
        if opponent == interaction.user:
            await interaction.response.send_message("😐 You can't play against yourself.", ephemeral=True)
            return

        bot_game = opponent.bot
        view = TicTacToe(player1=interaction.user, player2=opponent, bot_player=bot_game)
        mode = "🤖 Bot" if bot_game else opponent.mention

        await interaction.response.send_message(
            f"🎮 Tic Tac Toe\n❌ {interaction.user.mention} vs ⭕ {mode}\nYour turn!",
            view=view
        )

    # Rolling buffer of recent messages
    message_buffer = []


    # --- Message tracking ---
    def track_message(msg):
        message_buffer.append(msg)
        if len(message_buffer) > MESSAGE_WINDOW:
            message_buffer.pop(0)

    def get_trending_words():
        all_words = []
        for msg in message_buffer:
            words = re.findall(r'\b\w+\b', msg.lower())
            all_words.extend([w for w in words if w not in {"the", "and", "a", "i", "is", "to", "of", "in", "for"}])
        return Counter(all_words).most_common(5)

    def get_trending_emojis():
        emojis = re.findall(r'[\U0001F300-\U0001F6FF\U0001F900-\U0001F9FF]', " ".join(message_buffer))
        return Counter(emojis).most_common(3)

    # --- Text reaction generator ---
    def generate_text_reaction(trending_words, trending_emojis):
        word = trending_words[0][0] if trending_words else "chat"
        emoji = trending_emojis[0][0] if trending_emojis else "😂"
        reactions = [
            f"Whoa! Looks like **{word}** is trending! {emoji * 2}",
            f"I keep seeing **{word}** everywhere! {emoji}",
            f"Server hype detected: **{word}**! {emoji * 3}",
            f"Alert! **{word}** is popular now! Should we make a meme?",
            f"Everyone’s talking about **{word}**! {emoji * 2}",
            f"Hot topic: **{word}**! React with {emoji} if you agree!",
            f"Did someone say **{word}**? That’s everywhere! {emoji * 4}"
        ]
        return random.choice(reactions)

    # --- Meme generator ---
    def generate_meme(top_text, bottom_text):
        try:
            templates = requests.get("https://api.imgflip.com/get_memes").json()['data']['memes']
            template = random.choice(templates)
            payload = {
                "template_id": template['id'],
                "username": IMGFLIP_USER,
                "password": IMGFLIP_PASS,
                "text0": top_text,
                "text1": bottom_text
            }
            resp = requests.post("https://api.imgflip.com/caption_image", data=payload).json()
            if resp['success']:
                return resp['data']['url']
        except:
            return None
        return None

    # --- Discord events ---
    @bot.event
    async def on_message(message):
        global message_count

        if message.author.bot:
            return

        message_count += 1
        track_message(message.content)

        # React every 10 messages (globally)
        if message_count % 10 == 0:
            trending_words = get_trending_words()
            trending_emojis = get_trending_emojis()

            text_reaction = generate_text_reaction(trending_words, trending_emojis)
            await message.channel.send(text_reaction)

            if len(trending_words) > 1:
                meme_url = generate_meme(
                    trending_words[0][0].capitalize(),
                    trending_words[1][0].capitalize()
                )
                if meme_url:
                    await message.channel.send(meme_url)

        await bot.process_commands(message)

    # --- Command to show current trends ---
    @bot.command()
    async def trends(ctx):
        trending_words = get_trending_words()
        trending_emojis = get_trending_emojis()
        embed = discord.Embed(title="Server Trends", color=0x00ff00)
        embed.add_field(name="Words", value=", ".join([w for w, _ in trending_words]) or "No trends yet", inline=False)
        embed.add_field(name="Emojis", value=" ".join([e for e, _ in trending_emojis]) or "No emoji trends yet",
                        inline=False)
        await ctx.send(embed=embed)

    @bot.tree.command(
        name="trend",
        description="Shows trending words and emojis from recent messages"

    )
    async def trend(interaction: discord.Interaction):
        trending_words = get_trending_words()
        trending_emojis = get_trending_emojis()

        embed = discord.Embed(
            title="📈 Server Trends",
            color=0x00ff00
        )

        # Words
        if trending_words:
            embed.add_field(
                name="🔥 Trending Words",
                value=", ".join([f"**{w}**" for w, _ in trending_words]), inline=False)
        else:
            embed.add_field(
                name="🔥 Trending Words",
                value="No trends yet.",
                inline=False
            )

        # Emojis
        if trending_emojis:
            embed.add_field(
                name="😂 Trending Emojis",
                value=" ".join([e for e, _ in trending_emojis]),
                inline=False
            )
        else:
            embed.add_field(
                name="😂 Trending Emojis",
                value="No emoji trends yet.",
                inline=False
            )

        embed.set_footer(text=f"Based on last {MESSAGE_WINDOW} messages")

        await interaction.response.send_message(embed=embed)

    # ---------------- RUSSIAN ROULETTE ----------------
    class RussianRoulette(View):
        def __init__(self, players):
            super().__init__(timeout=120)
            self.players = players
            self.current_index = 0
            self.chambers = [0, 0, 0, 0, 0, 1]
            random.shuffle(self.chambers)
            self.game_over = False

            # Add shoot button
            self.add_item(Button(label="🔫 Pull Trigger", style=discord.ButtonStyle.danger, custom_id="rr_shoot"))

        async def interaction_check(self, interaction: discord.Interaction) -> bool:
            if self.game_over:
                await interaction.response.send_message("The game is over!", ephemeral=True)
                return False
            if interaction.user != self.players[self.current_index]:
                await interaction.response.send_message("It's not your turn!", ephemeral=True)
                return False
            return True

        async def on_timeout(self):
            self.game_over = True
            for item in self.children:
                item.disabled = True

        async def on_button_click(self, interaction: discord.Interaction):
            if self.game_over:
                return

            player = self.players[self.current_index]
            bullet = self.chambers.pop(0)
            await interaction.response.defer()

            # Suspense effect
            await interaction.followup.send(f"{player.mention} is pulling the trigger… 😬")
            await asyncio.sleep(random.uniform(1, 3))

            if bullet == 1:
                await interaction.followup.send(f"💥 **Bang! {player.mention} is out!**")
                self.players.pop(self.current_index)
                if len(self.players) == 1:
                    await interaction.followup.send(f"🏆 {self.players[0].mention} is the winner!")
                    self.game_over = True
                    for item in self.children:
                        item.disabled = True
                    await interaction.message.edit(view=self)
                    return
            else:
                await interaction.followup.send(f"😅 Click… {player.mention} survived!")
                self.current_index = (self.current_index + 1) % len(self.players)

            if not self.chambers:
                self.chambers = [0, 0, 0, 0, 0, 1]
                random.shuffle(self.chambers)

            await interaction.message.edit(view=self)

    rr_games = {}  # channel_id: game

    @bot.tree.command(
        name="russian_roulette",
        description="Start a Russian Roulette game. Players join with the join button."

    )
    async def russian_roulette(interaction: discord.Interaction):
        if interaction.channel.id in rr_games:
            await interaction.response.send_message("A game is already running in this channel!", ephemeral=True)
            return

        players = [interaction.user]

        join_view = View(timeout=30)
        join_button = Button(label="Join Game", style=discord.ButtonStyle.success)

        async def join_callback(btn_interaction: discord.Interaction):
            if btn_interaction.user not in players:
                players.append(btn_interaction.user)
                await btn_interaction.response.send_message(f"{btn_interaction.user.mention} joined!", ephemeral=True)
            else:
                await btn_interaction.response.send_message("You're already in the game!", ephemeral=True)

        join_button.callback = join_callback
        join_view.add_item(join_button)

        await interaction.response.send_message(
            f"🔫 Russian Roulette starting! Click join to participate.\nPlayers: {players[0].mention}",
            view=join_view
        )

        await asyncio.sleep(30)  # wait for players to join

        if len(players) < 2:
            await interaction.followup.send("Not enough players joined. Game cancelled.")
            return

        rr_game = RussianRoulette(players)
        rr_games[interaction.channel.id] = rr_game
        await interaction.followup.send(f"🎲 Game starting with {', '.join([p.mention for p in players])}!", view=rr_game)







    reaction_scores = {}  # user_id: best_time

    class ReactionView(discord.ui.View):
        def __init__(self, user: discord.User):
            super().__init__(timeout=10)
            self.user = user
            self.start_time = None
            self.ready = False

        @discord.ui.button(label="WAIT...", style=discord.ButtonStyle.grey, disabled=True)
        async def click_button(self, interaction: discord.Interaction, button: discord.ui.Button):

            if interaction.user.id != self.user.id:
                await interaction.response.send_message(
                    "❌ This is not your game!", ephemeral=True
                )
                return

            if not self.ready:
                await interaction.response.send_message(
                    "❌ Too early! You clicked before green.", ephemeral=True
                )
                return

            reaction_time = (time.perf_counter() - self.start_time) * 1000
            reaction_time = round(reaction_time, 2)

            button.disabled = True
            button.label = f"{reaction_time} ms"
            button.style = discord.ButtonStyle.green
            self.stop()

            await interaction.response.edit_message(
                content=f"⚡ **Reaction Time:** `{reaction_time} ms`",
                view=self
            )

    @bot.tree.command(name="reaction", description="Test your reaction speed!")
    async def reaction(interaction: discord.Interaction):

        view = ReactionView(interaction.user)

        await interaction.response.send_message(
            "🟡 **Get ready...** Wait for the button to turn green!",
            view=view
        )

        await asyncio.sleep(random.uniform(2, 6))

        view.ready = True
        view.start_time = time.perf_counter()

        for item in view.children:
            item.disabled = False
            item.label = "CLICK!"
            item.style = discord.ButtonStyle.green

        await interaction.edit_original_response(
            content="🟢 **CLICK NOW!**",
            view=view
        )

    # -------- ROCK PAPER SCISSORS --------
    class RockPaperScissorsView(View):
        def __init__(self, user: discord.Member):
            super().__init__(timeout=30)
            self.user = user
            self.choices = {"rock": "🪨", "paper": "📄", "scissors": "✂️"}
            self.user_choice = None
            self.game_over = False

        def get_bot_choice(self):
            return random.choice(["rock", "paper", "scissors"])

        def determine_winner(self, user_choice, bot_choice):
            if user_choice == bot_choice:
                return "tie"
            if (user_choice == "rock" and bot_choice == "scissors") or \
               (user_choice == "paper" and bot_choice == "rock") or \
               (user_choice == "scissors" and bot_choice == "paper"):
                return "win"
            return "lose"

        @discord.ui.button(label="🪨 Rock", style=discord.ButtonStyle.primary)
        async def rock_button(self, interaction: discord.Interaction, button: discord.ui.Button):
            if interaction.user != self.user:
                await interaction.response.send_message("You can't play this game!", ephemeral=True)
                return
            self.user_choice = "rock"
            await self.play_game(interaction)

        @discord.ui.button(label="📄 Paper", style=discord.ButtonStyle.primary)
        async def paper_button(self, interaction: discord.Interaction, button: discord.ui.Button):
            if interaction.user != self.user:
                await interaction.response.send_message("You can't play this game!", ephemeral=True)
                return
            self.user_choice = "paper"
            await self.play_game(interaction)

        @discord.ui.button(label="✂️ Scissors", style=discord.ButtonStyle.primary)
        async def scissors_button(self, interaction: discord.Interaction, button: discord.ui.Button):
            if interaction.user != self.user:
                await interaction.response.send_message("You can't play this game!", ephemeral=True)
                return
            self.user_choice = "scissors"
            await self.play_game(interaction)

        async def play_game(self, interaction: discord.Interaction):
            bot_choice = self.get_bot_choice()
            result = self.determine_winner(self.user_choice, bot_choice)

            # Disable all buttons
            for item in self.children:
                item.disabled = True

            # Create result message
            user_emoji = self.choices[self.user_choice]
            bot_emoji = self.choices[bot_choice]

            if result == "win":
                result_text = f"🎉 **You Win!**\n{user_emoji} **{self.user_choice.upper()}** beats {bot_emoji} **{bot_choice.upper()}**"
                color = discord.Color.green()
            elif result == "lose":
                result_text = f"😔 **You Lose!**\n{user_emoji} **{self.user_choice.upper()}** loses to {bot_emoji} **{bot_choice.upper()}**"
                color = discord.Color.red()
            else:
                result_text = f"🤝 **It's a Tie!**\nBoth chose {user_emoji} **{self.user_choice.upper()}**"
                color = discord.Color.greyple()

            embed = discord.Embed(
                title="🎮 Rock, Paper, Scissors",
                description=result_text,
                color=color
            )
            embed.set_footer(text=f"{interaction.user.name} vs Bot")

            await interaction.response.edit_message(embed=embed, view=self)
            self.stop()

    @bot.tree.command(name="rps", description="Play Rock, Paper, Scissors against the bot")
    async def rock_paper_scissors(interaction: discord.Interaction):
        view = RockPaperScissorsView(interaction.user)

        embed = discord.Embed(
            title="🎮 Rock, Paper, Scissors",
            description="Choose your move!",
            color=discord.Color.blue()
        )
        embed.set_footer(text=f"{interaction.user.name} vs Bot")

        await interaction.response.send_message(embed=embed, view=view)

    @bot.tree.command(name="reaction_leaderboard", description="Fastest reaction times")
    async def reaction_leaderboard(interaction: discord.Interaction):

        if not reaction_scores:
            await interaction.response.send_message("No scores yet!")
            return

        sorted_scores = sorted(reaction_scores.items(), key=lambda x: x[1])[:10]

        leaderboard = ""
        for i, (user_id, score) in enumerate(sorted_scores, start=1):
            user = await bot.fetch_user(user_id)
            leaderboard += f"**{i}.** {user.name} — `{score} ms`\n"

        embed = discord.Embed(
            title="⚡ Reaction Time Leaderboard",
            description=leaderboard,
            color=discord.Color.green()
        )

        await interaction.response.send_message(embed=embed)


