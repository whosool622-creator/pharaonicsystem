from vkbottle.bot import Bot, Message
from models.role import RoleManager
from models.history import HistoryManager
from rules import MentionRule, extract_user_id_from_args
from utils import format_time, format_duration

mention_rule = MentionRule()


def register(bot: Bot):
    
    @bot.on.chat_message(text=["/history", "/история"])
    async def history_cmd(message: Message):
        if not await RoleManager.check_permission(message.from_id, message.peer_id, "history"):
            return await message.answer("⛔ Недостаточно прав")
        
        args = message.text.split()
        
        if len(args) > 1:
            user_id = extract_user_id_from_args(args, 1)
        else:
            user_id = await mention_rule(message)
        
        if not user_id:
            return await message.answer("❌ Укажите пользователя: /history @user")
        
        history = await HistoryManager.get_user_history(user_id, message.peer_id, 20)
        
        if not history:
            return await message.answer(f"✅ У @id{user_id} нет истории наказаний")
        
        action_names = {
            "warn": "⚠️ Предупреждение",
            "mute": "🔇 Мут",
            "unmute": "🔊 Размут",
            "kick": "👢 Кик",
            "ban": "🚫 Бан",
            "unban": "✅ Разбан",
            "tempban": "⏳ Временный бан"
        }
        
        response = f"📋 **История наказаний** @id{user_id}:\n\n"
        
        for mod_id, action_type, reason, duration, ts in history:
            action_name = action_names.get(action_type, action_type)
            response += f"• **{action_name}**\n"
            response += f"  Модератор: @id{mod_id}\n"
            response += f"  Дата: {format_time(ts)}\n"
            if reason:
                response += f"  Причина: {reason}\n"
            if duration:
                response += f"  Длительность: {format_duration(duration)}\n"
            response += "\n"
        
        await message.answer(response)
