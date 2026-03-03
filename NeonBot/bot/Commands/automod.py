import discord
from discord.ext import commands
from .helper import send_dm, save_json, load_json
from datetime import timedelta

class AutoMod(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bad_words = ["arschloch", "wichser", "hurensohn", "schlampe", "fotze", "bastard", "ficken", "penner"]
        self.violations = load_json("automod.json")

    @commands.Cog.listener()
    async def on_message(self, msg):
        if msg.author.bot or not msg.guild: return
        if msg.author.id == msg.guild.owner_id or msg.author.guild_permissions.administrator: return

        content = msg.content.lower()
        reason = None
        if any(w in content for w in self.bad_words): reason = "Schimpfwoerter"
        elif "discord.gg/" in content: reason = "Invite-Links"
        elif len(msg.mentions) > 5: reason = "Massen-Ping"
        elif len(msg.content) > 15 and sum(1 for c in msg.content if c.isupper()) / len(msg.content) > 0.7: reason = "Caps-Spam"

        if reason:
            uid, gid = str(msg.author.id), str(msg.guild.id)
            if gid not in self.violations: self.violations[gid] = {}
            count = self.violations[gid].get(uid, 0) + 1
            self.violations[gid][uid] = count
            save_json("automod.json", self.violations)
            
            await msg.delete()
            embed = discord.Embed(title="🛡️ AutoMod", description=f"Grund: {reason}\nStatus: {count}/3 bis Warn, {count}/6 bis Timeout", color=0xff2d78)
            await send_dm(msg.author, embed)
            
            if count == 3: await send_dm(msg.author, discord.Embed(title="⚠️ Warnung", description="3 Verstoesse erreicht!", color=0xffa500))
            if count >= 6:
                await msg.author.timeout(timedelta(hours=1), reason="AutoMod Limit")
                self.violations[gid][uid] = 0
                save_json("automod.json", self.violations)

async def setup(bot): await bot.add_cog(AutoMod(bot))
