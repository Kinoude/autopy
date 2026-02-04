
import discord
from discord.ext import commands
from discord import app_commands
import time
from core.database import db
from core.permissions import permissions

class UserRedeem(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="redeem", description="Redeem a license key")
    async def redeem(self, interaction: discord.Interaction, key: str):
        await interaction.response.defer(ephemeral=True)
        
        # 1. Check if key exists in licenses
        key_data = await db.query("SELECT * FROM licenses WHERE license = ?", [key], "get")
        
        if not key_data:
             return await interaction.followup.send("Invalid key!", ephemeral=True)
             
        # 2. Parse duration
        duration_str = key_data['duration']
        days = int(duration_str.replace("d", ""))
        duration_ms = days * 24 * 60 * 60 * 1000
        
        user_id = str(interaction.user.id)
        current_ms = int(time.time() * 1000)
        new_expiry = current_ms + duration_ms
        
        # 3. Check if user already has a license
        existing = await db.query("SELECT * FROM usedLicenses WHERE user_id = ?", [user_id], "get")
        
        if existing:
            # Extend duration
            current_expiry = int(existing['expiry'])
            if current_expiry > current_ms:
                new_expiry = current_expiry + duration_ms
            else:
                new_expiry = current_ms + duration_ms
                
            await db.query("UPDATE usedLicenses SET expiry = ? WHERE user_id = ?", [new_expiry, user_id])
            msg = f"Extended your license by {days} days!"
        else:
            # Create new license entry
            await db.query("INSERT INTO usedLicenses (license, user_id, expiry) VALUES (?, ?, ?)", [key, user_id, new_expiry])
            
            # Also give 1 slot if they have none
            slots = await db.query("SELECT slots FROM slots WHERE user_id = ?", [user_id], "get")
            if not slots:
                 await db.query("INSERT INTO slots (user_id, slots) VALUES (?, ?)", [user_id, 1])
            
            msg = f"Redeemed license for {days} days! You now have access."

        # 4. Consume key
        await db.query("DELETE FROM licenses WHERE license = ?", [key])
        
        embed = discord.Embed(title="Success!", description=msg, color=0x00ff00)
        embed.set_footer(text=f"Expires: <t:{int(new_expiry/1000)}:R>")
        await interaction.followup.send(embeds=[embed], ephemeral=True)

    @app_commands.command(name="license", description="Check your license status")
    async def license(self, interaction: discord.Interaction):
        user_id = str(interaction.user.id)
        
        # Check Owner
        if await permissions.is_owner(user_id):
             return await interaction.response.send_message("You are an Owner (Lifetime Access)", ephemeral=True)

        license_data = await db.query("SELECT * FROM usedLicenses WHERE user_id = ?", [user_id], "get")
        
        if not license_data:
             return await interaction.response.send_message("You do not have an active license.", ephemeral=True)
             
        expiry = int(license_data['expiry'])
        current_ms = int(time.time() * 1000)
        
        if expiry < current_ms:
             return await interaction.response.send_message("Your license has expired.", ephemeral=True)
             
        slots_data = await db.query("SELECT slots FROM slots WHERE user_id = ?", [user_id], "get")
        slots = slots_data['slots'] if slots_data else 0
        
        embed = discord.Embed(title="License Status", color=0x00aaff)
        embed.add_field(name="Status", value="Active ✅")
        embed.add_field(name="Expires", value=f"<t:{int(expiry/1000)}:R>")
        embed.add_field(name="Slots", value=str(slots))
        
        await interaction.response.send_message(embeds=[embed], ephemeral=True)

async def setup(bot):
    await bot.add_cog(UserRedeem(bot))
