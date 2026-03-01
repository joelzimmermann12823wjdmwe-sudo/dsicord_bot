import discord
from discord.ext import commands
from discord import app_commands
import asyncio
from Commands.helper import load_data, save_data

class TicketButton(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="🎫 Ticket erstellen", style=discord.ButtonStyle.blurple, custom_id="create_ticket")
    async def create_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        existing = discord.utils.get(interaction.guild.text_channels, name=f"ticket-{interaction.user.name.lower().replace(' ','-')}")
        if existing:
            return await interaction.response.send_message(f"Du hast bereits ein offenes Ticket: {existing.mention}", ephemeral=True)
        config   = load_data("config.json")
        role_id  = config.get(str(interaction.guild.id), {}).get("support_role")
        overwrites = {
            interaction.guild.default_role: discord.PermissionOverwrite(read_messages=False),
            interaction.user:               discord.PermissionOverwrite(read_messages=True, send_messages=True),
            interaction.guild.me:           discord.PermissionOverwrite(read_messages=True, send_messages=True, manage_channels=True),
        }
        if role_id:
            role = interaction.guild.get_role(int(role_id))
            if role: overwrites[role] = discord.PermissionOverwrite(read_messages=True, send_messages=True)
        channel = await interaction.guild.create_text_channel(
            name=f"ticket-{interaction.user.name.lower().replace(' ','-')}",
            overwrites=overwrites, category=interaction.channel.category,
            topic=f"Ticket von {interaction.user} | ID: {interaction.user.id}"
        )
        tickets = load_data("tickets.json")
        tickets[str(channel.id)] = {"user": str(interaction.user.id), "user_name": str(interaction.user), "status": "open"}
        save_data("tickets.json", tickets)
        embed = discord.Embed(title="🎫 Support Ticket", description=f"Hallo {interaction.user.mention}!\nBitte beschreibe dein Anliegen.", color=discord.Color.blurple())
        embed.set_footer(text="Neon Bot • Ticket System")
        await channel.send(content=f"{interaction.user.mention}", embed=embed, view=CloseTicketView())
        await interaction.response.send_message(f"✅ Ticket erstellt: {channel.mention}", ephemeral=True)

class CloseTicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="🔒 Ticket schliessen", style=discord.ButtonStyle.red, custom_id="close_ticket")
    async def close_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        tickets = load_data("tickets.json")
        ch_id   = str(interaction.channel.id)
        if ch_id in tickets:
            tickets[ch_id]["status"] = "closed"
            save_data("tickets.json", tickets)
        await interaction.response.send_message("🔒 Ticket wird in 5 Sekunden geschlossen...")
        await asyncio.sleep(5)
        try: await interaction.channel.delete(reason="Ticket geschlossen")
        except discord.NotFound: pass

class Tickets(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        bot.add_view(TicketButton())
        bot.add_view(CloseTicketView())

    @app_commands.command(name="ticket-setup", description="Erstellt das Ticket Panel")
    @app_commands.default_permissions(administrator=True)
    async def ticket_setup(self, interaction: discord.Interaction):
        embed = discord.Embed(title="🎫 Support Tickets", description="Klicke den Button um ein Ticket zu erstellen!", color=discord.Color.blurple())
        embed.set_footer(text="Neon Bot • Support System")
        await interaction.channel.send(embed=embed, view=TicketButton())
        await interaction.response.send_message("✅ Ticket Panel erstellt!", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Tickets(bot))
