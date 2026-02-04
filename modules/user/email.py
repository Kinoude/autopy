
import discord
from discord.ext import commands
from discord import app_commands
from core.email_handler import email_handler
from core.permissions import permissions

class UserEmail(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    group = app_commands.Group(name="mail", description="Manage your emails")

    @group.command(name="register", description="Register a new email")
    async def register(self, interaction: discord.Interaction, email: str):
        await interaction.response.defer(ephemeral=True)
        
        user_id = str(interaction.user.id)
        success, msg = await email_handler.register_email(user_id, email)
        
        color = 0x00ff00 if success else 0xff0000
        embed = discord.Embed(description=msg, color=color)
        await interaction.followup.send(embeds=[embed], ephemeral=True)

    @group.command(name="list", description="List your registered emails")
    async def list_emails(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        
        user_id = str(interaction.user.id)
        emails = await email_handler.get_user_emails(user_id)
        
        if not emails:
            return await interaction.followup.send("You have no registered emails.", ephemeral=True)
            
        desc = "\n".join([f"• `{e}`" for e in emails])
        embed = discord.Embed(title="Your Emails", description=desc, color=0x00aaff)
        await interaction.followup.send(embeds=[embed], ephemeral=True)

    @group.command(name="inbox", description="Check email inbox")
    async def inbox(self, interaction: discord.Interaction, email: str):
        await interaction.response.defer(ephemeral=True)
        
        user_id = str(interaction.user.id)
        is_owner = await permissions.is_owner(user_id)
        
        success, result = await email_handler.get_inbox(email, user_id, is_owner)
        
        if not success:
             # result is validation error message
             return await interaction.followup.send(result, ephemeral=True)
             
        # result is list of messages
        messages = result
        
        if not messages:
            embed = discord.Embed(title=f"Inbox: {email}", description="📭 No emails found.", color=0xcccccc)
            await interaction.followup.send(embeds=[embed], ephemeral=True)
            return
            
        # Display latest 5
        embed = discord.Embed(title=f"Inbox: {email}", color=0x00aaff)
        for msg in messages[:5]:
            subject = msg.get('subject', 'No Subject')
            content = msg.get('content', '...')[:100] # Truncate
            embed.add_field(name=subject, value=content, inline=False)
            
        await interaction.followup.send(embeds=[embed], ephemeral=True)

async def setup(bot):
    await bot.add_cog(UserEmail(bot))
