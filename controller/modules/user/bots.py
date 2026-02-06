
import discord
from discord.ext import commands
from discord import app_commands
from core.database import db

class UserBots(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="bots", description="Manage your bots")
    async def bots(self, interaction: discord.Interaction):
        user_id = str(interaction.user.id)
        
        # Use create_bot_msg logic which handles lists/creation/slots
        from controller.utils.bot.createbotmsg import create_bot_msg
        
        msg = await create_bot_msg(self.bot, user_id)
        
        if interaction.response.is_done():
            await interaction.followup.send(**msg)
        else:
            await interaction.response.send_message(**msg)

async def setup(bot):
    await bot.add_cog(UserBots(bot))
