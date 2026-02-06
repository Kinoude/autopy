
import discord
from controller.utils.bot.showbotmsg import show_bot_msg
from controller.utils.bot.createbotmsg import create_bot_msg

custom_id = "managebots"

async def handler(interaction):
    # Select Menu interaction
    selected = interaction.data['values'][0]
    parts = selected.split("|")
    action = parts[0]
    user_id = parts[1]
    
    if action == "bot":
        # Switch to that bot
        bot_number = parts[2]
        msg = await show_bot_msg(user_id, bot_number, user_id)
        if interaction.response.is_done():
             await interaction.followup.send(**msg)
        else:
             await interaction.response.send_message(**msg)
             
    elif action == "newbot":
        # Show Modal to create new bot
        bot_number = parts[2]
        
        # Define modal dynamically or use a class that sends back custom_id matching our newbot handler
        class NewBotModal(discord.ui.Modal, title=f"Set Token for Bot #{bot_number}"):
            token = discord.ui.TextInput(
                label="New bot's token",
                placeholder="Enter token from Discord Developer Portal.",
                min_length=0,
                max_length=256,
                required=True,
                custom_id="token"
            )
            
            async def on_submit(self, i: discord.Interaction):
                 pass # handled by modal handler via custom_id
        
        modal = NewBotModal()
        # Important: this ID matches what newbot.py expects
        modal.custom_id = f"handlenewbot|{user_id}|{bot_number}"
        
        await interaction.response.send_modal(modal)
        
    elif action == "purchaseslot":
        await interaction.response.send_message("Please use the link button to purchase slots.", ephemeral=True)
        
    elif action == "none":
        await interaction.response.send_message("No action selected.", ephemeral=True)
