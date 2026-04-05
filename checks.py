from discord.ext import commands


def _get_permission_lists(bot) -> dict:
    return getattr(bot, "permissions", {})


def is_owner():
    async def predicate(ctx: commands.Context) -> bool:
        permissions = _get_permission_lists(ctx.bot)
        if ctx.author.id in permissions.get("owner", []):
            return True
        raise commands.CheckFailure("Dieser Befehl ist nur für Bot-Owner.")

    return commands.check(predicate)


def is_developer():
    async def predicate(ctx: commands.Context) -> bool:
        permissions = _get_permission_lists(ctx.bot)
        user_id = ctx.author.id
        if user_id in permissions.get("owner", []) or user_id in permissions.get("developers", []):
            return True
        raise commands.CheckFailure("Dieser Befehl ist nur für Bot-Developer.")

    return commands.check(predicate)


def is_admin_or_developer():
    async def predicate(ctx: commands.Context) -> bool:
        permissions = _get_permission_lists(ctx.bot)
        user_id = ctx.author.id
        if (
            user_id in permissions.get("owner", [])
            or user_id in permissions.get("admins", [])
            or user_id in permissions.get("developers", [])
        ):
            return True
        raise commands.CheckFailure("Dieser Befehl ist nur für Bot-Owner, Admins oder Developer.")

    return commands.check(predicate)
