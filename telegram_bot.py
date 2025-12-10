import asyncio
import logging
import os
from collections import defaultdict, deque
from typing import Dict, Deque, List
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from openrouter_client import OpenRouterClient

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TELEGRAM_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
OPENROUTER_API_KEY = os.getenv('OPENROUTER_API_KEY')

if not TELEGRAM_TOKEN or not OPENROUTER_API_KEY:
    raise ValueError("Missing required environment variables: TELEGRAM_BOT_TOKEN or OPENROUTER_API_KEY")

bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher()
openrouter_client = OpenRouterClient(OPENROUTER_API_KEY)

user_conversations: Dict[int, Deque] = defaultdict(lambda: deque(maxlen=20))
user_output_preferences: Dict[int, str] = defaultdict(lambda: "text")
user_recipe_conversations: Dict[int, Deque] = defaultdict(lambda: deque(maxlen=50))
user_recipe_info: Dict[int, Dict] = defaultdict(dict)
user_temperature_preferences: Dict[int, float] = defaultdict(lambda: 0.0)
user_model_preferences: Dict[int, str] = defaultdict(lambda: "deepseek")
user_max_tokens_preferences: Dict[int, int] = defaultdict(lambda: 4000)
user_system_prompt_preferences: Dict[int, bool] = defaultdict(lambda: True)


def filter_conversation_messages(messages: List[Dict[str, str]]) -> List[Dict[str, str]]:
    """Filter out SYSTEM messages from conversation history"""
    return [msg for msg in messages if not (msg.get("role") == "assistant" and msg.get("content", "").startswith("SYSTEM:"))]


def get_reply_keyboard() -> ReplyKeyboardMarkup:
    text_btn = KeyboardButton(text="📝 Text Mode")
    json_btn = KeyboardButton(text="🔧 JSON Mode")
    recipe_btn = KeyboardButton(text="👨‍🍳 Recipe Master")
    model_btn = KeyboardButton(text="🔄 Change Model")
    return ReplyKeyboardMarkup(
        keyboard=[[text_btn, json_btn], [recipe_btn, model_btn]],
        resize_keyboard=True,
        persistent=True
    )


