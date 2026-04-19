from vkbottle import Keyboard, KeyboardButtonColor, Text


def get_moder_keyboard() -> str:
    keyboard = Keyboard(one_time=False, inline=False)
    
    keyboard.add(Text("/ban", {"cmd": "ban"}), color=KeyboardButtonColor.NEGATIVE)
    keyboard.add(Text("/mute", {"cmd": "mute"}), color=KeyboardButtonColor.PRIMARY)
    keyboard.add(Text("/warn", {"cmd": "warn"}), color=KeyboardButtonColor.SECONDARY)
    keyboard.row()
    
    keyboard.add(Text("/unban", {"cmd": "unban"}), color=KeyboardButtonColor.POSITIVE)
    keyboard.add(Text("/unmute", {"cmd": "unmute"}), color=KeyboardButtonColor.POSITIVE)
    keyboard.row()
    
    keyboard.add(Text("/warns", {"cmd": "warns"}), color=KeyboardButtonColor.SECONDARY)
    keyboard.add(Text("/clearwarns", {"cmd": "clearwarns"}), color=KeyboardButtonColor.SECONDARY)
    keyboard.row()
    
    keyboard.add(Text("/info", {"cmd": "info"}), color=KeyboardButtonColor.PRIMARY)
    keyboard.add(Text("/history", {"cmd": "history"}), color=KeyboardButtonColor.PRIMARY)
    keyboard.row()
    
    keyboard.add(Text("/role", {"cmd": "role"}), color=KeyboardButtonColor.POSITIVE)
    keyboard.add(Text("/menu", {"cmd": "menu"}), color=KeyboardButtonColor.SECONDARY)
    
    return keyboard.get_json()


def get_role_keyboard() -> str:
    keyboard = Keyboard(one_time=False, inline=False)
    
    keyboard.add(Text("/role add", {"cmd": "role_add"}), color=KeyboardButtonColor.POSITIVE)
    keyboard.add(Text("/role remove", {"cmd": "role_remove"}), color=KeyboardButtonColor.NEGATIVE)
    keyboard.row()
    keyboard.add(Text("/role list", {"cmd": "role_list"}), color=KeyboardButtonColor.PRIMARY)
    keyboard.add(Text("/role info", {"cmd": "role_info"}), color=KeyboardButtonColor.SECONDARY)
    keyboard.row()
    keyboard.add(Text("/menu", {"cmd": "menu"}), color=KeyboardButtonColor.SECONDARY)
    
    return keyboard.get_json()


def get_stats_keyboard() -> str:
    keyboard = Keyboard(one_time=False, inline=False)
    
    keyboard.add(Text("/stats", {"cmd": "stats"}), color=KeyboardButtonColor.PRIMARY)
    keyboard.add(Text("/modstats", {"cmd": "modstats"}), color=KeyboardButtonColor.SECONDARY)
    keyboard.row()
    keyboard.add(Text("/top", {"cmd": "top"}), color=KeyboardButtonColor.POSITIVE)
    keyboard.add(Text("/menu", {"cmd": "menu"}), color=KeyboardButtonColor.SECONDARY)
    
    return keyboard.get_json()
