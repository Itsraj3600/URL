from cinebot import Cine3600Bot
from pyrogram import filters

@Cine3600Bot.on_message(filters.all)
async def debug(client, message):
    print(
        f"UPDATE: chat={message.chat.id} "
        f"type={message.chat.type} "
        f"text={message.text}"
    )