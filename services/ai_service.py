import logging

logger = logging.getLogger(__name__)

# Make OpenAI import optional
try:
    from openai import AsyncOpenAI
    from info import OPENAI_API
    
    client = AsyncOpenAI(api_key=OPENAI_API) if OPENAI_API else None
    AI_ENABLED = client is not None
except ImportError:
    logger.warning("OpenAI package not installed. AI features will be disabled.")
    client = None
    AI_ENABLED = False
except Exception as e:
    logger.warning(f"Failed to initialize OpenAI client: {e}. AI features will be disabled.")
    client = None
    AI_ENABLED = False


class AIService:

    @staticmethod
    async def ask(prompt: str) -> str:
        if not AI_ENABLED or client is None:
            logger.warning("AI service is not available. Returning default message.")
            return "AI service is currently unavailable. Please try again later."
        
        try:
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
        except Exception as e:
            logger.error(f"Error calling OpenAI API: {e}")
            return "An error occurred while processing your request."
