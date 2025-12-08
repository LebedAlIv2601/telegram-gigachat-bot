import asyncio
import logging
import os
from collections import defaultdict, deque
from typing import Dict, Deque, List
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart, Command
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
user_recipe_conversations: Dict[int, Deque] = defaultdict(lambda: deque(maxlen=50))
user_recipe_info: Dict[int, Dict] = defaultdict(dict)
user_temperature_preferences: Dict[int, float] = defaultdict(lambda: 0.0)


def filter_conversation_messages(messages: List[Dict[str, str]]) -> List[Dict[str, str]]:
    """Filter out SYSTEM messages from conversation history"""
    return [msg for msg in messages if not (msg.get("role") == "assistant" and msg.get("content", "").startswith("SYSTEM:"))]


def get_reply_keyboard() -> ReplyKeyboardMarkup:
    text_btn = KeyboardButton(text="📝 Text Mode")
    json_btn = KeyboardButton(text="🔧 JSON Mode")
    recipe_btn = KeyboardButton(text="👨‍🍳 Recipe Master")
    return ReplyKeyboardMarkup(
        keyboard=[[text_btn, json_btn], [recipe_btn]],
        resize_keyboard=True,
        persistent=True
    )


@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    await message.answer(
        "SYSTEM: Hello! I'm a magic bot powered by GigaChat AI. Ask me anything and I'll use my magic to help you!\n\nUse the bottom menu to switch between Text and JSON output modes.",
        reply_markup=get_reply_keyboard()
    )


@dp.message(Command("temperature"))
async def temperature_command_handler(message: Message) -> None:
    user_id = message.from_user.id
    
    # Extract temperature value from command
    command_parts = message.text.split()
    if len(command_parts) != 2:
        current_temp = user_temperature_preferences[user_id]
        await message.answer(f"SYSTEM: Current temperature: {current_temp}\n\nUsage: /temperature VALUE\nValue must be between 0 and 2.0", reply_markup=get_reply_keyboard())
        return
    
    try:
        temperature_value = float(command_parts[1])
        if temperature_value < 0 or temperature_value > 2.0:
            await message.answer("SYSTEM: Temperature must be between 0 and 2.0", reply_markup=get_reply_keyboard())
            return
        
        user_temperature_preferences[user_id] = temperature_value
        await message.answer("SYSTEM: Temperature changed", reply_markup=get_reply_keyboard())
        logger.info(f"User {user_id} set temperature to {temperature_value}")
        
    except ValueError:
        await message.answer("SYSTEM: Invalid temperature value. Must be a number between 0 and 2.0", reply_markup=get_reply_keyboard())


@dp.message(Command("clear"))
async def clear_command_handler(message: Message) -> None:
    user_id = message.from_user.id
    user_conversations[user_id].clear()
    user_recipe_conversations[user_id].clear()
    user_recipe_info[user_id].clear()
    await message.answer("SYSTEM: Conversation history cleared", reply_markup=get_reply_keyboard())
    logger.info(f"User {user_id} cleared conversation history")


@dp.message()
async def handle_message(message: Message) -> None:
    user_id = message.from_user.id
    user_text = message.text
    
    # Skip temperature commands from conversation history
    if user_text.startswith("/temperature"):
        return
    
    # Handle mode switching via keyboard buttons
    if user_text in ["📝 Text Mode", "🔧 JSON Mode", "👨‍🍳 Recipe Master"]:
        if user_text == "📝 Text Mode":
            new_mode = "text"
            mode_name = "Text"
            await message.answer(f"SYSTEM: Switched to {mode_name} mode", reply_markup=get_reply_keyboard())
        elif user_text == "🔧 JSON Mode":
            new_mode = "json"
            mode_name = "JSON"
            await message.answer(f"SYSTEM: Switched to {mode_name} mode", reply_markup=get_reply_keyboard())
        else:  # Recipe Master
            new_mode = "recipe"
            # Clear any previous recipe conversation
            user_recipe_conversations[user_id].clear()
            user_recipe_info[user_id].clear()
            await message.answer("Привет! Я мастер-шеф. Что будем готовить сегодня?", reply_markup=get_reply_keyboard())
            
        user_output_preferences[user_id] = new_mode
        logger.info(f"User {user_id} switched to {new_mode} mode")
        return
    
    logger.info(f"Received message from user {user_id}: {user_text}")
    
    output_format = user_output_preferences[user_id]
    
    if output_format == "recipe":
        # Handle recipe mode
        user_recipe_conversations[user_id].append({"role": "user", "content": user_text})
        messages_to_send = filter_conversation_messages(list(user_recipe_conversations[user_id]))
    else:
        # Handle text/json modes (preserve existing functionality)
        user_conversations[user_id].append({"role": "user", "content": user_text})
        filtered_messages = filter_conversation_messages(list(user_conversations[user_id]))
        messages_to_send = filtered_messages[-10:]
    
    try:
        thinking_message = await message.answer("Думаю...")
        
        user_temperature = user_temperature_preferences[user_id]
        response = await gigachat_client.send_message(messages_to_send, output_format, user_temperature)
        
        await bot.delete_message(chat_id=message.chat.id, message_id=thinking_message.message_id)
        
        if response:
            if output_format == "recipe":
                user_recipe_conversations[user_id].append({"role": "assistant", "content": response})
                
                # Check if this is a final recipe (contains "Итоговый рецепт:")
                if "Итоговый рецепт:" in response:
                    await message.answer(response, reply_markup=get_reply_keyboard())
                    # Clear recipe context after final recipe
                    user_recipe_conversations[user_id].clear()
                    user_recipe_info[user_id].clear()
                    logger.info(f"Sent final recipe to user {user_id} and cleared context")
                else:
                    await message.answer(response, reply_markup=get_reply_keyboard())
                    logger.info(f"Sent recipe question/response to user {user_id}")
            else:
                # Preserve existing text/json functionality
                user_conversations[user_id].append({"role": "assistant", "content": response})
                
                if output_format == "json":
                    formatted_response = f"```json\n{response}\n```"
                    await message.answer(formatted_response, parse_mode="Markdown", reply_markup=get_reply_keyboard())
                else:
                    await message.answer(response, reply_markup=get_reply_keyboard())
                
                logger.info(f"Sent {output_format} response to user {user_id}")
        else:
            await message.answer("SYSTEM: Not available now, please, try again later", reply_markup=get_reply_keyboard())
            logger.warning(f"No response from GigaChat for user {user_id}")
            
    except Exception as e:
        logger.error(f"Error processing message for user {user_id}: {e}")
        try:
            await bot.delete_message(chat_id=message.chat.id, message_id=thinking_message.message_id)
        except:
            pass
        await message.answer("SYSTEM: Not available now, please, try again later", reply_markup=get_reply_keyboard())




async def main() -> None:
    logger.info("Starting Telegram bot...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())