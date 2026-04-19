import asyncio
from vkbottle.bot import Bot

from config import settings
from db_mysql import init_db
from middlewares import admin_check_middleware, role_check_middleware
from commands import register_commands
from background import unmute_checker, tempban_checker

# Создаём бота
bot = Bot(token=settings.VK_TOKEN)

# Подключаем middleware
bot.labeler.message_view.register_middleware(admin_check_middleware)
bot.labeler.message_view.register_middleware(role_check_middleware)

# Регистрируем команды
register_commands(bot)


async def main():
    # Инициализируем БД
    await init_db()
    
    # Запускаем фоновые задачи
    asyncio.create_task(unmute_checker(bot))
    asyncio.create_task(tempban_checker(bot))
    
    print("✅ Бот запущен!")
    print("📋 Доступные команды: /menu, /warn, /mute, /ban, /tempban, /kick")
    print("📊 Статистика: /stats, /modstats, /history")
    
    await bot.run_polling()


if __name__ == "__main__":
    asyncio.run(main())
