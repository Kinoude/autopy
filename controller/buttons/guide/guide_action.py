
import discord
import os

async def handle_guide_action(interaction, action):
    try:
        if action == 'starting_bot':
            await interaction.response.send_message("David's guide: https://www.youtube.com/watch?v=r5kNwO-Ta8w", ephemeral=True)
        elif action == 'securing':
            await interaction.response.send_message("Run /secure to start.", ephemeral=True)
        elif action == 'ssidhelp':
            # Path to SchubiAuthV2.jar
            file_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "files", "SchubiAuthV2.jar")
            files = []
            if os.path.exists(file_path):
                files.append(discord.File(file_path, filename="SchubiAuthV2.jar"))
            await interaction.response.send_message("Use the jar below.", files=files, ephemeral=True)
        # ... (rest of simple messages)
        else:
             await interaction.response.send_message(f"Guide: {action}", ephemeral=True)
             
    except Exception as e:
        await interaction.response.send_message(f"Error: {e}", ephemeral=True)

async def handler(interaction):
    custom_id = interaction.data.get('custom_id', '')
    if '|' in custom_id:
        action = custom_id.split('|')[1]
        await handle_guide_action(interaction, action)

custom_id = "guide_action"
