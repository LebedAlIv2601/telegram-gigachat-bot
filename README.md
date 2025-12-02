# Telegram Bot with GigaChat Integration

A Telegram bot that integrates with Sber's GigaChat AI to provide intelligent responses to user messages.

## Features

- 🤖 Responds to user messages using GigaChat AI
- 💬 Maintains conversation context (last 10 messages per user)
- 🔄 Automatic OAuth token refresh
- 🤔 Shows "Думаю..." message while processing queries
- 🛡️ Error handling and graceful degradation
- 🚀 24/7 operation scripts for Mac
- 📝 Comprehensive logging
- 📋 **Dual Output Modes**: Switch between Text and JSON response formats
- ⌨️ **Persistent Bottom Menu**: Always-visible mode switching buttons
- 🎯 **Structured JSON**: Includes answer, recommendations, and author fields
- 👤 **Per-User Preferences**: Each user's output format preference remembered

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

- **System prompts**: Separate prompts for text and JSON modes in `gigachat_client.py`
- **Message history**: Keeps last 10 messages per user for context
- **Token refresh**: Automatic OAuth token refresh every ~29 minutes
- **Output modes**: Users can switch between Text and JSON formats using bottom menu buttons

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

## Usage

1. **Start chatting**: Send any message to get a response
2. **Switch modes**: Use the bottom menu buttons:
   - 📝 Text Mode: Standard text responses
   - 🔧 JSON Mode: Structured JSON with recommendations
3. **Your preference is remembered** for future conversations

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

- Returns "Not available now, please, try again later" when GigaChat is unavailable
- Automatically retries requests after token refresh on 401 errors
- Comprehensive logging for debugging

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

MIT License - see LICENSE file for details

## Security Note

Never commit your `.env` file with real tokens to version control. The `.gitignore` file is configured to prevent this.