
import discord
from core.database import db
from core.bot_manager import start_bot
import time

custom_id = "handlenewbot"

async def handler(interaction):
    # handlenewbot|userid|botnumber
    custom_id_str = interaction.data.get('custom_id', '')
    parts = custom_id_str.split("|")
    
    if len(parts) < 3:
        return await interaction.response.send_message("❌ Invalid interaction data.", ephemeral=True)
        
    user_id = parts[1]
    bot_number = parts[2]
    
    # Get inputs manually from interaction.data
    token = None
    components = interaction.data.get('components', [])
    
    for row in components:
        for component in row.get('components', []):
            if component.get('custom_id') == 'token':
                token = component.get('value')
                break
        if token: break
    
    if not token:
        return await interaction.response.send_message("❌ Token is required!", ephemeral=True)
        
    await interaction.response.defer(ephemeral=True)
    
    try:
        exists = await db.query("SELECT 1 FROM autosecure WHERE user_id = ? AND botnumber = ?", [user_id, bot_number])
        
        if exists:
            await db.query("UPDATE autosecure SET token = ? WHERE user_id = ? AND botnumber = ?", [token, user_id, bot_number])
        else:
            await db.query(
                "INSERT INTO autosecure (user_id, botnumber, token, creationdate) VALUES (?, ?, ?, ?)",
                [user_id, bot_number, token, int(time.time())]
            )
            
        started = await start_bot(user_id, bot_number, token)
        
        if started:
            await interaction.followup.send(f"✅ Bot #{bot_number} created and started!", ephemeral=True)
        else:
            await interaction.followup.send(f"⚠️ Bot #{bot_number} saved but failed to start (check token).", ephemeral=True)
            
    except Exception as e:
        print(f"Error creating bot: {e}")
        try:
            await interaction.followup.send(f"❌ Error creating bot: {e}", ephemeral=True)
        except: pass
