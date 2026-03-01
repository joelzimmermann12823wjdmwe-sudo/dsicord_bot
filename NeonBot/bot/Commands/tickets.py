import discord, asyncio
from discord.ext import commands
from discord import app_commands
from Commands.helper import load_data, save_data


class TicketButton(discord.ui.View):
    def __init__(self): super().__init__(timeout=None)

    @discord.ui.button(label="🎫 Ticket erstellen", style=discord.ButtonStyle.blurple, custom_id="neonbot_ticket_create")
    async def create(self, interaction: discord.Interaction, button: discord.ui.Button):
        name = f"ticket-{interaction.user.name.lower().replace(' ','-')[:20]}"
        ex   = discord.utils.get(interaction.guild.text_channels, name=name)
        if ex:
            return await interaction.response.send_message(f"❌ Ticket existiert bereits: {ex.mention}", ephemeral=True)
        cfg     = load_data("config.json")
        role_id = cfg.get(str(interaction.guild.id), {}).get("support_role")
        ow = {
            interaction.guild.default_role: discord.PermissionOverwrite(read_messages=False),
            interaction.user:               discord.PermissionOverwrite(read_messages=True, send_messages=True),
            interaction.guild.me:           discord.PermissionOverwrite(read_messages=True, send_messages=True, manage_channels=True),
        }
        if role_id:
            r = interaction.guild.get_role(int(role_id))
            if r: ow[r] = discord.PermissionOverwrite(read_messages=True, send_messages=True)
        try:
            ch = await interaction.guild.create_text_channel(name=name, overwrites=ow, category=interaction.channel.category)
        except discord.Forbidden:
            return await interaction.response.send_message("❌ Keine Berechtigung!", ephemeral=True)
        t = load_data("tickets.json")
        t[str(ch.id)] = {"user": str(interaction.user.id), "user_name": str(interaction.user), "status": "open"}
        save_data("tickets.json", t)
        e = discord.Embed(title="🎫 Support Ticket", description=f"Hallo {interaction.user.mention}!\nBitte beschreibe dein Anliegen.", color=discord.Color.blurple())
        e.set_footer(text="Neon Bot • Ticket System")
        await ch.send(content=interaction.user.mention, embed=e, view=CloseTicketView())
        await interaction.response.send_message(f"✅ Ticket: {ch.mention}", ephemeral=True)


class CloseTicketView(discord.ui.View):
    def __init__(self): super().__init__(timeout=None)

    @discord.ui.button(label="🔒 Ticket schliessen", style=discord.ButtonStyle.red, custom_id="neonbot_ticket_close")
    async def close(self, interaction: discord.Interaction, button: discord.ui.Button):
        t = load_data("tickets.json"); cid = str(interaction.channel.id)
        if cid in t: t[cid]["status"] = "closed"; save_data("tickets.json", t)
        await interaction.response.send_message("🔒 Wird in 5 Sekunden geschlossen...")
        await asyncio.sleep(5)
        try: await interaction.channel.delete(reason="Ticket geschlossen")
        except discord.NotFound: pass


class Tickets(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        bot.add_view(TicketButton())
        bot.add_view(CloseTicketView())

    @app_commands.command(name="ticketsetup", description="Erstellt ein Ticket-Panel in diesem Channel")
    @app_commands.default_permissions(administrator=True)
    async def ticketsetup(self, interaction: discord.Interaction):
        e = discord.Embed(title="🎫 Support Tickets", description="Klicke den Button um ein Ticket zu erstellen!", color=discord.Color.blurple())
        e.set_footer(text="Neon Bot • Support System")
        await interaction.channel.send(embed=e, view=TicketButton())
        await interaction.response.send_message("✅ Ticket-Panel erstellt!", ephemeral=True)

    @app_commands.command(name="supportrolle", description="Setzt die Support-Rolle fuer Tickets")
    @app_commands.describe(rolle="Die Support-Rolle")
    @app_commands.default_permissions(administrator=True)
    async def supportrolle(self, interaction: discord.Interaction, rolle: discord.Role):
        cfg = load_data("config.json"); gid = str(interaction.guild.id)
        if gid not in cfg: cfg[gid] = {}
        cfg[gid]["support_role"] = str(rolle.id); save_data("config.json", cfg)
        await interaction.response.send_message(f"✅ Support-Rolle: {rolle.mention}", ephemeral=True)


async def setup(bot): await bot.add_cog(Tickets(bot))
