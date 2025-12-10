# Project Memory - Telegram OpenRouter AI Bot

## Project Overview
This is a Telegram bot that integrates with OpenRouter API to provide intelligent responses using multiple AI models. The bot maintains conversation context and includes management scripts for continuous operation. Features triple output modes (Text/JSON/Recipe Master) with persistent bottom menu navigation and model selection.

## Key Components
- **telegram_bot.py**: Main bot implementation using aiogram with triple output modes and model selection
- **openrouter_client.py**: OpenRouter API client with multiple model support and token usage tracking
- Management scripts for Mac 24/7 operation (start_bot.sh, stop_bot.sh, check_bot.sh)

## New Features (Latest)
- **Model Selection**: Switch between DeepSeek R1T2, Nova 2 Lite, and Google Gemma models via "🔄 Change Model" button
- **Token Usage Tracking**: All responses include token usage info (prompt/response/total tokens)
- **Per-user Model Preferences**: Selected model persists per user until bot restart
- **Triple Output Modes**: Text, JSON, and Recipe Master response formats
- **Persistent Bottom Menu**: "📝 Text Mode", "🔧 JSON Mode", "👨‍🍳 Recipe Master", and "🔄 Change Model" buttons
- **Recipe Master**: Cooking expert that creates step-by-step recipes in Russian
- **JSON Structure**: Contains `answer`, `recommendations`, `author` fields
- **Per-user Preferences**: Output format and model selection stored in memory per user
- **Formatted JSON**: Multi-line with proper indentation and minimal escaping
- **Temperature Control**: Per-user temperature setting (0-2.0) via `/temperature` command
- **Max Tokens Control**: Per-user maximum response tokens (100-4000) via `/maxTokens` command
- **System Prompt Toggle**: Enable/disable system prompts via `/systemPrompt on|off` command
- **Conversation Management**: `/clear` command to reset conversation history; model changes also clear history
- **System Message Filtering**: SYSTEM messages excluded from AI context

## Development Context
- Python project using aiogram for Telegram integration
- Async/await pattern throughout
- Environment variables for sensitive tokens
- Conversation history per user (max 10 messages for text/json, 50 for recipes)
- Triple system prompts for text/json/recipe modes
- In-memory user preference storage (output format, model selection, temperature, max tokens, system prompt toggle)
- Available AI Models: DeepSeek R1T2 (tngtech/deepseek-r1t2-chimera:free), Nova 2 Lite (amazon/nova-2-lite-v1:free), Google Gemma (google/gemma-3n-e4b-it:free)
- Default model: DeepSeek R1T2

## Output Modes
### Text Mode
- Standard paragraph responses from selected AI model
- System prompt: "You are all-known magic guy. Use all your magic to help user find an answer for his questions. Answer in one paragraph"

### JSON Mode  
- Structured JSON response with three fields:
  - `answer`: AI model's response text
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

## Bot Commands
- `/start` - Initialize bot and show welcome message
- `/temperature VALUE` - Set AI temperature (0-2.0, default: 0)
- `/maxTokens VALUE` - Set maximum response tokens (100-4000, default: 4000)
- `/systemPrompt on|off` - Enable/disable system prompts (default: on)
- `/clear` - Clear conversation history for current user

## Management Commands
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
- OPENROUTER_API_KEY

## Notes
- Bot shows "Думаю..." while processing
- Error handling returns "SYSTEM: Not available now" message
- User preferences reset on bot restart (in-memory storage)
- Default mode is "text", default model is "deepseek", default temperature is 0, default max tokens is 4000, default system prompt is enabled
- Network call logging with request/response bodies
- Recipe mode maintains separate conversation history
- All bot system messages prefixed with "SYSTEM:" and filtered from AI model context
- Temperature, maxTokens, systemPrompt and system messages excluded from conversation history
- Per-user preferences (model, temperature, max tokens, system prompt toggle, output format) persist until bot restart
- All responses include token usage information in format: (Prompt: X, Response: Y, Total: Z tokens)
- Model changes clear conversation history automatically