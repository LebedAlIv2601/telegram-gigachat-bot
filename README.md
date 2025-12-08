# Telegram Bot with GigaChat Integration

A Telegram bot that integrates with Sber's GigaChat AI to provide intelligent responses to user messages.

## Features

- 🤖 Responds to user messages using GigaChat AI
- 💬 Maintains conversation context (last 10 messages for text/json, 50 for recipes)
- 🔄 Automatic OAuth token refresh
- 🤔 Shows "Думаю..." message while processing queries
- 🛡️ Error handling and graceful degradation
- 🚀 24/7 operation scripts for Mac
- 📝 Comprehensive logging
- 📋 **Triple Output Modes**: Switch between Text, JSON, and Recipe Master formats
- ⌨️ **Persistent Bottom Menu**: Always-visible mode switching buttons
- 🎯 **Structured JSON**: Includes answer, recommendations, and author fields
- 👨‍🍳 **Recipe Master**: Expert cooking assistant creating step-by-step recipes in Russian
- 👤 **Per-User Preferences**: Each user's output format preference remembered
- 🌡️ **Temperature Control**: Adjustable GigaChat creativity via `/temperature` command (0-2.0)
- 🧹 **Conversation Management**: `/clear` command to reset chat history
- 🔧 **System Message Filtering**: Clean conversation context for AI processing

## Prerequisites

- Python 3.9+
- Telegram Bot Token (from [@BotFather](https://t.me/botfather))
- GigaChat Authorization Token (from Sber)

## Quick Setup

1. **Clone the repository:**
```bash
git clone https://github.com/yourusername/telegram-gigachat-bot.git
cd telegram-gigachat-bot
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Configure environment variables:**
```bash
cp .env.example .env
```
Edit `.env` and add your tokens:
```
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
GIGACHAT_AUTH_TOKEN=your_gigachat_auth_token
```

4. **Run the bot:**
```bash
python telegram_bot.py
```

## 24/7 Operation (Mac)

For running the bot continuously on Mac:

### Initial Setup (One Time):
```bash
./setup_mac.sh
```

### Start Bot in Background:
```bash
./start_bot.sh
```

### Management Commands:
```bash
./check_bot.sh    # Check bot status
./stop_bot.sh     # Stop the bot
./restore_sleep.sh # Restore normal sleep settings
```

### View Logs:
```bash
tail -f bot.log
```

## How to Get Tokens

### Telegram Bot Token:
1. Message [@BotFather](https://t.me/botfather) on Telegram
2. Send `/newbot`
3. Follow instructions to create your bot
4. Copy the token provided

### GigaChat Authorization Token:
1. Register at [GigaChat API](https://developers.sber.ru/portal/products/gigachat-api)
2. Get your authorization token for API access

## Configuration

- **System prompts**: Separate prompts for text, JSON, and recipe modes in `gigachat_client.py`
- **Message history**: Keeps last 10 messages for text/json, 50 for recipes per user
- **Token refresh**: Automatic OAuth token refresh every ~29 minutes
- **Output modes**: Users can switch between Text, JSON, and Recipe Master formats using bottom menu buttons

## Output Modes

### Text Mode (Default)
- Standard paragraph responses from GigaChat
- Natural conversation format

### JSON Mode
- Structured JSON responses with three fields:
  - `answer`: The AI's response text
  - `recommendations`: Sources to verify the answer (websites, books, experts)
  - `author`: Random imagined author name
- Formatted with proper line breaks for readability
- Displayed in Telegram with syntax highlighting

### Recipe Master Mode
- Russian cooking expert that creates detailed step-by-step recipes
- Greeting: "Привет! Я мастер-шеф. Что будем готовить сегодня?"
- Collects specific information before creating recipes:
  - **Available ingredients**: Selects suitable ones from your list (doesn't use all)
  - **Kitchen equipment**: Gets concrete list or confirms "no equipment"
  - **Recipe complexity**: Clear level (простой/средний/сложный)
  - **Maximum cooking time**: Specific time with units (e.g., "30 минут", "1 час")
- Only responds to cooking-related queries
- Recipe format: "Итоговый рецепт: [DISH NAME]" followed by numbered steps
- Clears conversation context after each completed recipe

## Usage

### Basic Commands
- `/start` - Initialize the bot and show welcome message
- `/temperature VALUE` - Set GigaChat creativity (0-2.0, default: 0)
  - 0 = More focused and deterministic
  - 2.0 = More creative and varied responses
- `/clear` - Clear conversation history

### Chat Modes
1. **Start chatting**: Send any message to get a response
2. **Switch modes**: Use the bottom menu buttons:
   - 📝 Text Mode: Standard text responses
   - 🔧 JSON Mode: Structured JSON with recommendations
   - 👨‍🍳 Recipe Master: Step-by-step cooking recipes in Russian
3. **Your preferences are remembered** for future conversations (until bot restart)
4. **Recipe creation**: In Recipe Master mode, answer the chef's questions about ingredients, equipment, complexity, and time to get your custom recipe

## Files Structure

```
telegram-gigachat-bot/
├── telegram_bot.py          # Main bot implementation
├── gigachat_client.py       # GigaChat API client
├── requirements.txt         # Dependencies
├── .env.example            # Environment template
├── .gitignore              # Git ignore rules
├── setup_mac.sh            # Mac 24/7 setup
├── start_bot.sh            # Start bot in background
├── stop_bot.sh             # Stop bot
├── check_bot.sh            # Check bot status
├── restore_sleep.sh        # Restore sleep settings
└── README.md               # This file
```

## Error Handling

- Returns "SYSTEM: Not available now, please, try again later" when GigaChat is unavailable
- Automatically retries requests after token refresh on 401 errors
- Comprehensive logging for debugging
- System messages are prefixed with "SYSTEM:" and filtered from AI context

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

MIT License - see LICENSE file for details

## Security Note

Never commit your `.env` file with real tokens to version control. The `.gitignore` file is configured to prevent this.