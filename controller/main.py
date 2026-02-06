
import discord
from discord.ext import commands
import os
import asyncio
from core.bot_manager import restore_bots
from db.database import db

class ControllerBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True  # If needed
        super().__init__(command_prefix="!", intents=intents, help_command=None)
        
    async def setup_hook(self):
        # Initialize Database
        await db.initialize()
        
        # Load button handlers
        from controller.handlers.button_handler import button_handler
        await button_handler.load_buttons(self)
        self.button_handler = button_handler

        # Load modal handlers
        from controller.handlers.modal_handler import modal_handler
        await modal_handler.load_modals(self)
        self.modal_handler = modal_handler
        
        # Load Extensions
        # Removed slots/keys as they are merged into admin
        items = [
            "controller.modules.admin.admin",
            "controller.modules.user.bots",
            "controller.modules.user.redeem",
            "controller.tasks.leaderboard_updater"
        ]
        
        for ext in items:
            try:
                await self.load_extension(ext)
                print(f"[Controller] Loaded {ext}")
            except Exception as e:
                print(f"[Controller] Failed to load {ext}: {e}")
        
        # Sync Command Tree
        await self.tree.sync()
        print("[Controller] Commands synced.")
        
        # Restore Child Bots
        await restore_bots()
    
    async def on_interaction(self, interaction):
        """Handle button/select/modal interactions"""
        if interaction.type == discord.InteractionType.component:
            await self.button_handler.handle_interaction(interaction)
        elif interaction.type == discord.InteractionType.modal_submit:
            await self.modal_handler.handle_interaction(interaction)

    async def on_ready(self):
        print(f"[Controller] Logged in as {self.user.name} ({self.user.id})")
        
# Entry point if run directly
if __name__ == "__main__":
    pass
