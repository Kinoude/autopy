
import discord

def guide_panel():
    embed = discord.Embed(
        title="Autosecure info",
        description="Select a button below to get more information.\nCredit: david",
        color=0xC8C8C8
    )
    
    view = discord.ui.View(timeout=None)
    
    # Row 1
    view.add_item(discord.ui.Button(label='Setup Guide', style=discord.ButtonStyle.primary, custom_id='guide_action|starting_bot', row=0))
    view.add_item(discord.ui.Button(label='Securing', style=discord.ButtonStyle.primary, custom_id='guide_action|securing', row=0))
    view.add_item(discord.ui.Button(label='Bot responses', style=discord.ButtonStyle.primary, custom_id='guide_action|responses', row=0))
    view.add_item(discord.ui.Button(label='Emails', style=discord.ButtonStyle.primary, custom_id='guide_action|emails', row=0))
    
    # Row 2
    view.add_item(discord.ui.Button(label='Login SSID', style=discord.ButtonStyle.primary, custom_id='guide_action|ssidhelp', row=1))
    view.add_item(discord.ui.Button(label='Login MSAUTH', style=discord.ButtonStyle.primary, custom_id='guide_action|login_msauth', row=1))
    view.add_item(discord.ui.Button(label='Login Secret', style=discord.ButtonStyle.primary, custom_id='guide_action|secret_key', row=1))
    
    # Row 3
    view.add_item(discord.ui.Button(label='Claiming', style=discord.ButtonStyle.primary, custom_id='guide_action|seeclaiming2', row=2))
    view.add_item(discord.ui.Button(label='Config', style=discord.ButtonStyle.primary, custom_id='guide_action|configbutton', row=2))
    
    # Row 4
    view.add_item(discord.ui.Button(label='Quarantine', style=discord.ButtonStyle.primary, custom_id='guide_action|quarantine3', row=3))
    view.add_item(discord.ui.Button(label='No Codes', style=discord.ButtonStyle.danger, custom_id='guide_action|nocode', row=3))
    view.add_item(discord.ui.Button(label="Multiplayer Fix", style=discord.ButtonStyle.danger, custom_id='guide_action|multiplayerhelp', row=3))

    return embed, view
