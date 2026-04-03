import discord

DEFAULT_COLOR = discord.Color.from_rgb(0, 212, 255)


def create_embed(title: str, description: str = "", color: discord.Color = DEFAULT_COLOR, footer: str = "Neon Bot") -> discord.Embed:
    embed = discord.Embed(title=title, description=description, color=color)
    embed.set_footer(text=footer)
    embed.timestamp = discord.utils.utcnow()
    return embed


async def send_discipline_dm(
    member: discord.Member,
    guild: discord.Guild,
    action: str,
    reason: str = "kein Grund angegeben",
    duration: int | None = None,
) -> bool:
    invite_link = None
    try:
        if getattr(guild, "vanity_url", None):
            invite_link = str(guild.vanity_url)
        else:
            invite_channel = guild.system_channel
            if invite_channel is None:
                invite_channel = next(
                    (
                        channel
                        for channel in guild.text_channels
                        if channel.permissions_for(guild.me).create_instant_invite
                    ),
                    None,
                )
            if invite_channel is not None:
                invite = await invite_channel.create_invite(
                    max_age=86400,
                    max_uses=1,
                    unique=True,
                    reason=f"Einladungslink nach {action} für {member}",
                )
                invite_link = str(invite)
    except Exception:
        invite_link = None

    embed = create_embed(
        title=f"Serverinfo: {guild.name}",
        description=f"Du wurdest {action}.",
    )
    embed.add_field(name="Server", value=guild.name, inline=False)
    embed.add_field(name="Grund", value=reason or "kein Grund angegeben", inline=False)
    if duration is not None:
        embed.add_field(name="Dauer", value=f"{duration} Minuten", inline=False)
    embed.add_field(
        name="Serverlink",
        value=invite_link or "Kein Einladungslink verfügbar.",
        inline=False,
    )

    try:
        await member.send(embed=embed)
        return True
    except Exception:
        return False


def field_embed(title: str, description: str, fields: list[tuple[str, str, bool]] | None = None, color: discord.Color = DEFAULT_COLOR, footer: str = "Neon Bot") -> discord.Embed:
    embed = create_embed(title=title, description=description, color=color, footer=footer)
    if fields:
        for name, value, inline in fields:
            embed.add_field(name=name, value=value, inline=inline)
    return embed
