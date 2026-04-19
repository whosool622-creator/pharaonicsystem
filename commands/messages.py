from vkbottle.bot import Bot, Message
from models.role import RoleManager
from models.history import HistoryManager, ActionType
from rules import MentionRule, extract_user_id_from_args

mention_rule = MentionRule()


def register(bot: Bot):
    
    @bot.on.chat_message(text=["/clean", "/очистить"])
    async def clean_cmd(message: Message):
        if not await RoleManager.check_permission(message.from_id, message.peer_id, "clean"):
            return await message.answer("⛔ Недостаточно прав")
        
        args = message.text.split()
        count = 10
        
        if len(args) > 1:
            try:
                count = min(int(args[1]), 100)
            except ValueError:
                pass
        
        try:
            history = await bot.api.messages.get_history(
                peer_id=message.peer_id,
                count=100
            )
            
            bot_messages = [
                msg.conversation_message_id 
                for msg in history.items 
                if msg.from_id == -bot.group_id
            ][:count]
            
            if bot_messages:
                await bot.api.messages.delete(
                    peer_id=message.peer_id,
                    cmids=bot_messages,
                    delete_for_all=True
                )
                await message.answer(f"✅ Удалено {len(bot_messages)} сообщений бота")
            else:
                await message.answer("ℹ️ Нет сообщений бота для удаления")
                
        except Exception as e:
            await message.answer(f"❌ Ошибка: {e}")
    
    
    @bot.on.chat_message(text=["/purge", "/очистить_пользователя"])
    async def purge_cmd(message: Message):
        if not await RoleManager.check_permission(message.from_id, message.peer_id, "purge"):
            return await message.answer("⛔ Недостаточно прав")
        
        args = message.text.split()
        user_id = await mention_rule(message)
        
        if not user_id and len(args) > 1:
            user_id = extract_user_id_from_args(args, 1)
        
        if not user_id:
            return await message.answer("❌ Укажите пользователя: /purge @user [количество]")
        
        count = 20
        if len(args) > 2:
            try:
                count = min(int(args[2]), 100)
            except ValueError:
                pass
        
        try:
            history = await bot.api.messages.get_history(
                peer_id=message.peer_id,
                count=200
            )
            
            user_messages = [
                msg.conversation_message_id 
                for msg in history.items 
                if msg.from_id == user_id
            ][:count]
            
            if user_messages:
                await bot.api.messages.delete(
                    peer_id=message.peer_id,
                    cmids=user_messages,
                    delete_for_all=True
                )
                
                await HistoryManager.add_entry(
                    message.peer_id, message.from_id, user_id,
                    ActionType.PURGE, f"Удалено {len(user_messages)} сообщений"
                )
                
                await message.answer(f"✅ Удалено {len(user_messages)} сообщений @id{user_id}")
            else:
                await message.answer(f"ℹ️ Нет сообщений @id{user_id} для удаления")
                
        except Exception as e:
            await message.answer(f"❌ Ошибка: {e}")
    
    
    @bot.on.chat_message(text=["/pin", "/закрепить"])
    async def pin_cmd(message: Message):
        if not await RoleManager.check_permission(message.from_id, message.peer_id, "pin"):
            return await message.answer("⛔ Недостаточно прав")
        
        if not message.reply_message:
            return await message.answer("❌ Ответьте на сообщение, которое нужно закрепить")
        
        try:
            await bot.api.messages.pin(
                peer_id=message.peer_id,
                conversation_message_id=message.reply_message.conversation_message_id
            )
            await message.answer("📌 Сообщение закреплено")
        except Exception as e:
            await message.answer(f"❌ Ошибка: {e}")
    
    
    @bot.on.chat_message(text=["/unpin", "/открепить"])
    async def unpin_cmd(message: Message):
        if not await RoleManager.check_permission(message.from_id, message.peer_id, "unpin"):
            return await message.answer("⛔ Недостаточно прав")
        
        try:
            await bot.api.messages.unpin(peer_id=message.peer_id)
            await message.answer("📌 Сообщение откреплено")
        except Exception as e:
            await message.answer(f"❌ Ошибка: {e}")
