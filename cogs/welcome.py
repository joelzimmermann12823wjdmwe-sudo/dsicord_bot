import discord
from discord.ext import commands

class Welcome(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member):
        res = self.bot.supabase.table("server_settings").select("welcome_channel_id, welcome_message").eq("guild_id", member.guild.id).execute()
        
        if res.data:
            channel_id = res.data[0]['welcome_channel_id']
            msg = res.data[0]['welcome_message']
            
            if channel_id:
                channel = member.guild.get_channel(channel_id)
                if channel:
                    formatted_msg = msg.replace("{user}", member.mention).replace("{server}", member.guild.name)
                    await channel.send(formatted_msg)

async def setup(bot):
    await bot.add_cog(Welcome(bot))
