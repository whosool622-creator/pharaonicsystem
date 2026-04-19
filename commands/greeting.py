from vkbottle.bot import Bot, Message
from vkbottle import VKAPIError
from db_mysql import set_greeting, get_greeting, disable_greeting
from models.role import RoleManager


def register(bot: Bot):
    
    @bot.on.chat_message(text=["/greeting", "/приветствие"])
    async def greeting_cmd(message: Message):
        if not await RoleManager.check_permission(message.from_id, message.peer_id, "role_add"):
            return await message.answer("⛔ Недостаточно прав")
        
        args = message.text.split(maxsplit=1)
        
        if len(args) == 1:
            current = await get_greeting(message.peer_id)
            if current:
                return await message.answer(
                    f"📝 Текущее приветствие:\n{current}\n\n"
                    "/greeting off — отключить\n"
                    "/greeting set Текст — изменить"
                )
            else:
                return await message.answer("📝 Приветствие не настроено.\n/greeting set Текст")
        
        subcmd = args[1].lower()
        
        if subcmd == "off":
            await disable_greeting(message.peer_id)
            await message.answer("✅ Приветствие отключено")
        
        elif subcmd.startswith("set "):
            greeting_text = args[1][4:]
            await set_greeting(message.peer_id, greeting_text, True)
            await message.answer(f"✅ Приветствие установлено:\n{greeting_text}")
        
        else:
            await message.answer(
                "📋 **Настройка приветствий:**\n"
                "/greeting set Текст — установить\n"
                "/greeting off — отключить\n"
                "/greeting — показать\n\n"
                "**Переменные:** {name}, {mention}, {chat}"
            )
    
    
    @bot.on.chat_member_join()
    async def on_member_join(message: Message):
        greeting = await get_greeting(message.peer_id)
        if not greeting:
            return
        
        try:
            user_info = await bot.api.users.get(user_ids=message.from_id)
            user_name = user_info[0].first_name if user_info else "Пользователь"
        except VKAPIError:
            user_name = "Пользователь"
        
        try:
            chat_info = await bot.api.messages.get_conversations_by_id(peer_ids=message.peer_id)
            chat_name = chat_info.items[0].chat_settings.title if chat_info.items else "Беседа"
        except:
            chat_name = "Беседа"
        
        greeting_text = greeting.replace("{name}", user_name)
        greeting_text = greeting_text.replace("{mention}", f"@id{message.from_id}")
        greeting_text = greeting_text.replace("{chat}", chat_name)
        
        await message.answer(greeting_text)
