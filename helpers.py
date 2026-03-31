import discord

DEFAULT_COLOR = discord.Color.from_rgb(0, 212, 255)


def create_embed(title: str, description: str = "", color: discord.Color = DEFAULT_COLOR, footer: str = "Neon Bot") -> discord.Embed:
    embed = discord.Embed(title=title, description=description, color=color)
    embed.set_footer(text=footer)
    embed.timestamp = discord.utils.utcnow()
    return embed


def field_embed(title: str, description: str, fields: list[tuple[str, str, bool]] | None = None, color: discord.Color = DEFAULT_COLOR, footer: str = "Neon Bot") -> discord.Embed:
    embed = create_embed(title=title, description=description, color=color, footer=footer)
    if fields:
        for name, value, inline in fields:
            embed.add_field(name=name, value=value, inline=inline)
    return embed
