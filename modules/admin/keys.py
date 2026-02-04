
import discord
from discord.ext import commands
from discord import app_commands
import random
import string
import time
from core.database import db
from core.permissions import permissions

class AdminKeys(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def generate_key_string(self, length=16):
        return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

    @app_commands.command(name="create-key", description="Create license keys")
    @app_commands.describe(amount="Number of keys to create", duration="Duration in days (default 30)")
    async def create_key(self, interaction: discord.Interaction, amount: int = 1, duration: int = 30):
        # 1. Permission Check
        if not await permissions.is_owner(interaction.user.id):
            return await interaction.response.send_message("You are not an owner!", ephemeral=True)
            
        await interaction.response.defer(ephemeral=True)
        
        created_keys = []
        
        for _ in range(amount):
            key = f"ASRA-{self.generate_key_string()}"
            duration_text = f"{duration}d"
            
            await db.query("INSERT INTO licenses (license, duration) VALUES (?, ?)", [key, duration_text])
            created_keys.append(key)
            
        keys_text = "\n".join(f"`{k}`" for k in created_keys)
        embed = discord.Embed(title="Keys Created", description=keys_text, color=0x00ff00)
        embed.set_footer(text=f"Duration: {duration} days")
        
        await interaction.followup.send(embeds=[embed])

    @app_commands.command(name="delete-key", description="Delete a license key")
    async def delete_key(self, interaction: discord.Interaction, key: str):
        if not await permissions.is_owner(interaction.user.id):
            return await interaction.response.send_message("You are not an owner!", ephemeral=True)
            
        await db.query("DELETE FROM licenses WHERE license = ?", [key])
        await interaction.response.send_message(f"Deleted key `{key}`", ephemeral=True)

    @app_commands.command(name="view-keys", description="View all unused keys")
    async def view_keys(self, interaction: discord.Interaction):
         if not await permissions.is_owner(interaction.user.id):
            return await interaction.response.send_message("You are not an owner!", ephemeral=True)
            
         rows = await db.query("SELECT * FROM licenses")
         
         if not rows:
             return await interaction.response.send_message("No unused keys found.", ephemeral=True)
             
         desc = "\n".join(f"`{row['license']}` ({row['duration']})" for row in rows[:50])
         if len(rows) > 50:
             desc += f"\n...and {len(rows)-50} more."
             
         embed = discord.Embed(title="Unused Keys", description=desc, color=0x00aa00)
         await interaction.response.send_message(embeds=[embed], ephemeral=True)

async def setup(bot):
    await bot.add_cog(AdminKeys(bot))
