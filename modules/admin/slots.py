
import discord
from discord import app_commands
from discord.ext import commands
from core.database import db
from core.permissions import permissions

class AdminSlots(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def is_owner_check(self, interaction: discord.Interaction):
        return permissions.is_owner(interaction.user.id)

    @app_commands.command(name="add-slots", description="Add slots to a user")
    async def add_slots(self, interaction: discord.Interaction, user_id: str, amount: int):
        if not await permissions.is_owner(interaction.user.id):
             return await interaction.response.send_message("Not authorized.", ephemeral=True)
             
        # Check if user exists in slots table
        existing = await db.query("SELECT slots FROM slots WHERE user_id = ?", [user_id], "get")
        
        if existing:
            new_amount = existing['slots'] + amount
            await db.query("UPDATE slots SET slots = ? WHERE user_id = ?", [new_amount, user_id])
        else:
            new_amount = amount
            await db.query("INSERT INTO slots (user_id, slots) VALUES (?, ?)", [user_id, amount])
            
        await interaction.response.send_message(f"Added {amount} slots to <@{user_id}>. Total: {new_amount}", ephemeral=True)

    @app_commands.command(name="remove-slots", description="Remove slots from a user")
    async def remove_slots(self, interaction: discord.Interaction, user_id: str, amount: int):
        if not await permissions.is_owner(interaction.user.id):
             return await interaction.response.send_message("Not authorized.", ephemeral=True)

        existing = await db.query("SELECT slots FROM slots WHERE user_id = ?", [user_id], "get")
        
        if not existing:
             return await interaction.response.send_message("User has no slots.", ephemeral=True)
             
        current = existing['slots']
        new_amount = max(0, current - amount)
        
        await db.query("UPDATE slots SET slots = ? WHERE user_id = ?", [new_amount, user_id])
        await interaction.response.send_message(f"Removed {amount} slots from <@{user_id}>. Total: {new_amount}", ephemeral=True)

    @app_commands.command(name="user-info", description="View user slots and active bots")
    async def user_info(self, interaction: discord.Interaction, user_id: str):
        if not await permissions.is_owner(interaction.user.id):
             return await interaction.response.send_message("Not authorized.", ephemeral=True)

        # Get Slots
        slots_data = await db.query("SELECT slots FROM slots WHERE user_id = ?", [user_id], "get")
        slots = slots_data['slots'] if slots_data else 0
        
        # Get Active Bots
        bots = await db.query("SELECT * FROM autosecure WHERE user_id = ?", [user_id])
        bot_count = len(bots)
        
        embed = discord.Embed(title=f"Info for User {user_id}", color=0x00aaff)
        embed.add_field(name="Slots", value=str(slots))
        embed.add_field(name="Active Bots", value=str(bot_count))
        
        if bots:
            bot_list = "\n".join([f"#{b['botnumber']}: <@{b['token'].split('.')[0]}>" for b in bots[:10]]) # Token hint
            embed.description = f"**Bots:**\n{bot_list}"
            
        await interaction.response.send_message(embeds=[embed], ephemeral=True)

async def setup(bot):
    await bot.add_cog(AdminSlots(bot))
