import asyncio
from db_mysql import get_all_active_mutes, remove_mute


async def unmute_checker(bot):
    """Проверяет истёкшие муты и размучивает пользователей"""
    while True:
        await asyncio.sleep(10)
        
        try:
            expired = await get_all_active_mutes()
            
            for user_id, peer_id, unmute_time in expired:
                await remove_mute(user_id, peer_id)
                
                try:
                    await bot.api.messages.send(
                        peer_id=peer_id,
                        message=f"🔊 @id{user_id}, время мута истекло. Можешь снова писать.",
                        random_id=0
                    )
                except:
                    pass
                    
        except Exception as e:
            print(f"[UnmuteChecker] Ошибка: {e}")
