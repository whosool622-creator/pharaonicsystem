from vkbottle.bot import Bot


def register_commands(bot: Bot):
    from commands.menu import register as register_menu
    from commands.help import register as register_help
    from commands.warns import register as register_warns
    from commands.mutes import register as register_mutes
    from commands.bans import register as register_bans
    from commands.info import register as register_info
    from commands.get_id import register as register_get_id
    from commands.roles import register as register_roles
    from commands.greeting import register as register_greeting
    from commands.messages import register as register_messages
    from commands.stats import register as register_stats
    from commands.history_cmd import register as register_history
    
    register_menu(bot)
    register_help(bot)
    register_warns(bot)
    register_mutes(bot)
    register_bans(bot)
    register_info(bot)
    register_get_id(bot)
    register_roles(bot)
    register_greeting(bot)
    register_messages(bot)
    register_stats(bot)
    register_history(bot)
