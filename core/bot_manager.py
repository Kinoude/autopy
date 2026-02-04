
import discord
from discord.ext import commands
from discord import app_commands
import asyncio
from core.database import db

active_bots = {}

class ChildBot(commands.Bot):
    def __init__(self, token, user_id, bot_number):
        intents = discord.Intents.default()
        intents.guilds = True 
        super().__init__(command_prefix="!", intents=intents)
        self.user_id = user_id
        self.bot_number = bot_number
        self.token_str = token

    async def on_ready(self):
        print(f"[ChildBot] {self.user.name} ({self.user_id}|{self.bot_number}) is ready!")
        try:
             await self.tree.sync()
        except Exception as e:
             print(f"[ChildBot] Failed to sync commands: {e}")

    async def setup_hook(self):
        # Register /ready command
        @self.tree.command(name="ready", description="Check if bot is ready")
        async def ready(interaction: discord.Interaction):
            await interaction.response.send_message(f"Bot #{self.bot_number} is ready! Logged in as {self.user.name}", ephemeral=True)

async def start_bot(token, user_id, bot_number):
    try:
        bot = ChildBot(token, user_id, bot_number)
        asyncio.create_task(bot.start(token))
        key = f"{user_id}|{bot_number}"
        active_bots[key] = bot
        return bot
    except Exception as e:
        print(f"Failed to start bot {user_id}|{bot_number}: {e}")
        return None

async def stop_bot(user_id, bot_number):
    key = f"{user_id}|{bot_number}"
    if key in active_bots:
        bot = active_bots[key]
        await bot.close()
        del active_bots[key]
        return True
    return False

async def restore_bots():
    print("[BotManager] Restoring bots from database...")
    rows = await db.query("SELECT * FROM autosecure")
    count = 0
    if rows:
        for row in rows:
            token = row['token']
            if token:
                await start_bot(token, row['user_id'], row['botnumber'])
                count += 1
    print(f"[BotManager] Restored {count} bots.")
