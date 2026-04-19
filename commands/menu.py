from vkbottle.bot import Bot, Message
from keyboards import get_moder_keyboard
from models.role import RoleManager, RoleLevel, ROLE_NAMES


def register(bot: Bot):
    
    @bot.on.chat_message(text=["/menu", "/меню", "меню", "menu"])
    async def menu_cmd(message: Message):
        user_role = await RoleManager.get_role(message.from_id, message.peer_id)
        
        response = f"🛡 **ПАНЕЛЬ МОДЕРАТОРА**\n\n"
        response += f"👤 Ваша роль: {ROLE_NAMES[user_role]}\n"
        response += f"💡 /help — справка по всем командам\n\n"
        
        response += "**📋 Основные команды:**\n"
        response += "• /warn @user [причина] — предупреждение\n"
        response += "• /warns @user — список предупреждений\n"
        response += "• /clearwarns @user — сбросить\n\n"
        
        response += "**🔇 Муты:**\n"
        response += "• /mute @user 1h [причина] — замутить\n"
        response += "• /unmute @user — размутить\n"
        response += "• /mutes — список мутов\n\n"
        
        response += "**🚫 Баны:**\n"
        response += "• /kick @user — кикнуть\n"
        response += "• /ban @user — забанить навсегда\n"
        response += "• /tempban @user 7d — временный бан\n"
        response += "• /unban @user — разбанить\n"
        response += "• /bans — список банов\n\n"
        
        response += "**📊 Информация:**\n"
        response += "• /info @user — информация\n"
        response += "• /history @user — история\n"
        response += "• /stats — статистика\n"
        response += "• /get_id — узнать ID\n\n"
        
        if user_role >= RoleLevel.ADMIN:
            response += "**📌 Управление:**\n"
            response += "• /role — управление ролями\n"
            response += "• /clean, /purge — очистка сообщений\n"
            response += "• /greeting — приветствия\n\n"
        
        response += "💡 Используйте кнопки ниже для быстрого доступа."
        
        await message.answer(response, keyboard=get_moder_keyboard())
