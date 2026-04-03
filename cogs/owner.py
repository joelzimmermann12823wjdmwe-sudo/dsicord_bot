import discord
from discord.ext import commands

class Owner(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def is_admin_or_developer(self):
        async def predicate(ctx):
            user_id = ctx.author.id
            return user_id in self.bot.permissions.get("admins", []) or user_id in self.bot.permissions.get("developers", [])
        return commands.check(predicate)

    @commands.hybrid_command(name="owner", description="Exklusive Befehle für den Bot-Entwickler.")
    @commands.is_owner()
    async def owner(self, ctx):
        await ctx.send("👑 Willkommen Meister. Alle Systeme laufen reibungslos.")

    @commands.hybrid_command(name="ban_server", description="Bannt einen Server.")
    @is_admin_or_developer()
    async def ban_server(self, ctx, server_id: int):
        if server_id not in self.bot.permissions["banned_servers"]:
            self.bot.permissions["banned_servers"].append(server_id)
            self.bot.save_permissions()
            await ctx.send(f"✅ Server {server_id} gebannt.")
        else:
            await ctx.send("❌ Server bereits gebannt.")

    @commands.hybrid_command(name="unban_server", description="Entbannt einen Server.")
    @is_admin_or_developer()
    async def unban_server(self, ctx, server_id: int):
        if server_id in self.bot.permissions["banned_servers"]:
            self.bot.permissions["banned_servers"].remove(server_id)
            self.bot.save_permissions()
            await ctx.send(f"✅ Server {server_id} entbannt.")
        else:
            await ctx.send("❌ Server nicht gebannt.")

    @commands.hybrid_command(name="ban_user", description="Bannt einen User.")
    @is_admin_or_developer()
    async def ban_user(self, ctx, user_id: int):
        if user_id not in self.bot.permissions["banned_users"]:
            self.bot.permissions["banned_users"].append(user_id)
            self.bot.save_permissions()
            await ctx.send(f"✅ User {user_id} gebannt.")
        else:
            await ctx.send("❌ User bereits gebannt.")

    @commands.hybrid_command(name="unban_user", description="Entbannt einen User.")
    @is_admin_or_developer()
    async def unban_user(self, ctx, user_id: int):
        if user_id in self.bot.permissions["banned_users"]:
            self.bot.permissions["banned_users"].remove(user_id)
            self.bot.save_permissions()
            await ctx.send(f"✅ User {user_id} entbannt.")
        else:
            await ctx.send("❌ User nicht gebannt.")

async def setup(bot):
    await bot.add_cog(Owner(bot))
