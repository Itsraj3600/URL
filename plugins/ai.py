from pyrogram import Client, filters
from services.ai_service import AIService
from info import AI


@Client.on_message(filters.private & filters.text & filters.command("ai"))
async def ai_handler(client, message):

    if not AI:
        await message.reply_text("AI is disabled.")
        return

    if len(message.command) < 2:
        await message.reply_text(
            "Usage:\n"
            "/ai your question"
        )
        return

    prompt = " ".join(message.command[1:])

    waiting = await message.reply_text("🤖 Thinking...")

    try:
        answer = await AIService.ask(prompt)
        await waiting.edit(answer)

    except Exception as e:
        await waiting.edit(f"❌ Error:\n`{e}`")