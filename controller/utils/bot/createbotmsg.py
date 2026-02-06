
import discord
from core.database import db

# Ported from createbotmsg.js
async def create_bot_msg(client, user_id):
    try:
        # 1. Fetch user's bots
        bots = await db.query(
            "SELECT botnumber, token FROM autosecure WHERE user_id = ? ORDER BY botnumber ASC", 
            [user_id]
        )
        
        # 2. Fetch user's slots
        slots = 1
        slots_res = await db.query("SELECT slots FROM slots WHERE user_id = ?", [user_id])
        if slots_res:
             slots = slots_res[0]['slots']
             
        filtered_bots = [b for b in bots if b.get('token') and b.get('token').strip()]
        current_used_slots = len(filtered_bots)
        open_slots = max(0, slots - current_used_slots)
        
        # 3. Handling Single Bot case
        from controller.utils.bot.showbotmsg import show_bot_msg
        if slots == 1 and current_used_slots == 1:
             single_bot = filtered_bots[0]
             return await show_bot_msg(user_id, single_bot['botnumber'], user_id)

        # 4. Build Select Menu
        options = []
        
        # Add existing bots
        max_options = 25
        
        for bot in filtered_bots[:20]:
             label = f"Bot #{bot['botnumber']}"
             value = f"bot|{user_id}|{bot['botnumber']}"
             options.append(discord.SelectOption(label=label, value=value))
             
        # Add "Create new bot" option if slots available
        # Find next available bot number
        used_numbers = [b['botnumber'] for b in bots]
        next_bot_num = 1
        while next_bot_num in used_numbers:
            next_bot_num += 1
            
        if open_slots > 0 and len(options) < max_options:
             options.append(discord.SelectOption(
                 label="Create a new bot", 
                 value=f"newbot|{user_id}|{next_bot_num}",
                 # description="Setup a new bot instance"
             ))
             
        # Add Purchase option if applicable (slots=1, used=1)
        if slots == 1 and current_used_slots == 1:
             options.append(discord.SelectOption(label="Add an extra bot slot!", value="purchaseslot"))

        # If empty (no bots, but slots available)
        if not options:
             options.append(discord.SelectOption(
                 label="Create your first bot",
                 value=f"newbot|{user_id}|1",
                 description="You don't have any bots yet"
             ))

        # Fallback
        if not options:
             options.append(discord.SelectOption(label="No actions available", value="none"))

        select_menu = discord.ui.Select(
            placeholder="Manage bots",
            custom_id=f"managebots|{user_id}",
            options=options
        )
        
        view = discord.ui.View()
        view.add_item(select_menu)
        
        # Purchase Button Row (ActionRow 1 in legacy)
        # Legacy: Purchase Slots (Link)
        view.add_item(discord.ui.Button(label="Purchase Slots", style=discord.ButtonStyle.link, url="https://asraautosecure.mysellauth.com/product/extraslot"))

        # Embed constructions replicating legacy TextDisplay content
        embed = discord.Embed(
            title="Panel for bots management",
            description=(
                f"The maximum number of bots you can manage is `{slots}`\n"
                "\n"
                "You can manage the bot on the main Autosecure bot or on your own bot using `/bots`.\n"
                "Some options may only be available on the main bot (like Replace Token, Restart Bot).\n"
                "\n"
                "If you want more slots, buy additional ones by clicking the button below"
            ),
            color=0x40e0d0
        )
        
        return {"embeds": [embed], "view": view, "ephemeral": True}

    except Exception as e:
        print(f"Error in create_bot_msg: {e}")
        import traceback
        traceback.print_exc()
        return {"content": "Error loading bot panel.", "ephemeral": True}
