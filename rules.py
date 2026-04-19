import re
from vkbottle.bot import Message


class MentionRule:
    async def __call__(self, message: Message):
        if hasattr(message, 'mention') and message.mention.fwd:
            return message.mention.id
        
        if match := re.search(r"\[id(\d+)\|", message.text):
            return int(match.group(1))
        
        return None


def extract_user_id_from_args(args: list, index: int = 0) -> int | None:
    if len(args) <= index:
        return None
    
    arg = args[index]
    
    if match := re.search(r"\[id(\d+)\|", arg):
        return int(match.group(1))
    
    if arg.isdigit():
        return int(arg)
    
    return None
