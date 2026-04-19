from vkbottle.bot import Bot, Message
from db_mysql import add_warn, get_warns_count, get_warns_list, remove_warn, clear_warns, add_ban
from rules import MentionRule, extract_user_id_from_args
from utils import format_time
from keyboards import get_moder_keyboard
from models.role import RoleManager
from models.history import HistoryManager, ActionType

mention_rule = MentionRule()


def register(bot: Bot):
    
    @bot.on.chat_message(text=["/warn", "/варн", "/пред"])
    async def warn_cmd(message: Message):
        if not await RoleManager.check_permission(message.from_id, message.peer_id, "warn"):
            return await message.answer("⛔ Недостаточно прав")
        
        user_id = await mention_rule(message)
        if not user_id:
            args = message.text.split()
            if len(args) > 1:
                user_id = extract_user_id_from_args(args, 1)
        
        if not user_id:
            return await message.answer("❌ Укажите пользователя: /warn @user [причина]")
        
        if user_id == message.from_id:
            return await message.answer("❌ Нельзя выдать предупреждение самому себе")
        
        if await RoleManager.is_founder(user_id, message.peer_id):
            return await message.answer("❌ Нельзя выдать предупреждение Основателю")
        
        if await mention_rule(message):
            reason = message.text.partition("] ")[2] or "Не указана"
        else:
            args = message.text.split(maxsplit=2)
            reason = args[2] if len(args) > 2 else "Не указана"
        
        await add_warn(user_id, message.peer_id, message.from_id, reason)
        warns_count = await get_warns_count(user_id, message.peer_id)
        
        await HistoryManager.add_entry(
            message.peer_id, message.from_id, user_id,
            ActionType.WARN, reason
        )
        
        await message.answer(
            f"⚠ @id{user_id} получил предупреждение (#{warns_count})\n"
            f"📝 Причина: {reason}\n"
            f"📊 Всего: {warns_count}/3",
            keyboard=get_moder_keyboard()
        )
        
        if warns_count >= 3:
            await add_ban(user_id, message.peer_id, message.from_id, "Накоплено 3 предупреждения")
            
            await HistoryManager.add_entry(
                message.peer_id, message.from_id, user_id,
                ActionType.BAN, "Автоматический бан за 3 предупреждения"
            )
            
            try:
                await bot.api.messages.remove_chat_user(
                    chat_id=message.peer_id - 2000000000,
                    user_id=user_id
                )
                await clear_warns(user_id, message.peer_id)
                await message.answer(f"🚫 @id{user_id} заблокирован за 3 предупреждения")
            except Exception as e:
                await message.answer(f"❌ Не удалось забанить: {e}")
    
    
    @bot.on.chat_message(text=["/warns", "/варны", "/преды"])
    async def warns_list_cmd(message: Message):
        if not await RoleManager.check_permission(message.from_id, message.peer_id, "warns"):
            return await message.answer("⛔ Недостаточно прав")
        
        args = message.text.split()
        
        if len(args) > 1:
            user_id = extract_user_id_from_args(args, 1)
        else:
            user_id = await mention_rule(message)
        
        if not user_id:
            return await message.answer("❌ Укажите пользователя: /warns @user")
        
        warns = await get_warns_list(user_id, message.peer_id)
        
        if not warns:
            return await message.answer(f"✅ У @id{user_id} нет предупреждений")
        
        response = f"📋 **Предупреждения** @id{user_id}:\n\n"
        for i, (warn_id, mod_id, reason, ts) in enumerate(warns, 1):
            response += f"{i}. [{format_time(ts)}] от @id{mod_id}\n"
            response += f"   📝 {reason}\n"
            response += f"   🆔 ID: `{warn_id}`\n\n"
        
        response += f"📊 Всего: {len(warns)}/3"
        
        await message.answer(response)
    
    
    @bot.on.chat_message(text=["/delwarn", "/делварн", "/удпред"])
    async def del_warn_cmd(message: Message):
        if not await RoleManager.check_permission(message.from_id, message.peer_id, "delwarn"):
            return await message.answer("⛔ Недостаточно прав")
        
        args = message.text.split()
        
        if len(args) < 2:
            return await message.answer("❌ Укажите ID: /delwarn 123")
        
        try:
            warn_id = int(args[1])
            await remove_warn(warn_id, message.peer_id)
            
            await HistoryManager.add_entry(
                message.peer_id, message.from_id, 0,
                ActionType.DELWARN, f"Удалено предупреждение #{warn_id}"
            )
            
            await message.answer(f"✅ Предупреждение #{warn_id} удалено")
        except ValueError:
            await message.answer("❌ Неверный ID")
    
    
    @bot.on.chat_message(text=["/clearwarns", "/клирварнс", "/сброспреды"])
    async def clear_warns_cmd(message: Message):
        if not await RoleManager.check_permission(message.from_id, message.peer_id, "clearwarns"):
            return await message.answer("⛔ Недостаточно прав")
        
        user_id = await mention_rule(message)
        if not user_id:
            args = message.text.split()
            if len(args) > 1:
                user_id = extract_user_id_from_args(args, 1)
        
        if not user_id:
            return await message.answer("❌ Укажите пользователя: /clearwarns @user")
        
        warns_count = await get_warns_count(user_id, message.peer_id)
        
        if warns_count == 0:
            return await message.answer(f"ℹ️ У @id{user_id} нет предупреждений")
        
        await clear_warns(user_id, message.peer_id)
        
        await HistoryManager.add_entry(
            message.peer_id, message.from_id, user_id,
            ActionType.CLEARWARNS, f"Сброшено {warns_count} предупреждений"
        )
        
        await message.answer(f"✅ Предупреждения @id{user_id} удалены (было {warns_count})")
