import time
from typing import Optional
from db_mysql import execute, fetch_all


class ActionType:
    WARN = "warn"
    DELWARN = "delwarn"
    CLEARWARNS = "clearwarns"
    MUTE = "mute"
    UNMUTE = "unmute"
    KICK = "kick"
    BAN = "ban"
    UNBAN = "unban"
    TEMPBAN = "tempban"
    ROLE_ADD = "role_add"
    ROLE_REMOVE = "role_remove"
    CLEAN = "clean"
    PURGE = "purge"


class HistoryManager:
    
    @staticmethod
    async def add_entry(
        peer_id: int,
        moderator_id: int,
        target_id: int,
        action_type: str,
        reason: Optional[str] = None,
        duration: Optional[int] = None
    ) -> None:
        await execute(
            """INSERT INTO moderation_history 
               (peer_id, moderator_id, target_id, action_type, reason, duration, timestamp) 
               VALUES (%s, %s, %s, %s, %s, %s, %s)""",
            (peer_id, moderator_id, target_id, action_type, reason, duration, time.time())
        )
    
    @staticmethod
    async def get_user_history(user_id: int, peer_id: int, limit: int = 20) -> list:
        return await fetch_all(
            """SELECT moderator_id, action_type, reason, duration, timestamp 
               FROM moderation_history 
               WHERE target_id = %s AND peer_id = %s 
               ORDER BY timestamp DESC LIMIT %s""",
            (user_id, peer_id, limit)
        )
    
    @staticmethod
    async def get_moderator_actions(moderator_id: int, peer_id: int, limit: int = 50) -> list:
        return await fetch_all(
            """SELECT target_id, action_type, reason, duration, timestamp 
               FROM moderation_history 
               WHERE moderator_id = %s AND peer_id = %s 
               ORDER BY timestamp DESC LIMIT %s""",
            (moderator_id, peer_id, limit)
        )
    
    @staticmethod
    async def get_stats(peer_id: int, days: int = 7) -> dict:
        since = time.time() - (days * 86400)
        
        action_stats = await fetch_all(
            """SELECT action_type, COUNT(*) as count 
               FROM moderation_history 
               WHERE peer_id = %s AND timestamp > %s 
               GROUP BY action_type""",
            (peer_id, since)
        )
        
        top_moderators = await fetch_all(
            """SELECT moderator_id, COUNT(*) as count 
               FROM moderation_history 
               WHERE peer_id = %s AND timestamp > %s 
               GROUP BY moderator_id 
               ORDER BY count DESC LIMIT 10""",
            (peer_id, since)
        )
        
        return {
            "action_stats": {row[0]: row[1] for row in action_stats},
            "top_moderators": top_moderators,
            "period_days": days
        }
