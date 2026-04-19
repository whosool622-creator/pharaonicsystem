import time
from vkbottle.bot import Bot, Message
from db_mysql import (
    add_ban, is_banned, remove_ban, get_all_bans_by_peer,
    add_temp_ban, get_active_temp_ban, remove_temp_ban, get_all_temp_bans_by_peer
)
from rules import MentionRule, extract_user_id_from_args
from utils import format_time, parse_duration, format_duration
from keyboards import get_moder_keyboard
from models.role import RoleManager
from models.history import HistoryManager, ActionType

mention_rule = MentionRule()


def register(bot: Bot):
    
    @bot.on.chat_message(text=["/ban", "/бан"])
    async def ban_cmd(message: Message):
        if not await RoleManager.check_permission(message.from_id, message.peer_id, "ban"):
            return await message.answer("⛔ Недостаточно прав")
        
        user_id = await mention_rule(message)
        if not user_id:
            args = message.text.split()
            if len(args) > 1:
                user_id = extract_user_id_from_args(args, 1)
        
        if not user_id:
            return await message.answer("❌ Укажите пользователя: /ban @user [причина]")
        
        if user_id == message.from_id:
            return await message.answer("❌ Нельзя забанить самого себя")
        
        if await RoleManager.is_founder(user_id, message.peer_id):
            return await message.answer("❌ Нельзя забанить Основателя")
        
        if await mention_rule(message):
            reason = message.text.partition("] ")[2] or "Нарушение правил"
        else:
            args = message.text.split(maxsplit=2)
            reason = args[2] if len(args) > 2 else "Нарушение правил"
        
        try:
            await bot.api.messages.remove_chat_user(
                chat_id=message.peer_id - 2000000000,
                user_id=user_id
            )
            
            await add_ban(user_id, message.peer_id, message.from_id, reason)
            
            await HistoryManager.add_entry(
                message.peer_id, message.from_id, user_id,
                ActionType.BAN, reason
            )
            
            await message.answer(
                f"🚫 @id{user_id} заблокирован навсегда\n"
                f"📝 Причина: {reason}",
                keyboard=get_moder_keyboard()
            )
        except Exception as e:
            await message.answer(f"❌ Ошибка: {e}")
    
    
    @bot.on.chat_message(text=["/unban", "/анбан", "/разбан"])
    async def unban_cmd(message: Message):
        if not await RoleManager.check_permission(message.from_id, message.peer_id, "unban"):
            return await message.answer("⛔ Недостаточно прав")
        
        user_id = await mention_rule(message)
        if not user_id:
            args = message.text.split()
            if len(args) > 1:
                user_id = extract_user_id_from_args(args, 1)
        
        if not user_id:
            return await message.answer("❌ Укажите пользователя: /unban @user")
        
        if not await is_banned(user_id, message.peer_id):
            return await message.answer(f"❌ @id{user_id} не забанен")
        
        await remove_ban(user_id, message.peer_id)
        
        await HistoryManager.add_entry(
            message.peer_id, message.from_id, user_id,
            ActionType.UNBAN, "Разбан"
        )
        
        try:
            await bot.api.messages.add_chat_user(
                chat_id=message.peer_id - 2000000000,
                user_id=user_id
            )
            await message.answer(f"✅ @id{user_id} разбанен и возвращён в беседу")
        except:
            await message.answer(f"✅ @id{user_id} разбанен (добавьте вручную)")
    
    
    @bot.on.chat_message(text=["/tempban", "/темпбан", "/врембан"])
    async def temp_ban_cmd(message: Message):
        if not await RoleManager.check_permission(message.from_id, message.peer_id, "tempban"):
            return await message.answer("⛔ Недостаточно прав")
        
        args = message.text.split()
        
        if len(args) < 3:
            return await message.answer(
                "❌ **Формат:** /tempban @user 7d [причина]\n"
                "**Примеры:** 30m, 2h, 1d, 7d"
            )
        
        user_id = extract_user_id_from_args(args, 1)
        if not user_id:
            return await message.answer("❌ Укажите пользователя")
        
        if user_id == message.from_id:
            return await message.answer("❌ Нельзя забанить самого себя")
        
        if await RoleManager.is_founder(user_id, message.peer_id):
            return await message.answer("❌ Нельзя забанить Основателя")
        
        if await is_banned(user_id, message.peer_id):
            return await message.answer(f"❌ @id{user_id} уже забанен навсегда")
        
        existing = await get_active_temp_ban(user_id, message.peer_id)
        if existing:
            return await message.answer(f"❌ @id{user_id} уже имеет временный бан")
        
        duration_str = args[2]
        duration = parse_duration(duration_str)
        if not duration:
            return await message.answer("❌ Неверный формат времени: 30m, 2h, 1d, 7d")
        
        if duration > 30 * 86400:
            return await message.answer("❌ Максимальный срок — 30 дней")
        
        reason = " ".join(args[3:]) if len(args) > 3 else "Не указана"
        unban_time = time.time() + duration
        
        await add_temp_ban(user_id, message.peer_id, message.from_id, unban_time, reason)
        
        await HistoryManager.add_entry(
            message.peer_id, message.from_id, user_id,
            ActionType.TEMPBAN, reason, duration
        )
        
        try:
            await bot.api.messages.remove_chat_user(
                chat_id=message.peer_id - 2000000000,
                user_id=user_id
            )
            await message.answer(
                f"⏳ @id{user_id} временно забанен на {format_duration(duration)}\n"
                f"📝 Причина: {reason}"
            )
        except Exception as e:
            await remove_temp_ban(user_id, message.peer_id)
            await message.answer(f"❌ Ошибка: {e}")
    
    
    @bot.on.chat_message(text=["/kick", "/кик"])
    async def kick_cmd(message: Message):
        if not await RoleManager.check_permission(message.from_id, message.peer_id, "kick"):
            return await message.answer("⛔ Недостаточно прав")
        
        user_id = await mention_rule(message)
        if not user_id:
            args = message.text.split()
            if len(args) > 1:
                user_id = extract_user_id_from_args(args, 1)
        
        if not user_id:
            return await message.answer("❌ Укажите пользователя: /kick @user")
        
        if user_id == message.from_id:
            return await message.answer("❌ Нельзя кикнуть самого себя")
        
        if await RoleManager.is_founder(user_id, message.peer_id):
            return await message.answer("❌ Нельзя кикнуть Основателя")
        
        if await mention_rule(message):
            reason = message.text.partition("] ")[2] or "Не указана"
        else:
            args = message.text.split(maxsplit=2)
            reason = args[2] if len(args) > 2 else "Не указана"
        
        try:
            await bot.api.messages.remove_chat_user(
                chat_id=message.peer_id - 2000000000,
                user_id=user_id
            )
            
            await HistoryManager.add_entry(
                message.peer_id, message.from_id, user_id,
                ActionType.KICK, reason
            )
            
            await message.answer(f"👢 @id{user_id} кикнут\n📝 Причина: {reason}")
        except Exception as e:
            await message.answer(f"❌ Ошибка: {e}")
