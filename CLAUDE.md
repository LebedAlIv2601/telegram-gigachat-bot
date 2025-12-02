# Project Memory - Telegram GigaChat Bot

## Project Overview
This is a Telegram bot that integrates with Sber's GigaChat AI service to provide intelligent responses to user messages. The bot maintains conversation context and includes management scripts for continuous operation. Features dual output modes (Text/JSON) with persistent bottom menu navigation.

## Key Components
- **telegram_bot.py**: Main bot implementation using aiogram with dual output modes
- **gigachat_client.py**: GigaChat API client with OAuth token management and format-specific prompts
- Management scripts for Mac 24/7 operation (start_bot.sh, stop_bot.sh, check_bot.sh)

## New Features (Latest)
- **Dual Output Modes**: Text and JSON response formats
- **Persistent Bottom Menu**: "📝 Text Mode" and "🔧 JSON Mode" buttons always visible
- **JSON Structure**: Contains `answer`, `recommendations`, `author` fields
- **Per-user Preferences**: Output format stored in memory per user
- **Formatted JSON**: Multi-line with proper indentation and minimal escaping

## Development Context
- Python project using aiogram for Telegram integration
- Async/await pattern throughout
- Environment variables for sensitive tokens
- Conversation history per user (max 10 messages)
- Dual system prompts for text/json modes
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