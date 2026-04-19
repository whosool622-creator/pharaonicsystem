from vkbottle.bot import Bot, Message
from models.role import RoleManager
from models.history import HistoryManager
from utils import format_time
from rules import extract_user_id_from_args


def register(bot: Bot):
    
    @bot.on.chat_message(text=["/stats", "/статистика"])
    async def stats_cmd(message: Message):
        args = message.text.split()
        days = 7
        
        if len(args) > 1:
            try:
                days = int(args[1])
            except ValueError:
                pass
        
        stats = await HistoryManager.get_stats(message.peer_id, days)
        
        response = f"📊 **Статистика беседы за {days} дн:**\n\n"
        
        action_names = {
            "warn": "⚠️ Предупреждений",
            "mute": "🔇 Мутов",
            "kick": "👢 Киков",
            "ban": "🚫 Банов",
            "tempban": "⏳ Врем. банов",
            "unban": "✅ Разбанов",
            "unmute": "🔊 Размутов"
        }
        
        response += "**Действия модерации:**\n"
        total = 0
        for action, count in stats["action_stats"].items():
            name = action_names.get(action, action)
            response += f"{name}: {count}\n"
            total += count
        
        response += f"\n**Всего действий:** {total}\n\n"
        
        if stats["top_moderators"]:
            response += "**🏆 Топ модераторов:**\n"
            for i, (mod_id, count) in enumerate(stats["top_moderators"][:5], 1):
                response += f"{i}. @id{mod_id} — {count} действ.\n"
        
        await message.answer(response)
    
    
    @bot.on.chat_message(text=["/modstats", "/модстат"])
    async def modstats_cmd(message: Message):
        args = message.text.split()
        
        if len(args) > 1:
            user_id = extract_user_id_from_args(args, 1)
            if user_id and user_id != message.from_id:
                if not await RoleManager.check_permission(message.from_id, message.peer_id, "modstats"):
                    return await message.answer("⛔ Недостаточно прав")
        else:
            user_id = message.from_id
        
        if not user_id:
            user_id = message.from_id
        
        actions = await HistoryManager.get_moderator_actions(user_id, message.peer_id, 50)
        
        if not actions:
            return await message.answer(f"ℹ️ @id{user_id} ещё не совершал действий")
        
        action_counts = {}
        for target_id, action_type, reason, duration, ts in actions:
            action_counts[action_type] = action_counts.get(action_type, 0) + 1
        
        response = f"📊 **Статистика модератора** @id{user_id}:\n\n"
        
        action_names = {
            "warn": "⚠️ Предупреждения",
            "mute": "🔇 Муты",
            "kick": "👢 Кики",
            "ban": "🚫 Баны",
            "tempban": "⏳ Врем. баны"
        }
        
        for action, count in action_counts.items():
            name = action_names.get(action, action)
            response += f"{name}: {count}\n"
        
        response += f"\n**Последние действия:**\n"
        for target_id, action_type, reason, duration, ts in actions[:5]:
            name = action_names.get(action_type, action_type)
            response += f"• {name} — @id{target_id} ({format_time(ts)})\n"
        
        await message.answer(response)
