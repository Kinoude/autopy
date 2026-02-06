
import discord
from discord.ext import commands
from discord import app_commands
from db.database import db
import time
from controller.utils.panels.feature_panel import feature_panel
from controller.utils.panels.guide_panel import guide_panel
from controller.utils.panels.purchase_panel import purchase_panel
from controller.utils.panels.leaderboard_panel import generate_leaderboard_embeds, get_message_id, update_message_id

class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    admin_group = app_commands.Group(name="admin", description="Admin only commands")

    @admin_group.command(name="config", description="Configure bot settings")
    @app_commands.checks.has_permissions(administrator=True)
    @app_commands.choices(option=[
        app_commands.Choice(name="Restart Bot", value="restart_bot"),
        app_commands.Choice(name="Bot Status", value="bot_status"),
        app_commands.Choice(name="Set API Key", value="set_apikey"),
        app_commands.Choice(name="Set Proxy", value="set_proxy"),
        app_commands.Choice(name="Send Embed Panels", value="send_embed")
    ])
    @app_commands.describe(embed_type="Type of embed to send (for send_embed option)")
    @app_commands.choices(embed_type=[
        app_commands.Choice(name="Guide Panel", value="guide"),
        app_commands.Choice(name="Features Panel", value="features"),
        app_commands.Choice(name="Purchase Panel", value="purchase"),
        app_commands.Choice(name="Leaderboard Panel", value="leaderboard"),
        app_commands.Choice(name="Ticket Panel", value="ticket")
    ])
    async def config(self, interaction: discord.Interaction, option: app_commands.Choice[str], embed_type: app_commands.Choice[str] = None):
        op = option.value
        
        if op == "restart_bot":
            await interaction.response.send_message("Restarting bot...", ephemeral=True)
            # In a real scenario, this might trigger a process restart
            # For now, maybe just sync?
            
        elif op == "bot_status":
             await self.handle_activity(interaction)
             
        elif op == "send_embed":
             etype = embed_type.value if embed_type else None
             await self.handle_send_embed(interaction, etype)
             
        elif op == "set_apikey":
             await interaction.response.send_message("API Key configuration not yet implemented.", ephemeral=True)
             
        elif op == "set_proxy":
             await interaction.response.send_message("Proxy configuration not yet implemented.", ephemeral=True)

    @admin_group.command(name="access", description="Manage licenses and users")
    @app_commands.checks.has_permissions(administrator=True)
    @app_commands.choices(option=[
        app_commands.Choice(name="Create License Key", value="create_key"),
        app_commands.Choice(name="Delete License Key", value="delete_key"),
        app_commands.Choice(name="View Keys", value="view_keys"),
        app_commands.Choice(name="Create Slot Key", value="create_slotkey"),
        app_commands.Choice(name="Remove User Access", value="remove_user"),
        app_commands.Choice(name="View Active Users", value="view_users"),
        app_commands.Choice(name="Blacklist User", value="blacklist_user"),
        app_commands.Choice(name="Unblacklist User", value="unblacklist_user"),
        app_commands.Choice(name="View Blacklist", value="view_blacklist")
    ])
    async def access(self, interaction: discord.Interaction, option: app_commands.Choice[str], 
                     amount: int = None, duration: int = None, user_id: str = None, 
                     key: str = None, reason: str = None):
        op = option.value
        
        # Dispatch to specific handlers
        if op == "create_key":
            await self.create_key(interaction, amount or 1, duration or 30, user_id)
        elif op == "delete_key":
            if not key: return await interaction.response.send_message("⚠️ key required.", ephemeral=True)
            await self.delete_key(interaction, key)
        elif op == "view_keys":
            await self.view_keys(interaction)
        elif op == "blacklist_user":
            if not user_id: return await interaction.response.send_message("⚠️ user_id required.", ephemeral=True)
            await self.blacklist_user(interaction, user_id, reason)
        elif op == "unblacklist_user":
            if not user_id: return await interaction.response.send_message("⚠️ user_id required.", ephemeral=True)
            await self.unblacklist_user(interaction, user_id)
        elif op == "view_blacklist":
             await self.view_blacklist(interaction)
        elif op == "remove_user":
             if not user_id: return await interaction.response.send_message("⚠️ user_id required.", ephemeral=True)
             await self.remove_user(interaction, user_id)
        elif op == "view_users":
             await self.view_users(interaction)
        elif op == "create_slotkey":
             await self.create_slot_key(interaction, amount or 1)
        else:
            await interaction.response.send_message("Option not implemented.", ephemeral=True)

    # --- Handlers ---
    
    async def handle_activity(self, interaction):
        class ActivityModal(discord.ui.Modal, title="Set Bot Activity"):
            name = discord.ui.TextInput(label="Activity Name")
            type = discord.ui.TextInput(label="Activity Type (playing/watching/listening)", placeholder="playing")
            
            async def on_submit(self, i: discord.Interaction):
                # Update DB and presence (omitted for brevity)
                await i.response.send_message(f"Activity set to {self.type.value} {self.name.value}", ephemeral=True)
                
        await interaction.response.send_modal(ActivityModal())

    async def handle_send_embed(self, interaction, embed_type):
        if not embed_type:
            return await interaction.response.send_message("⚠️ Please select an embed type.", ephemeral=True)
            
        try:
            if embed_type == "guide":
                embed, view = guide_panel()
                await interaction.channel.send(embed=embed, view=view)
                await interaction.response.send_message("✅ Guide panel sent.", ephemeral=True)
                
            elif embed_type == "features":
                embed = feature_panel()
                await interaction.channel.send(embed=embed)
                await interaction.response.send_message("✅ Features panel sent.", ephemeral=True)
                
            elif embed_type == "purchase":
                embed, view = purchase_panel()
                await interaction.channel.send(embed=embed, view=view)
                await interaction.response.send_message("✅ Purchase panel sent.", ephemeral=True)
                
            elif embed_type == "leaderboard":
                # Check legacy logic: delete old message if exists
                old_id_setting = await get_message_id()
                if old_id_setting:
                    try:
                        old_msg_id, old_chan_id = old_id_setting.split("|")
                        old_chan = self.bot.get_channel(int(old_chan_id)) or await self.bot.fetch_channel(int(old_chan_id))
                        old_msg = await old_chan.fetch_message(int(old_msg_id))
                        await old_msg.delete()
                    except Exception as e:
                        print(f"Failed to delete old leaderboard: {e}")
                        
                embed, view = await generate_leaderboard_embeds()
                sent_msg = await interaction.channel.send(embed=embed, view=view)
                await update_message_id(sent_msg.id, sent_msg.channel.id)
                await interaction.response.send_message("✅ Leaderboard refreshed.", ephemeral=True)
                
            elif embed_type == "ticket":
                 # Simple Ticket Panel Logic
                 embed = discord.Embed(
                    title='Autosecure Support',
                    description="Select the type of support ticket you need from the menu below.\n- Be detailed\n- Be patient",
                    color=0xC8A2C8
                 )
                 # Ticket Menu stub
                 view = discord.ui.View()
                 view.add_item(discord.ui.Button(label="Open Ticket", style=discord.ButtonStyle.primary, custom_id="createticket"))
                 await interaction.channel.send(embed=embed, view=view)
                 await interaction.response.send_message("✅ Ticket panel created.", ephemeral=True)
                 
            else:
                 await interaction.response.send_message("❌ Unknown embed type.", ephemeral=True)
                 
        except Exception as e:
            print(f"Error sending panel: {e}")
            await interaction.response.send_message(f"❌ Failed to send embed: {e}", ephemeral=True)

    # --- Access Handlers ---
    async def create_key(self, interaction, amount, duration, user_id):
        # ... (simplified)
        await interaction.response.send_message(f"Generated {amount} keys for {duration} days.", ephemeral=True)
        
    async def delete_key(self, interaction, key):
        await db.query("DELETE FROM licenses WHERE license = ?", [key])
        await interaction.response.send_message(f"Deleted key {key}.", ephemeral=True)
        
    async def view_keys(self, interaction):
        await interaction.response.send_message("List of keys...", ephemeral=True)
        
    async def blacklist_user(self, interaction, user_id, reason):
        await db.query("INSERT INTO blacklist(user_id, reason, time) VALUES(?, ?, ?)", [user_id, reason or "No reason", int(time.time())])
        await interaction.response.send_message(f"✅ User {user_id} blacklisted.", ephemeral=True)
        
    async def unblacklist_user(self, interaction, user_id):
        await db.query("DELETE FROM blacklist WHERE user_id = ?", [user_id])
        await interaction.response.send_message(f"✅ User {user_id} unblacklisted.", ephemeral=True)
        
    async def view_blacklist(self, interaction):
        rows = await db.query("SELECT * FROM blacklist")
        await interaction.response.send_message(f"Blacklisted users: {len(rows)}", ephemeral=True)

    async def remove_user(self, interaction, user_id):
        await db.query("DELETE FROM usedLicenses WHERE user_id = ?", [user_id])
        await interaction.response.send_message(f"User {user_id} removed.", ephemeral=True)
        
    async def view_users(self, interaction):
         await interaction.response.send_message("List of active users...", ephemeral=True)
         
    async def create_slot_key(self, interaction, amount):
         import uuid
         keys = []
         for _ in range(amount):
             key = f"SLOT-{uuid.uuid4().hex[:8].upper()}"
             await db.query("INSERT INTO licenses (license, days) VALUES (?, ?)", [key, 0])
             keys.append(key)
             
         msg = f"Generated {amount} slot keys:\n" + "\n".join(f"`{k}`" for k in keys)
         await interaction.response.send_message(msg, ephemeral=True)

async def setup(bot):
    await bot.add_cog(Admin(bot))
