from openai import AsyncOpenAI
from info import OPENAI_API

client = AsyncOpenAI(api_key=OPENAI_API)


class AIService:

    @staticmethod
    async def ask(prompt: str) -> str:
        response = await client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are CINE3600 AI, a helpful assistant integrated "
                        "inside a Telegram movie bot."
                    )
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.7,
            max_tokens=500,
        )

        return response.choices[0].message.content.strip()