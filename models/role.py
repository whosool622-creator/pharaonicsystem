from enum import IntEnum
from dataclasses import dataclass
from typing import Set
import time
from db_mysql import fetch_one, fetch_all, execute_and_commit, execute


class RoleLevel(IntEnum):
    USER = 1
    MODERATOR = 2
    ADMIN = 3
    FOUNDER = 4


@dataclass
class Role:
    level: RoleLevel
    name: str
    permissions: Set[str]
    
    def has_permission(self, permission: str) -> bool:
        return permission in self.permissions


ROLE_PERMISSIONS = {
    RoleLevel.USER: {
        "info", "get_id", "chat_id", "my_id", "menu"
    },
    RoleLevel.MODERATOR: {
        "warn", "warns", "delwarn", "clearwarns",
        "mute", "unmute", "kick",
        "info", "get_id", "chat_id", "my_id", "menu",
        "history", "modstats_self"
    },
    RoleLevel.ADMIN: {
        "warn", "warns", "delwarn", "clearwarns",
        "mute", "unmute", "kick", "ban", "unban", "tempban",
        "info", "get_id", "chat_id", "my_id", "menu",
        "history", "modstats", "modstats_self",
        "clean", "purge", "pin", "unpin",
        "role_add", "role_remove", "roles_list"
    },
    RoleLevel.FOUNDER: {
        "warn", "warns", "delwarn", "clearwarns",
        "mute", "unmute", "kick", "ban", "unban", "tempban",
        "info", "get_id", "chat_id", "my_id", "menu",
        "history", "modstats", "modstats_self",
        "clean", "purge", "pin", "unpin",
        "role_add", "role_remove", "roles_list", "role_set_founder"
    }
}

ROLE_NAMES = {
    RoleLevel.USER: "👤 Пользователь",
    RoleLevel.MODERATOR: "🛡 Модератор",
    RoleLevel.ADMIN: "👑 Администратор",
    RoleLevel.FOUNDER: "⭐ Основатель"
}


class RoleManager:
    
    @staticmethod
    async def get_role(user_id: int, peer_id: int) -> RoleLevel:
        result = await fetch_one(
            "SELECT role_level FROM roles WHERE user_id = %s AND peer_id = %s",
            (user_id, peer_id)
        )
        return RoleLevel(result[0]) if result else RoleLevel.USER
    
    @staticmethod
    async def set_role(user_id: int, peer_id: int, role: RoleLevel, assigned_by: int) -> None:
        await execute(
            "INSERT INTO roles (user_id, peer_id, role_level, assigned_by, assigned_at) VALUES (%s, %s, %s, %s, %s) "
            "ON DUPLICATE KEY UPDATE role_level = VALUES(role_level), assigned_by = VALUES(assigned_by), assigned_at = VALUES(assigned_at)",
            (user_id, peer_id, role.value, assigned_by, time.time())
        )
    
    @staticmethod
    async def remove_role(user_id: int, peer_id: int) -> None:
        await execute(
            "DELETE FROM roles WHERE user_id = %s AND peer_id = %s",
            (user_id, peer_id)
        )
    
    @staticmethod
    async def get_all_roles(peer_id: int) -> list:
        return await fetch_all(
            "SELECT user_id, role_level, assigned_by, assigned_at FROM roles WHERE peer_id = %s ORDER BY role_level DESC",
            (peer_id,)
        )
    
    @staticmethod
    async def check_permission(user_id: int, peer_id: int, permission: str) -> bool:
        role = await RoleManager.get_role(user_id, peer_id)
        return permission in ROLE_PERMISSIONS.get(role, set())
    
    @staticmethod
    async def is_founder(user_id: int, peer_id: int) -> bool:
        role = await RoleManager.get_role(user_id, peer_id)
        return role == RoleLevel.FOUNDER
