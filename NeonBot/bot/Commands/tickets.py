import discord
import asyncio
from discord.ext import commands
from discord import app_commands
from Commands.helper import load_data, save_data

class TicketButton(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="🎫 Ticket erstellen", style=discord.ButtonStyle.blurple, custom_id="neonbot_create_ticket")
    async def create_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        safe_name = interaction.user.name.lower().replace(" ", "-").replace("_", "-")[:20]
        channel_name = f"ticket-{safe_name}"
        existing = discord.utils.get(interaction.guild.text_channels, name=channel_name)
        if existing:
            return await interaction.response.send_message(
                f"❌ Du hast bereits ein offenes Ticket: {existing.mention}", ephemeral=True
            )
        cfg     = load_data("config.json")
        role_id = cfg.get(str(interaction.guild.id), {}).get("support_role")
        overwrites = {
            interaction.guild.default_role: discord.PermissionOverwrite(read_messages=False),
            interaction.user:               discord.PermissionOverwrite(read_messages=True, send_messages=True),
            interaction.guild.me:           discord.PermissionOverwrite(read_messages=True, send_messages=True, manage_channels=True),
        }
        if role_id:
            role = interaction.guild.get_role(int(role_id))
            if role: overwrites[role] = discord.PermissionOverwrite(read_messages=True, send_messages=True)

        try:
            ch = await interaction.guild.create_text_channel(
                name       = channel_name,
                overwrites = overwrites,
                category   = interaction.channel.category,
                topic      = f"Ticket von {interaction.user} | ID: {interaction.user.id}"
            )
        except discord.Forbidden:
            return await interaction.response.send_message("❌ Ich habe keine Berechtigung einen Channel zu erstellen!", ephemeral=True)

        tickets = load_data("tickets.json")
        tickets[str(ch.id)] = {
            "user":      str(interaction.user.id),
            "user_name": str(interaction.user),
            "status":    "open"
        }
        save_data("tickets.json", tickets)

        embed = discord.Embed(
            title       = "🎫 Support Ticket",
            description = f"Hallo {interaction.user.mention}!\nBitte beschreibe dein Anliegen ausführlich.",
            color       = discord.Color.blurple()
        )
        embed.set_footer(text="Neon Bot • Ticket System")
        await ch.send(content=interaction.user.mention, embed=embed, view=CloseTicketView())
        await interaction.response.send_message(f"✅ Ticket erstellt: {ch.mention}", ephemeral=True)


class CloseTicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="🔒 Ticket schließen", style=discord.ButtonStyle.red, custom_id="neonbot_close_ticket")
    async def close_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        tickets = load_data("tickets.json")
        ch_id   = str(interaction.channel.id)
        if ch_id in tickets:
            tickets[ch_id]["status"] = "closed"
            save_data("tickets.json", tickets)
        await interaction.response.send_message("🔒 Ticket wird in 5 Sekunden geschlossen...")
        await asyncio.sleep(5)
        try:
            await interaction.channel.delete(reason="Ticket geschlossen")
        except discord.NotFound:
            pass


class Tickets(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        bot.add_view(TicketButton())
        bot.add_view(CloseTicketView())

    @app_commands.command(
        name        = "ticketsetup",
        description = "Erstellt ein Ticket-Panel mit Button in diesem Channel"
    )
    @app_commands.default_permissions(administrator=True)
    async def ticketsetup(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title       = "🎫 Support Tickets",
            description = "Klicke den Button unten um ein Support-Ticket zu erstellen!",
            color       = discord.Color.blurple()
        )
        embed.set_footer(text="Neon Bot • Support System")
        await interaction.channel.send(embed=embed, view=TicketButton())
        await interaction.response.send_message("✅ Ticket-Panel erstellt!", ephemeral=True)

    @app_commands.command(
        name        = "supportrolle",
        description = "Setzt die Support-Rolle die Zugriff auf alle Tickets hat"
    )
    @app_commands.describe(rolle="Die Support-Rolle")
    @app_commands.default_permissions(administrator=True)
    async def supportrolle(self, interaction: discord.Interaction, rolle: discord.Role):
        cfg = load_data("config.json")
        gid = str(interaction.guild.id)
        if gid not in cfg: cfg[gid] = {}
        cfg[gid]["support_role"] = str(rolle.id)
        save_data("config.json", cfg)
        await interaction.response.send_message(
            f"✅ Support-Rolle auf {rolle.mention} gesetzt!", ephemeral=True
        )

async def setup(bot):
    await bot.add_cog(Tickets(bot))
