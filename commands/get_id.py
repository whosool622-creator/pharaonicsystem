from vkbottle.bot import Bot, Message
from rules import MentionRule, extract_user_id_from_args

mention_rule = MentionRule()


def register(bot: Bot):
    
    @bot.on.chat_message(text=["/get_id", "/getid", "/id", "/айди"])
    async def get_id_cmd(message: Message):
        target_id = await mention_rule(message)
        
        if not target_id:
            args = message.text.split()
            if len(args) > 1:
                target_id = extract_user_id_from_args(args, 1)
        
        from_id = message.from_id
        peer_id = message.peer_id
        chat_id = peer_id - 2000000000 if peer_id > 2000000000 else None
        message_id = message.conversation_message_id
        
        response = "🆔 **Информация об ID:**\n\n"
        response += f"👤 **Ваш ID:** `{from_id}`\n"
        
        if target_id:
            response += f"🎯 **ID цели:** `{target_id}`\n"
            response += f"🔗 **Упоминание:** @id{target_id}\n"
        
        response += f"\n💬 **ID беседы:** `{peer_id}`\n"
        if chat_id:
            response += f"📱 **Chat ID:** `{chat_id}`\n"
        
        response += f"📝 **ID сообщения:** `{message_id}`\n"
        
        await message.answer(response)
    
    
    @bot.on.chat_message(text=["/chat_id", "/чатид", "/беседа"])
    async def chat_id_cmd(message: Message):
        peer_id = message.peer_id
        chat_id = peer_id - 2000000000 if peer_id > 2000000000 else None
        
        response = f"💬 **ID беседы:** `{peer_id}`\n"
        if chat_id:
            response += f"📱 **Chat ID:** `{chat_id}`\n"
            clean_id = str(chat_id).replace('2', '', 1) if str(chat_id).startswith('2') else str(chat_id)
            response += f"🔗 **Ссылка:** https://vk.me/join/{clean_id}"
        
        await message.answer(response)
    
    
    @bot.on.chat_message(text=["/my_id", "/мойид"])
    async def my_id_cmd(message: Message):
        response = f"🆔 **Ваш ID:** `{message.from_id}`\n"
        response += f"🔗 **Упоминание:** @id{message.from_id}"
        
        try:
            user_info = await bot.api.users.get(user_ids=message.from_id)
            if user_info:
                response = f"👤 **{user_info[0].first_name} {user_info[0].last_name}**\n" + response
        except:
            pass
        
        await message.answer(response)
