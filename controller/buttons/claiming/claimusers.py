
import discord
from core.database import db

custom_id = "claimusers"

async def handler(interaction):
    try:
        parts = interaction.data['custom_id'].split("|")
        botnumber = parts[1]
        ownerid = parts[2]
        
        # Fetch unclaimed hits
        hits = await db.query("SELECT * FROM unclaimed WHERE user_id = ?", [ownerid])
        
        if not hits:
            embed = discord.Embed(title="Unclaimed Hits", description="No unclaimed hits found.", color=0x00aaff)
            return await interaction.response.send_message(embed=embed, ephemeral=True)
            
        # Display hits
        desc_lines = []
        for hit in hits[:10]:
            username = hit.get('username', 'Unknown')
            desc_lines.append(f"• **{username}**")
            
        desc = "\n".join(desc_lines)
        if len(hits) > 10: desc += f"\n...and {len(hits)-10} more."
            
        embed = discord.Embed(title=f"Unclaimed Hits ({len(hits)})", description=desc, color=0x00aaff)
        
        view = discord.ui.View()
        view.add_item(discord.ui.Button(label="Refresh", custom_id=f"claimusers|{botnumber}|{ownerid}", style=discord.ButtonStyle.secondary))
        
        if interaction.response.is_done():
             await interaction.followup.send(embed=embed, view=view, ephemeral=True)
        else:
             await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

    except Exception as e:
        print(f"Error in claimusers: {e}")
        try: await interaction.response.send_message("Error loading claims.", ephemeral=True)
        except: pass
