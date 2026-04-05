from discord.ext import commands


def is_developer():
    async def predicate(ctx: commands.Context) -> bool:
        permissions = getattr(ctx.bot, "permissions", {})
        return ctx.author.id in permissions.get("developers", [])

    return commands.check(predicate)


def is_admin_or_developer():
    async def predicate(ctx: commands.Context) -> bool:
        permissions = getattr(ctx.bot, "permissions", {})
        user_id = ctx.author.id
        return user_id in permissions.get("admins", []) or user_id in permissions.get("developers", [])

    return commands.check(predicate)
