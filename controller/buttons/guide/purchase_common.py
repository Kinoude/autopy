
# Common purchase logic
async def handler(interaction):
    custom_id = interaction.data.get('custom_id', '')
    if custom_id == 'purchaselicense':
        await interaction.response.send_message("Buy License: https://asraautosecure.mysellauth.com/", ephemeral=True)
    elif custom_id == 'purchaseslot':
         await interaction.response.send_message("Buy Slot: https://asraautosecure.mysellauth.com/product/extraslot", ephemeral=True)
