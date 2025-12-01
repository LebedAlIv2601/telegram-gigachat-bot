import asyncio
import logging
import os
from collections import defaultdict, deque
from typing import Dict, Deque, List
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiogram.types import Message
from gigachat_client import GigaChatClient

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TELEGRAM_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
GIGACHAT_AUTH_TOKEN = os.getenv('GIGACHAT_AUTH_TOKEN')

if not TELEGRAM_TOKEN or not GIGACHAT_AUTH_TOKEN:
    raise ValueError("Missing required environment variables: TELEGRAM_BOT_TOKEN or GIGACHAT_AUTH_TOKEN")

bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher()
gigachat_client = GigaChatClient(GIGACHAT_AUTH_TOKEN)

user_conversations: Dict[int, Deque] = defaultdict(lambda: deque(maxlen=10))


@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    await message.answer("Hello! I'm a magic bot powered by GigaChat AI. Ask me anything and I'll use my magic to help you!")


@dp.message()
async def handle_message(message: Message) -> None:
    user_id = message.from_user.id
    user_text = message.text
    
    logger.info(f"Received message from user {user_id}: {user_text}")
    
    user_conversations[user_id].append({"role": "user", "content": user_text})
    
    messages_to_send = list(user_conversations[user_id])[-5:]
    
    try:
        response = await gigachat_client.send_message(messages_to_send)
        
        if response:
            user_conversations[user_id].append({"role": "assistant", "content": response})
            await message.answer(response)
            logger.info(f"Sent response to user {user_id}")
        else:
            await message.answer("Not available now, please, try again later")
            logger.warning(f"No response from GigaChat for user {user_id}")
            
    except Exception as e:
        logger.error(f"Error processing message for user {user_id}: {e}")
        await message.answer("Not available now, please, try again later")


async def main() -> None:
    logger.info("Starting Telegram bot...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())