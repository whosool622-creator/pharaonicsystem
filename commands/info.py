from vkbottle.bot import Bot, Message
from db_mysql import get_warns_count, get_active_mute, is_banned, get_ban_info, get_active_temp_ban
from rules import MentionRule, extract_user_id_from_args
from utils import format_time, get_remaining_time
from models.role import RoleManager, ROLE_NAMES

mention_rule = MentionRule()


def register(bot: Bot):
    
    @bot.on.chat_message(text=["/info", "/инфо"])
    async def info_cmd(message: Message):
        user_id = await mention_rule(message)
        if not user_id:
            args = message.text.split()
            if len(args) > 1:
                user_id = extract_user_id_from_args(args, 1)
        
        if not user_id:
            user_id = message.from_id
        
        warns = await get_warns_count(user_id, message.peer_id)
        mute = await get_active_mute(user_id, message.peer_id)
        banned = await is_banned(user_id, message.peer_id)
        temp_ban = await get_active_temp_ban(user_id, message.peer_id)
        role = await RoleManager.get_role(user_id, message.peer_id)
        
        user_name = "Пользователь"
        try:
            user_info = await bot.api.users.get(user_ids=user_id)
            if user_info:
                user_name = f"{user_info[0].first_name} {user_info[0].last_name}"
        except:
            pass
        
        response = f"📊 **Информация о пользователе**\n\n"
        response += f"👤 **Имя:** {user_name}\n"
        response += f"🆔 **ID:** `{user_id}`\n"
        response += f"📌 **Роль:** {ROLE_NAMES[role]}\n\n"
        
        response += f"⚠️ **Предупреждений:** {warns}/3\n"
        
        if mute:
            remaining = get_remaining_time(mute[0])
            response += f"🔇 **В муте:** да (осталось {remaining})\n"
            response += f"   📝 {mute[1]}\n"
        else:
            response += "🔇 **В муте:** нет\n"
        
        if banned:
            ban_info = await get_ban_info(user_id, message.peer_id)
            if ban_info:
                response += "🚫 **Забанен:** да (навсегда)\n"
                response += f"   📝 {ban_info[1]}\n"
                response += f"   📅 {format_time(ban_info[2])}\n"
        elif temp_ban:
            remaining = get_remaining_time(temp_ban[0])
            response += f"⏳ **Временный бан:** да (осталось {remaining})\n"
            response += f"   📝 {temp_ban[1]}\n"
        else:
            response += "🚫 **Забанен:** нет\n"
        
        await message.answer(response)
