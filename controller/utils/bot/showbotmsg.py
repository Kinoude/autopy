
import discord
from core.database import db
import time

async def show_bot_msg(user_id, bot_number, owner_id):
    # Fetch bot settings
    settings = await db.query("SELECT * FROM autosecure WHERE user_id = ? AND botnumber = ?", [owner_id, bot_number])
    
    if not settings:
        return {"content": "Bot not found in database (report this please!)", "ephemeral": True}
        
    s = settings[0] # Row object
    
    # Determine bot tag/status simplified
    # Legacy updates lastsavedname here
    bot_tag = s.get('lastsavedname', 'Unknown')
    # Use real tag if online lookup was possible, but we stay simple for now
    
    creation_date = s.get('creationdate', time.time())
    # Format: 2024-03-09 12:00:00 (Legacy format)
    formatted_date = time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(creation_date))
    
    hide_buttons = str(user_id) != str(owner_id)
    
    # Static thumbnail from legacy
    thumb_url = "https://cdn.discordapp.com/attachments/1282268899781382256/1436640718289502304/hel.png?ex=6910576e&is=690f05ee&hm=bc82e062b9bc3240ce40aacc5a74738d4b57b960550bad0490c8e069fa23b3dd&"
    
    # Create Embed (Approximating Container)
    embed = discord.Embed(
        # Title "You are currently managing: **Tag**"
        description=f"### You are currently managing: `{bot_tag}`",
        color=0x5d9c9e # Legacy color
    )
    
    embed.set_thumbnail(url=thumb_url)
    
    embed.add_field(name="Creation Date", value=f"```\n{formatted_date}\n```", inline=False)

    view = discord.ui.View()
    
    # Row 1: Setup/Links Actions (Legacy ActionRow1)
    # Our Website, Extra Slots
    view.add_item(discord.ui.Button(label='Our Website', style=discord.ButtonStyle.link, url='https://kinoud.site/', row=0))
    view.add_item(discord.ui.Button(label='Extra Slots', style=discord.ButtonStyle.link, url='https://asraautosecure.mysellauth.com/product/extraslot', row=0))
    
    # Row 2: Invite Bot (if owner) + Main Actions (Row 2 in legacy)
    # Legacy: Invite, Edit Bot, Autosecure, Phisher, Claim
    row_idx = 1
    if not hide_buttons:
        view.add_item(discord.ui.Button(label='Invite Bot', style=discord.ButtonStyle.link, url="https://asraautosecure.mysellauth.com/", row=row_idx)) # Using Link style as legacy uses it, wait legacy uses setURL so it IS Link style.
        # Wait, legacy setURL only if inviteLink exists. If disabled=!c (offline), it might be disabled.
        # We will assume online/available for now or generic link.
        
    view.add_item(discord.ui.Button(label="Edit Bot", style=discord.ButtonStyle.primary, custom_id=f"editbot|{bot_number}|{owner_id}", row=row_idx))
    view.add_item(discord.ui.Button(label="Autosecure", style=discord.ButtonStyle.primary, custom_id=f"editautosecure|{bot_number}|{owner_id}", row=row_idx))
    view.add_item(discord.ui.Button(label="Phisher", style=discord.ButtonStyle.primary, custom_id=f"editphisher|{bot_number}|{owner_id}", row=row_idx))
    view.add_item(discord.ui.Button(label="Claim", style=discord.ButtonStyle.primary, custom_id=f"claimusers|{bot_number}|{owner_id}", row=row_idx))
    
    # Row 3: Editors
    row_idx = 2
    view.add_item(discord.ui.Button(label="Edit Embeds", style=discord.ButtonStyle.primary, custom_id=f"editembeds|{bot_number}|{owner_id}", row=row_idx))
    view.add_item(discord.ui.Button(label="Edit Buttons", style=discord.ButtonStyle.primary, custom_id=f"editbuttons|{bot_number}|{owner_id}", row=row_idx))
    view.add_item(discord.ui.Button(label="Edit Modals", style=discord.ButtonStyle.primary, custom_id=f"editmodals|{bot_number}|{owner_id}", row=row_idx))
    view.add_item(discord.ui.Button(label="Edit Presets", style=discord.ButtonStyle.primary, custom_id=f"editpresets|{bot_number}|{owner_id}", row=row_idx))
    
    # Row 4: Configs
    row_idx = 3
    view.add_item(discord.ui.Button(label="Blacklisted users", style=discord.ButtonStyle.success, custom_id=f"blacklistedusers|{bot_number}|{owner_id}", row=row_idx))
    view.add_item(discord.ui.Button(label="Blacklisted Emails", style=discord.ButtonStyle.success, custom_id=f"blacklistedemails|{bot_number}|{owner_id}", row=row_idx))
    
    if not hide_buttons:
        view.add_item(discord.ui.Button(label="Download config", style=discord.ButtonStyle.secondary, custom_id=f"downloadconfig|{bot_number}|{owner_id}", row=row_idx))

    return {"embeds": [embed], "view": view, "ephemeral": True}
