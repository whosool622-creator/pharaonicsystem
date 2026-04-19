import asyncio
from db_mysql import get_all_expired_temp_bans, remove_temp_ban


async def tempban_checker(bot):
    """Проверяет истёкшие временные баны и разбанивает"""
    while True:
        await asyncio.sleep(30)
        
        try:
            expired = await get_all_expired_temp_bans()
            
            for user_id, peer_id, unban_time in expired:
                await remove_temp_ban(user_id, peer_id)
                
                try:
                    await bot.api.messages.add_chat_user(
                        chat_id=peer_id - 2000000000,
                        user_id=user_id
                    )
                    await bot.api.messages.send(
                        peer_id=peer_id,
                        message=f"🔓 @id{user_id}, время бана истекло. Добро пожаловать обратно!",
                        random_id=0
                    )
                except Exception as e:
                    print(f"[TempBanChecker] Не удалось добавить @id{user_id}: {e}")
                    
        except Exception as e:
            print(f"[TempBanChecker] Ошибка: {e}")
