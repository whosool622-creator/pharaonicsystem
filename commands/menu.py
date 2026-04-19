from vkbottle.bot import Bot, Message
from keyboards import get_moder_keyboard
from models.role import RoleManager, RoleLevel, ROLE_NAMES


def register(bot: Bot):
    
    @bot.on.chat_message(text=["/menu", "/меню", "меню", "menu"])
    async def menu_cmd(message: Message):
        user_role = await RoleManager.get_role(message.from_id, message.peer_id)
        
        response = f"🛡 **Панель модератора**\n\n"
        response += f"👤 Ваша роль: {ROLE_NAMES[user_role]}\n\n"
        
        response += "**📋 Основные команды:**\n"
        response += "• /warn @user [причина] — предупреждение\n"
        response += "• /warns @user — список предупреждений\n"
        response += "• /clearwarns @user — сбросить\n\n"
        
        response += "**🔇 Муты:**\n"
        response += "• /mute @user 1h [причина] — замутить\n"
        response += "• /unmute @user — размутить\n\n"
        
        response += "**🚫 Баны:**\n"
        response += "• /kick @user — кикнуть\n"
        response += "• /ban @user — забанить\n"
        response += "• /tempban @user 7d — временный бан\n"
        response += "• /unban @user — разбанить\n\n"
        
        response += "**📊 Информация:**\n"
        response += "• /info @user — информация\n"
        response += "• /history @user — история\n"
        response += "• /stats — статистика\n"
        response += "• /get_id — узнать ID\n"
        
        await message.answer(response, keyboard=get_moder_keyboard())
    
    
    @bot.on.chat_message(text=["/help", "/помощь", "help"])
    async def help_cmd(message: Message):
        args = message.text.split()
        
        if len(args) > 1:
            command = args[1].lower().lstrip("/")
            
            help_texts = {
                "warn": "/warn @user [причина] — выдаёт предупреждение. При 3 — автобан.",
                "mute": "/mute @user 1h [причина] — мут на время (30m, 2h, 1d).",
                "ban": "/ban @user [причина] — бан навсегда.",
                "tempban": "/tempban @user 7d [причина] — временный бан.",
                "kick": "/kick @user [причина] — кик без бана.",
                "role": "/role add @user admin — назначить роль.\n/role remove @user — снять.\n/role list — список.",
            }
            
            if command in help_texts:
                return await message.answer(help_texts[command])
            else:
                return await message.answer(f"❌ Справка по команде '/{command}' не найдена.")
        
        await message.answer(
            "📚 **Справка**\n\n"
            "/menu — все команды\n"
            "/help [команда] — справка по команде"
        )
