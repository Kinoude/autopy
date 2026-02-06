
import discord

custom_id = "createticket"

async def handler(interaction):
    # Determine ticket type from selection if it's a select menu
    # or just open a generic ticket if it's a button
    
    # Check if a ticket channel already exists for this user?
    # Simple logic: Create a thread
    
    user_name = interaction.user.name
    chan_name = f"ticket-{user_name}"
    
    thread = await interaction.channel.start_thread(name=chan_name, type=discord.ChannelType.private_thread)
    await thread.add_user(interaction.user)
    
    embed = discord.Embed(
        title="Ticket Opened",
        description=f"Hello {interaction.user.mention}, support will be with you shortly.\nPlease describe your issue.",
        color=0x00FF00
    )
    
    await thread.send(embed=embed)
    await interaction.response.send_message(f"Ticket created: {thread.mention}", ephemeral=True)
