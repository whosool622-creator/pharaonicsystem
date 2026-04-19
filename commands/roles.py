from vkbottle.bot import Bot, Message
from models.role import RoleManager, RoleLevel, ROLE_NAMES
from models.history import HistoryManager, ActionType
from rules import MentionRule, extract_user_id_from_args
from utils import format_time

mention_rule = MentionRule()


def register(bot: Bot):
    
    @bot.on.chat_message(text=["/role", "/роль"])
    async def role_cmd(message: Message):
        args = message.text.split()
        
        if len(args) < 2:
            return await message.answer(
                "📋 **Управление ролями:**\n"
                "/role add @user [moderator/admin] — назначить\n"
                "/role remove @user — снять\n"
                "/role list — список\n"
                "/role info @user — роль пользователя"
            )
        
        subcmd = args[1].lower()
        
        if subcmd in ["add", "remove"]:
            if not await RoleManager.check_permission(message.from_id, message.peer_id, "role_add"):
                return await message.answer("⛔ Недостаточно прав")
        
        if subcmd == "add":
            if len(args) < 4:
                return await message.answer("❌ Формат: /role add @user moderator")
            
            user_id = extract_user_id_from_args(args, 2)
            if not user_id:
                return await message.answer("❌ Укажите пользователя")
            
            role_str = args[3].lower()
            role_map = {
                "moderator": RoleLevel.MODERATOR,
                "модератор": RoleLevel.MODERATOR,
                "mod": RoleLevel.MODERATOR,
                "admin": RoleLevel.ADMIN,
                "админ": RoleLevel.ADMIN,
                "администратор": RoleLevel.ADMIN
            }
            
            if role_str not in role_map:
                return await message.answer("❌ Доступные роли: moderator, admin")
            
            new_role = role_map[role_str]
            current_role = await RoleManager.get_role(user_id, message.peer_id)
            
            if current_role == RoleLevel.FOUNDER:
                return await message.answer("❌ Нельзя изменить роль Основателя")
            
            if new_role == RoleLevel.ADMIN:
                user_role = await RoleManager.get_role(message.from_id, message.peer_id)
                if user_role < RoleLevel.ADMIN:
                    return await message.answer("❌ Только Основатель или Админ могут назначать Админов")
            
            await RoleManager.set_role(user_id, message.peer_id, new_role, message.from_id)
            
            await HistoryManager.add_entry(
                message.peer_id, message.from_id, user_id,
                ActionType.ROLE_ADD, f"Назначена роль: {ROLE_NAMES[new_role]}"
            )
            
            await message.answer(f"✅ @id{user_id} назначен: {ROLE_NAMES[new_role]}")
        
        elif subcmd == "remove":
            user_id = extract_user_id_from_args(args, 2) if len(args) > 2 else await mention_rule(message)
            if not user_id:
                return await message.answer("❌ Укажите пользователя: /role remove @user")
            
            current_role = await RoleManager.get_role(user_id, message.peer_id)
            if current_role == RoleLevel.FOUNDER:
                return await message.answer("❌ Нельзя снять роль Основателя")
            
            await RoleManager.remove_role(user_id, message.peer_id)
            
            await HistoryManager.add_entry(
                message.peer_id, message.from_id, user_id,
                ActionType.ROLE_REMOVE, f"Снята роль: {ROLE_NAMES[current_role]}"
            )
            
            await message.answer(f"✅ Роль @id{user_id} снята. Теперь: {ROLE_NAMES[RoleLevel.USER]}")
        
        elif subcmd == "list":
            roles = await RoleManager.get_all_roles(message.peer_id)
            if not roles:
                return await message.answer("📋 В беседе нет назначенных ролей")
            
            response = "📋 **Список ролей:**\n\n"
            for user_id, role_level, assigned_by, assigned_at in roles[:20]:
                response += f"@id{user_id} — {ROLE_NAMES[RoleLevel(role_level)]}\n"
                response += f"   Назначил: @id{assigned_by}\n"
                response += f"   Дата: {format_time(assigned_at)}\n\n"
            
            await message.answer(response)
        
        elif subcmd == "info":
            user_id = extract_user_id_from_args(args, 2) if len(args) > 2 else await mention_rule(message)
            if not user_id:
                user_id = message.from_id
            
            role = await RoleManager.get_role(user_id, message.peer_id)
            await message.answer(f"👤 @id{user_id}\n📌 Роль: {ROLE_NAMES[role]}")
        
        else:
            await message.answer("❌ Неизвестная подкоманда. Используйте: add, remove, list, info")
