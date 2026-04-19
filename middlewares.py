from vkbottle.bot import Bot, Message
from models.role import RoleManager


async def admin_check_middleware(message: Message, bot: Bot):
    if message.peer_id < 2000000000:
        return True
    
    if await RoleManager.is_founder(message.from_id, message.peer_id):
        return True
    
    try:
        members = await bot.api.messages.get_conversation_members(peer_id=message.peer_id)
        for member in members.items:
            if member.member_id == message.from_id:
                if member.is_admin or member.is_owner:
                    return True
    except Exception:
        pass
    
    await message.answer("⛔ Недостаточно прав.")
    return False


async def role_check_middleware(message: Message, bot: Bot):
    if message.peer_id < 2000000000:
        return True
    
    text = message.text.lower()
    if not text.startswith("/"):
        return True
    
    command = text.split()[0][1:]
    
    command_permissions = {
        "warn": "warn", "варн": "warn",
        "warns": "warns", "варны": "warns",
        "delwarn": "delwarn", "делварн": "delwarn",
        "clearwarns": "clearwarns", "клирварнс": "clearwarns",
        "mute": "mute", "мут": "mute",
        "unmute": "unmute", "анмут": "unmute",
        "kick": "kick", "кик": "kick",
        "ban": "ban", "бан": "ban",
        "unban": "unban", "анбан": "unban",
        "tempban": "tempban", "темпбан": "tempban",
        "clean": "clean", "очистить": "clean",
        "purge": "purge",
        "pin": "pin", "закрепить": "pin",
        "unpin": "unpin", "открепить": "unpin",
        "role": "role_add",
        "greeting": "role_add", "приветствие": "role_add",
        "history": "history", "история": "history",
        "modstats": "modstats", "модстат": "modstats",
        "stats": "stats", "статистика": "stats",
    }
    
    permission = command_permissions.get(command)
    if permission:
        if not await RoleManager.check_permission(message.from_id, message.peer_id, permission):
            await message.answer("⛔ Недостаточно прав по ролевой системе.")
            return False
    
    return True
