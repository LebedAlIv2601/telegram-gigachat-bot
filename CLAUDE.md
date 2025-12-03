# Project Memory - Telegram GigaChat Bot

## Project Overview
This is a Telegram bot that integrates with Sber's GigaChat AI service to provide intelligent responses to user messages. The bot maintains conversation context and includes management scripts for continuous operation. Features triple output modes (Text/JSON/Recipe Master) with persistent bottom menu navigation.

## Key Components
- **telegram_bot.py**: Main bot implementation using aiogram with triple output modes
- **gigachat_client.py**: GigaChat API client with OAuth token management and format-specific prompts
- Management scripts for Mac 24/7 operation (start_bot.sh, stop_bot.sh, check_bot.sh)

## New Features (Latest)
- **Triple Output Modes**: Text, JSON, and Recipe Master response formats
- **Persistent Bottom Menu**: "📝 Text Mode", "🔧 JSON Mode", and "👨‍🍳 Recipe Master" buttons always visible
- **Recipe Master**: Cooking expert that creates step-by-step recipes in Russian
- **JSON Structure**: Contains `answer`, `recommendations`, `author` fields
- **Per-user Preferences**: Output format stored in memory per user
- **Formatted JSON**: Multi-line with proper indentation and minimal escaping

## Development Context
- Python project using aiogram for Telegram integration
- Async/await pattern throughout
- Environment variables for sensitive tokens
- Conversation history per user (max 10 messages for text/json, 50 for recipes)
- Triple system prompts for text/json/recipe modes
- In-memory user preference storage

## Output Modes
### Text Mode
- Standard paragraph responses from GigaChat
- System prompt: "You are all-known magic guy. Use all your magic to help user find an answer for his questions. Answer in one paragraph"

### JSON Mode  
- Structured JSON response with three fields:
  - `answer`: GigaChat's response text
  - `recommendations`: Verification sources (websites, books, experts)
  - `author`: Random imagined author name
- Formatted with line breaks for readability
- Minimal character escaping

### Recipe Master Mode
- Russian cooking expert that creates step-by-step recipes
- Greeting: "Привет! Я мастер-шеф. Что будем готовить сегодня?"
- Collects required information before creating recipes:
  - Available ingredients (selects suitable ones, not all)
  - Kitchen equipment (specific list or "no equipment")
  - Recipe complexity (simple/medium/complex)
  - Maximum cooking time (specific number with units)
- Recipe format: "Итоговый рецепт: [DISH NAME]" + numbered steps
- Clears context after each recipe completion
- Only responds to cooking-related queries

## Common Commands
```bash
# Start bot
./start_bot.sh

# Check status  
./check_bot.sh

# Stop bot
./stop_bot.sh

# View logs
tail -f bot.log

# Run directly
python telegram_bot.py
```

## Dependencies
- aiogram: Telegram Bot API framework
- aiohttp: Async HTTP client
- python-dotenv: Environment variable management

## Environment Variables Required
- TELEGRAM_BOT_TOKEN
- GIGACHAT_AUTH_TOKEN

## Notes
- Bot shows "Думаю..." while processing
- Automatic token refresh every ~29 minutes
- Error handling returns "Not available now" message
- SSL disabled for GigaChat API calls
- User preferences reset on bot restart (in-memory storage)
- Default mode is "text" for new users
- Network call logging with request/response bodies
- Recipe mode maintains separate conversation history