@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    await message.answer(
        "SYSTEM: Hello! I'm a magic bot powered by OpenRouter AI. Ask me anything and I'll use my magic to help you!\n\nUse the bottom menu to switch between Text, JSON, Recipe modes and change AI models.",
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


@dp.message(Command("maxTokens"))
async def max_tokens_command_handler(message: Message) -> None:
    user_id = message.from_user.id
    
    # Extract max tokens value from command
    command_parts = message.text.split()
    if len(command_parts) != 2:
        current_max_tokens = user_max_tokens_preferences[user_id]
        await message.answer(f"SYSTEM: Current max tokens: {current_max_tokens}\n\nUsage: /maxTokens VALUE\nValue must be between 100 and 4000", reply_markup=get_reply_keyboard())
        return
    
    try:
        max_tokens_value = int(command_parts[1])
        if max_tokens_value < 100 or max_tokens_value > 4000:
            await message.answer("SYSTEM: Max tokens must be between 100 and 4000", reply_markup=get_reply_keyboard())
            return
        
        user_max_tokens_preferences[user_id] = max_tokens_value
        await message.answer("SYSTEM: Max tokens changed", reply_markup=get_reply_keyboard())
        logger.info(f"User {user_id} set max tokens to {max_tokens_value}")
        
    except ValueError:
        await message.answer("SYSTEM: Invalid max tokens value. Must be an integer between 100 and 4000", reply_markup=get_reply_keyboard())


@dp.message(Command("systemPrompt"))
async def system_prompt_command_handler(message: Message) -> None:
    user_id = message.from_user.id
    
    # Extract system prompt value from command
    command_parts = message.text.split()
    if len(command_parts) != 2:
        current_system_prompt = user_system_prompt_preferences[user_id]
        status = "enabled" if current_system_prompt else "disabled"
        await message.answer(f"SYSTEM: System prompt is currently {status}\n\nUsage: /systemPrompt on|off\nUse 'on' to enable system prompt, 'off' to disable", reply_markup=get_reply_keyboard())
        return
    
    value = command_parts[1].lower()
    if value not in ["on", "off"]:
        await message.answer("SYSTEM: Invalid value. Use 'on' to enable or 'off' to disable system prompt", reply_markup=get_reply_keyboard())
        return
    
    system_prompt_enabled = value == "on"
    user_system_prompt_preferences[user_id] = system_prompt_enabled
    status = "enabled" if system_prompt_enabled else "disabled"
    await message.answer(f"SYSTEM: System prompt {status}", reply_markup=get_reply_keyboard())
    logger.info(f"User {user_id} set system prompt to {system_prompt_enabled}")


@dp.message(Command("clear"))
async def clear_command_handler(message: Message) -> None:
    user_id = message.from_user.id
    user_conversations[user_id].clear()
    user_recipe_conversations[user_id].clear()
    user_recipe_info[user_id].clear()
    await message.answer("SYSTEM: Conversation history cleared", reply_markup=get_reply_keyboard())
    logger.info(f"User {user_id} cleared conversation history")


def get_model_keyboard() -> InlineKeyboardMarkup:
    deepseek_btn = InlineKeyboardButton(text="DeepSeek R1T2", callback_data="model_deepseek")
    nova2_btn = InlineKeyboardButton(text="Nova 2 Lite", callback_data="model_nova2")
    gemma_btn = InlineKeyboardButton(text="Google Gemma", callback_data="model_gemma")
    return InlineKeyboardMarkup(inline_keyboard=[[deepseek_btn], [nova2_btn], [gemma_btn]])


@dp.callback_query(lambda c: c.data and c.data.startswith("model_"))
async def handle_model_selection(callback_query: CallbackQuery) -> None:
    user_id = callback_query.from_user.id
    model_key = callback_query.data.split("_")[1]
    
    # Update user model preference
    user_model_preferences[user_id] = model_key
    
    # Clear conversation history when model changes
    user_conversations[user_id].clear()
    user_recipe_conversations[user_id].clear()
    user_recipe_info[user_id].clear()
    
    # Get model display name
    model_display_name = openrouter_client.get_model_display_name(model_key)
    
    await callback_query.answer()
    await callback_query.message.edit_text(
        f"Model selected: {model_display_name}",
        reply_markup=None
    )
    
    logger.info(f"User {user_id} changed model to {model_key} and conversation history cleared")


@dp.message()
async def handle_message(message: Message) -> None:
    user_id = message.from_user.id
    user_text = message.text
    
    # Skip temperature, maxTokens and systemPrompt commands from conversation history
    if user_text.startswith("/temperature") or user_text.startswith("/maxTokens") or user_text.startswith("/systemPrompt"):
        return
    
    # Handle mode switching and model change via keyboard buttons
    if user_text in ["📝 Text Mode", "🔧 JSON Mode", "👨‍🍳 Recipe Master", "🔄 Change Model"]:
        if user_text == "📝 Text Mode":
            new_mode = "text"
            mode_name = "Text"
            await message.answer(f"SYSTEM: Switched to {mode_name} mode", reply_markup=get_reply_keyboard())
        elif user_text == "🔧 JSON Mode":
            new_mode = "json"
            mode_name = "JSON"
            await message.answer(f"SYSTEM: Switched to {mode_name} mode", reply_markup=get_reply_keyboard())
        elif user_text == "👨‍🍳 Recipe Master":
            new_mode = "recipe"
            # Clear any previous recipe conversation
            user_recipe_conversations[user_id].clear()
            user_recipe_info[user_id].clear()
            await message.answer("Привет! Я мастер-шеф. Что будем готовить сегодня?", reply_markup=get_reply_keyboard())
        elif user_text == "🔄 Change Model":
            current_model = user_model_preferences[user_id]
            current_model_name = openrouter_client.get_model_display_name(current_model)
            await message.answer(
                f"Current model: {current_model_name}\n\nSelect a new model:",
                reply_markup=get_model_keyboard()
            )
            return
            
        if user_text != "🔄 Change Model":
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
        user_model = user_model_preferences[user_id]
        user_max_tokens = user_max_tokens_preferences[user_id]
        user_system_prompt_enabled = user_system_prompt_preferences[user_id]
        api_response = await openrouter_client.send_message(messages_to_send, output_format, user_model, user_temperature, user_max_tokens, user_system_prompt_enabled)
        
        await bot.delete_message(chat_id=message.chat.id, message_id=thinking_message.message_id)
        
        if api_response:
            response_content = api_response['content']
            token_info = f"(Prompt: {api_response['prompt_tokens']}, Response: {api_response['completion_tokens']}, Total: {api_response['total_tokens']} tokens)"
            
            if output_format == "recipe":
                user_recipe_conversations[user_id].append({"role": "assistant", "content": response_content})
                
                # Check if this is a final recipe (contains "Итоговый рецепт:")
                if "Итоговый рецепт:" in response_content:
                    response_with_tokens = f"{response_content}\n\n{token_info}"
                    await message.answer(response_with_tokens, reply_markup=get_reply_keyboard())
                    # Clear recipe context after final recipe
                    user_recipe_conversations[user_id].clear()
                    user_recipe_info[user_id].clear()
                    logger.info(f"Sent final recipe to user {user_id} and cleared context")
                else:
                    response_with_tokens = f"{response_content}\n\n{token_info}"
                    await message.answer(response_with_tokens, reply_markup=get_reply_keyboard())
                    logger.info(f"Sent recipe question/response to user {user_id}")
            else:
                # Preserve existing text/json functionality
                user_conversations[user_id].append({"role": "assistant", "content": response_content})
                
                if output_format == "json":
                    formatted_response = f"```json\n{response_content}\n```\n\n{token_info}"
                    await message.answer(formatted_response, parse_mode="Markdown", reply_markup=get_reply_keyboard())
                else:
                    response_with_tokens = f"{response_content}\n\n{token_info}"
                    await message.answer(response_with_tokens, reply_markup=get_reply_keyboard())
                
                logger.info(f"Sent {output_format} response to user {user_id}")
        else:
            await message.answer("SYSTEM: Not available now, please, try again later", reply_markup=get_reply_keyboard())
            logger.warning(f"No response from OpenRouter for user {user_id}")
            
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