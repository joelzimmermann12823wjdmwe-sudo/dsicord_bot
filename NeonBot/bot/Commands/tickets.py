import discord
from discord import app_commands
from discord.ext import commands

class TicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
    
    @discord.ui.button(label="Ticket erstellen", style=discord.ButtonStyle.primary, custom_id="create_ticket", emoji="??")
    async def create(self, itx: discord.Interaction, button: discord.ui.Button):
        channel = await itx.guild.create_text_channel(f"ticket-{itx.user.name}")
        await channel.set_permissions(itx.guild.default_role, view_channel=False)
        await channel.set_permissions(itx.user, view_channel=True, send_messages=True)
        await itx.response.send_message(f"Ticket erstellt: {channel.mention}", ephemeral=True)
        await channel.send(f"Willkommen {itx.user.mention}, der Support ist gleich da.")

class Tickets(commands.Cog):
    def __init__(self, bot): self.bot = bot

    @app_commands.command(name="ticketsetup", description="Ticket Panel erstellen")
    async def setup_ticket(self, itx: discord.Interaction):
        embed = discord.Embed(title="Support Ticket", description="Klicke auf den Button um ein Ticket zu öffnen.", color=0x00f0ff)
        await itx.response.send_message("Panel gesendet.", ephemeral=True)
        await itx.channel.send(embed=embed, view=TicketView())

async def setup(bot): await bot.add_cog(Tickets(bot))
