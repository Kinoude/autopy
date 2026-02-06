
import discord
from core.database import db

async def check_hidden(user_id):
    entry = await db.query("SELECT showleaderboard FROM settings WHERE user_id = ?", [user_id])
    if not entry: return False
    val = entry[0]['showleaderboard']
    return val == 0 or val == '0'

async def get_message_id():
    try:
        data = await db.query("SELECT leaderboardid FROM controlbot WHERE id = 1")
        if data: return data[0]['leaderboardid']
        return None
    except: return None

async def update_message_id(msg_id, channel_id):
    setting = f"{msg_id}|{channel_id}"
    existing = await db.query("SELECT * FROM controlbot WHERE id = 1")
    if existing:
        await db.query("UPDATE controlbot SET leaderboardid = ? WHERE id = 1", [setting])
    else:
        await db.query("INSERT INTO controlbot (id, leaderboardid) VALUES (?, ?)", [1, setting])

async def generate_leaderboard_embeds():
    try:
        count_leaderboard = await db.query("SELECT user_id, amount FROM leaderboard ORDER BY amount DESC LIMIT 10")
        
        count_text = ""
        for i, entry in enumerate(count_leaderboard):
            user_id = entry['user_id']
            amount = entry['amount']
            hidden = await check_hidden(user_id)
            user_tag = "`Hidden user`" if hidden else f"<@{user_id}>"
            count_text += f"**{i + 1}** | {user_tag} has autosecured `{amount:,}` accounts\n"
            
        if not count_text: count_text = "No entries yet."

        embed = discord.Embed(title="Autosecure Leaderboard", color=0x00FF00)
        embed.description = "## **Autosecure Leaderboard**\n" + count_text
        
        view = discord.ui.View(timeout=None)
        view.add_item(discord.ui.Button(label="Hide me", style=discord.ButtonStyle.secondary, custom_id="hideleaderboard"))
        
        return embed, view
        
    except Exception as e:
        print(f"Error generating leaderboard: {e}")
        return discord.Embed(description="❌ Failed to generate leaderboard"), None
