import time
from vkbottle.bot import Bot, Message
from db_mysql import add_mute, get_active_mute, remove_mute, get_all_mutes_by_peer
from rules import MentionRule, extract_user_id_from_args
from utils import format_duration, parse_duration, get_remaining_time
from keyboards import get_moder_keyboard
from models.role import RoleManager
from models.history import HistoryManager, ActionType

mention_rule = MentionRule()


def register(bot: Bot):
    
    @bot.on.chat_message(text=["/mute", "/мут"])
    async def mute_cmd(message: Message):
        if not await RoleManager.check_permission(message.from_id, message.peer_id, "mute"):
            return await message.answer("⛔ Недостаточно прав")
        
        args = message.text.split()
        
        if len(args) < 3:
            return await message.answer(
                "❌ **Формат:** /mute @user 1h [причина]\n"
                "**Примеры:** 30m, 2h, 1d"
            )
        
        user_id = extract_user_id_from_args(args, 1)
        if not user_id:
            return await message.answer("❌ Укажите пользователя")
        
        if user_id == message.from_id:
            return await message.answer("❌ Нельзя замутить самого себя")
        
        if await RoleManager.is_founder(user_id, message.peer_id):
            return await message.answer("❌ Нельзя замутить Основателя")
        
        existing = await get_active_mute(user_id, message.peer_id)
        if existing:
            remaining = get_remaining_time(existing[0])
            return await message.answer(f"❌ @id{user_id} уже в муте (осталось {remaining})")
        
        duration_str = args[2]
        duration = parse_duration(duration_str)
        if not duration:
            return await message.answer("❌ Неверный формат времени: 30m, 2h, 1d")
        
        if duration > 7 * 86400:
            return await message.answer("❌ Максимальный срок мута — 7 дней")
        
        reason = " ".join(args[3:]) if len(args) > 3 else "Не указана"
        unmute_time = time.time() + duration
        
        await add_mute(user_id, message.peer_id, message.from_id, unmute_time, reason)
        
        await HistoryManager.add_entry(
            message.peer_id, message.from_id, user_id,
            ActionType.MUTE, reason, duration
        )
        
        try:
            await bot.api.messages.delete(
                peer_id=message.peer_id,
                cmids=message.conversation_message_id,
                delete_for_all=True
            )
        except:
            pass
        
        await message.answer(
            f"🔇 @id{user_id} замучен на {format_duration(duration)}\n"
            f"📝 Причина: {reason}",
            keyboard=get_moder_keyboard()
        )
    
    
    @bot.on.chat_message(text=["/unmute", "/анмут", "/размут"])
    async def unmute_cmd(message: Message):
        if not await RoleManager.check_permission(message.from_id, message.peer_id, "unmute"):
            return await message.answer("⛔ Недостаточно прав")
        
        user_id = await mention_rule(message)
        if not user_id:
            args = message.text.split()
            if len(args) > 1:
                user_id = extract_user_id_from_args(args, 1)
        
        if not user_id:
            return await message.answer("❌ Укажите пользователя: /unmute @user")
        
        mute = await get_active_mute(user_id, message.peer_id)
        if not mute:
            return await message.answer(f"❌ @id{user_id} не в муте")
        
        await remove_mute(user_id, message.peer_id)
        
        await HistoryManager.add_entry(
            message.peer_id, message.from_id, user_id,
            ActionType.UNMUTE, "Досрочное снятие мута"
        )
        
        await message.answer(f"✅ @id{user_id} размучен")
    
    
    @bot.on.chat_message(text=["/mutes", "/муты"])
    async def mutelist_cmd(message: Message):
        if not await RoleManager.check_permission(message.from_id, message.peer_id, "mute"):
            return await message.answer("⛔ Недостаточно прав")
        
        mutes = await get_all_mutes_by_peer(message.peer_id)
        
        if not mutes:
            return await message.answer("📋 В беседе нет активных мутов")
        
        response = "📋 **Активные муты:**\n\n"
        for user_id, mod_id, unmute_time, reason in mutes[:20]:
            remaining = get_remaining_time(unmute_time)
            response += f"🔇 @id{user_id} — осталось {remaining}\n"
            response += f"   📝 {reason}\n\n"
        
        await message.answer(response)
