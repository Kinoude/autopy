
import discord
from discord.ext import commands
from discord import app_commands
from core.database import db
import time

class Redeem(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="redeem", description="Redeem a license key")
    @app_commands.describe(key="The license key to redeem")
    async def redeem(self, interaction: discord.Interaction, key: str):
        await interaction.response.defer(ephemeral=True)
        
        # Check if key exists
        license_data = await db.query("SELECT * FROM licenses WHERE license = ?", [key])
        
        if not license_data:
            return await interaction.followup.send("❌ Invalid license key.", ephemeral=True)
            
        # Check if Slot Key
        if key.startswith("SLOT-"):
             # Handle slot
             current_slots_res = await db.query("SELECT slots FROM slots WHERE user_id = ?", [user_id])
             if current_slots_res:
                 new_slots = current_slots_res[0]['slots'] + 1
                 await db.query("UPDATE slots SET slots = ? WHERE user_id = ?", [new_slots, user_id])
             else:
                 # Default was 1, so now 2? Or they had 0?
                 # If they are redeeming a slot key, they likely want MORE than 1.
                 # But if they have no entry, they default to 1 in createbotmsg.
                 # So if we insert 2, they get 2.
                 await db.query("INSERT INTO slots (user_id, slots) VALUES (?, ?)", [user_id, 2])
                 
             msg = "✅ Extra Bot Slot redeemed! You can now create an additional bot."
        else:
            # License Key
            license_info = license_data[0]
            days = license_info['days']
            
            current_time = int(time.time() * 1000)
            duration_ms = days * 24 * 60 * 60 * 1000
            expiry = current_time + duration_ms
            
            # Check existing
            existing = await db.query("SELECT * FROM usedLicenses WHERE user_id = ?", [user_id])
            if existing:
                # Extend
                old_expiry = int(existing[0]['expiry'])
                if old_expiry > current_time:
                    new_expiry = old_expiry + duration_ms
                else:
                    new_expiry = current_time + duration_ms
                    
                await db.query("UPDATE usedLicenses SET expiry = ? WHERE user_id = ?", [new_expiry, user_id])
                msg = f"✅ License extended! Added {days} days."
            else:
                # New
                await db.query("INSERT INTO usedLicenses (user_id, expiry) VALUES (?, ?)", [user_id, expiry])
                msg = f"✅ License redeemed! Valid for {days} days."
            
        # Delete used key
        await db.query("DELETE FROM licenses WHERE license = ?", [key])
        
        # Add Setup Button
        view = discord.ui.View()
        view.add_item(discord.ui.Button(label="🚀 Create/Manage Bots", style=discord.ButtonStyle.success, command=self.bot.tree.get_command("bots")))
        # Note: Buttons can't directly trigger commands like that easily without a handler or link.
        # Better: just tell them. Or utilize a link to the channel?
        # Actually, "managed bots" command is just a slash command. We can't deep-link to slash commands easily unless we use </bots:id>.
        # We can find the command ID if synced.
        
        # Try to find command ID
        bots_cmd = next((cmd for cmd in self.bot.tree.get_commands() if cmd.name == "bots"), None)
        if bots_cmd:
             # This ID might not be available until sync?
             # Just use text instruction.
             msg += "\n\n👉 Run `/bots` to get started!"
        
        await interaction.followup.send(msg, ephemeral=True)

async def setup(bot):
    await bot.add_cog(Redeem(bot))
