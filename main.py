
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
        intents.members = True
        super().__init__(command_prefix="!", intents=intents, help_command=None)

    async def setup_hook(self):
        print("[Controller] Loading handlers...")
        # Load button handlers
        from controller.handlers.button_handler import button_handler
        await button_handler.load_buttons(self)
        self.button_handler = button_handler

        # Load modal handlers
        from controller.handlers.modal_handler import modal_handler
        await modal_handler.load_modals(self)
        self.modal_handler = modal_handler
        
        print("[Controller] Loading modules...")
        # Load Extensions
        extensions = [
            "controller.modules.admin.admin",
            "controller.modules.user.bots",
            "controller.modules.user.redeem",
            "controller.tasks.leaderboard_updater"
        ]
        
        for ext in extensions:
            try:
                await self.load_extension(ext)
                print(f"[Controller] ✓ Loaded {ext}")
            except Exception as e:
                print(f"[Controller] ✗ Failed to load {ext}: {e}")
                import traceback
                traceback.print_exc()
        
        print("[Controller] Syncing commands...")
        await self.tree.sync()
        print("[Controller] Commands synced.")
        
        print("[BotManager] Restoring bots from database...")
        await restore_bots()
    
    async def on_interaction(self, interaction):
        """Handle button/select/modal interactions"""
        if interaction.type == discord.InteractionType.component:
            await self.button_handler.handle_interaction(interaction)
        elif interaction.type == discord.InteractionType.modal_submit:
            await self.modal_handler.handle_interaction(interaction)

    async def on_ready(self):
        print(f"[Controller] Logged in as {self.user.name} ({self.user.id})")
        print(f"[Controller] Ready! Bot is online and listening for commands.")

async def main():
    bot = ControllerBot()
    async with bot:
        await bot.start(TOKEN)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n[Controller] Shutdown requested.")
    except Exception as e:
        print(f"\n[Controller] Fatal error: {e}")
        import traceback
        traceback.print_exc()
