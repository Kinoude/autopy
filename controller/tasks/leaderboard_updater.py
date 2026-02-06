
import discord
from discord.ext import tasks, commands
from controller.utils.panels.leaderboard_panel import generate_leaderboard_embeds, get_message_id

class LeaderboardUpdater(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.update_leaderboard.start()

    def cog_unload(self):
        self.update_leaderboard.cancel()

    @tasks.loop(hours=1)
    async def update_leaderboard(self):
        await self.bot.wait_until_ready()
        try:
            data = await get_message_id()
            if not data: return

            msg_id, channel_id = data.split("|")
            try:
                channel = self.bot.get_channel(int(channel_id)) or await self.bot.fetch_channel(int(channel_id))
            except: return
            
            try:
                message = await channel.fetch_message(int(msg_id))
            except: return
                
            embed, view = await generate_leaderboard_embeds()
            await message.edit(embed=embed, view=view)
            
        except Exception as e:
            print(f"[Leaderboard] Error: {e}")

    @update_leaderboard.before_loop
    async def before_update_leaderboard(self):
        await self.bot.wait_until_ready()

async def setup(bot):
    await bot.add_cog(LeaderboardUpdater(bot))
