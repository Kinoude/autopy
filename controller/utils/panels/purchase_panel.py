
import discord

def purchase_panel():
    embed = discord.Embed(
        description="\n - **Phisher & Autosecure license** - Most trusted in comm \n - **Extra Bot Slot** - Addon to your license",
        color=0xADD8E6
    )
    
    view = discord.ui.View(timeout=None)
    view.add_item(discord.ui.Button(label='Purchase License', style=discord.ButtonStyle.primary, custom_id='purchaselicense'))
    view.add_item(discord.ui.Button(label='Purchase Bot Slot', style=discord.ButtonStyle.primary, custom_id='purchaseslot'))
    
    return embed, view
