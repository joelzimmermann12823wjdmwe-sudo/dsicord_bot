from discord.ext import commands


def _get_permission_lists(bot) -> dict:
    return getattr(bot, "permissions", {})


def is_owner():
    async def predicate(ctx: commands.Context) -> bool:
        permissions = _get_permission_lists(ctx.bot)
        return ctx.author.id in permissions.get("owner", [])

    return commands.check(predicate)


def is_developer():
    async def predicate(ctx: commands.Context) -> bool:
        permissions = _get_permission_lists(ctx.bot)
        user_id = ctx.author.id
        return user_id in permissions.get("owner", []) or user_id in permissions.get("developers", [])

    return commands.check(predicate)


def is_admin_or_developer():
    async def predicate(ctx: commands.Context) -> bool:
        permissions = _get_permission_lists(ctx.bot)
        user_id = ctx.author.id
        return (
            user_id in permissions.get("owner", [])
            or user_id in permissions.get("admins", [])
            or user_id in permissions.get("developers", [])
        )

    return commands.check(predicate)
