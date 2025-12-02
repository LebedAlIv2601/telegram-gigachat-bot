import asyncio
import logging
import os
from collections import defaultdict, deque
from typing import Dict, Deque, List
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
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

user_conversations: Dict[int, Deque] = defaultdict(lambda: deque(maxlen=20))
user_output_preferences: Dict[int, str] = defaultdict(lambda: "text")


def get_reply_keyboard() -> ReplyKeyboardMarkup:
    text_btn = KeyboardButton(text="📝 Text Mode")
    json_btn = KeyboardButton(text="🔧 JSON Mode")
    return ReplyKeyboardMarkup(
        keyboard=[[text_btn, json_btn]],
        resize_keyboard=True,
        persistent=True
    )


@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    await message.answer(
        "Hello! I'm a magic bot powered by GigaChat AI. Ask me anything and I'll use my magic to help you!\n\nUse the bottom menu to switch between Text and JSON output modes.",
        reply_markup=get_reply_keyboard()
    )


@dp.message()
async def handle_message(message: Message) -> None:
    user_id = message.from_user.id
    user_text = message.text
    
    # Handle mode switching via keyboard buttons
    if user_text in ["📝 Text Mode", "🔧 JSON Mode"]:
        new_mode = "text" if user_text == "📝 Text Mode" else "json"
        user_output_preferences[user_id] = new_mode
        mode_name = "Text" if new_mode == "text" else "JSON"
        await message.answer(f"Switched to {mode_name} mode", reply_markup=get_reply_keyboard())
        logger.info(f"User {user_id} switched to {new_mode} mode")
        return
    
    logger.info(f"Received message from user {user_id}: {user_text}")
    
    user_conversations[user_id].append({"role": "user", "content": user_text})
    
    messages_to_send = list(user_conversations[user_id])[-10:]
    
    try:
        thinking_message = await message.answer("Думаю...")
        
        output_format = user_output_preferences[user_id]
        response = await gigachat_client.send_message(messages_to_send, output_format)
        
        await bot.delete_message(chat_id=message.chat.id, message_id=thinking_message.message_id)
        
        if response:
            user_conversations[user_id].append({"role": "assistant", "content": response})
            
            if output_format == "json":
                formatted_response = f"```json\n{response}\n```"
                await message.answer(formatted_response, parse_mode="Markdown")
            else:
                await message.answer(response)
            
            logger.info(f"Sent {output_format} response to user {user_id}")
        else:
            await message.answer("Not available now, please, try again later")
            logger.warning(f"No response from GigaChat for user {user_id}")
            
    except Exception as e:
        logger.error(f"Error processing message for user {user_id}: {e}")
        try:
            await bot.delete_message(chat_id=message.chat.id, message_id=thinking_message.message_id)
        except:
            pass
        await message.answer("Not available now, please, try again later")




async def main() -> None:
    logger.info("Starting Telegram bot...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())