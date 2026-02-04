
import discord
from discord.ext import commands
import asyncio
import json
import os
import sys

# Ensure correct path for imports
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(BASE_DIR)

from core.database import db
from core.bot_manager import restore_bots

# Load Config
def load_config():
    # Helper to find config from CleanBot root
    path = os.path.join(BASE_DIR, "config.json")
    with open(path, "r") as f:
        return json.load(f)

config = load_config()
TOKEN = config["tokens"][0]

class ControllerBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.guilds = True
        intents.message_content = True
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        print("[Controller] Loading modules...")
        
        # Load extensions using dot notation relative to where this script is run
        # if running python CleanBot/main.py, we might need adjustments.
        # But since we added BASE_DIR to sys.path, we can import 'modules.xyz' directly if 'modules' is package.
        # 'modules' directory needs __init__.py? No, typically not in Python 3.
        
        await self.load_extension("modules.admin.keys")
        await self.load_extension("modules.user.redeem")
        await self.load_extension("modules.user.bots")
        await self.load_extension("modules.admin.slots")
        await self.load_extension("modules.user.email")
        
        await self.tree.sync()
        print("[Controller] Commands synced.")
        
        await restore_bots()

    async def on_ready(self):
        print(f"[Controller] Logged in as {self.user.name} ({self.user.id})")
        print("[Controller] System Ready. Use /create-key, /redeem, /bots")

async def main():
    bot = ControllerBot()
    async with bot:
        await bot.start(TOKEN)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Shutdown.")
