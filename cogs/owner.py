import discord
from discord.ext import commands
from checks import is_admin_or_developer

class Owner(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

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

    @commands.hybrid_command(name="add_bot_admin", description="Fügt einen Bot-Admin hinzu.")
    @commands.is_owner()
    async def add_bot_admin(self, ctx, user_id: int):
        if user_id not in self.bot.permissions["admins"]:
            self.bot.permissions["admins"].append(user_id)
            self.bot.save_permissions()
            await ctx.send(f"✅ Admin {user_id} hinzugefügt.")
        else:
            await ctx.send("❌ User ist bereits Admin.")

    @commands.hybrid_command(name="remove_bot_admin", description="Entfernt einen Bot-Admin.")
    @commands.is_owner()
    async def remove_bot_admin(self, ctx, user_id: int):
        if user_id in self.bot.permissions["admins"]:
            self.bot.permissions["admins"].remove(user_id)
            self.bot.save_permissions()
            await ctx.send(f"✅ Admin {user_id} entfernt.")
        else:
            await ctx.send("❌ User ist kein Admin.")

    @commands.hybrid_command(name="add_bot_developer", description="Fügt einen Bot-Developer hinzu.")
    @commands.is_owner()
    async def add_bot_developer(self, ctx, user_id: int):
        if user_id not in self.bot.permissions["developers"]:
            self.bot.permissions["developers"].append(user_id)
            self.bot.save_permissions()
            await ctx.send(f"✅ Developer {user_id} hinzugefügt.")
        else:
            await ctx.send("❌ User ist bereits Developer.")

    @commands.hybrid_command(name="remove_bot_developer", description="Entfernt einen Bot-Developer.")
    @commands.is_owner()
    async def remove_bot_developer(self, ctx, user_id: int):
        if user_id in self.bot.permissions["developers"]:
            self.bot.permissions["developers"].remove(user_id)
            self.bot.save_permissions()
            await ctx.send(f"✅ Developer {user_id} entfernt.")
        else:
            await ctx.send("❌ User ist kein Developer.")

async def setup(bot):
    await bot.add_cog(Owner(bot))
