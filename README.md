# Telegram Bot with OpenRouter AI Integration

A powerful Telegram bot that integrates with OpenRouter API to provide intelligent responses using multiple AI models including DeepSeek R1T2, Nova 2 Lite, and Google Gemma.

## Features

- 🤖 **Multi-Model AI**: Choose between DeepSeek R1T2, Nova 2 Lite, and Google Gemma models
- 🔄 **Model Switching**: Easy model selection via inline buttons with conversation history clearing
- 💬 **Conversation Context**: Maintains chat history (10 messages for text/json, 50 for recipes)
- 📊 **Token Usage Tracking**: Displays prompt, response, and total token counts for each interaction
- 🤔 Shows "Думаю..." message while processing queries
- 🛡️ **Error Handling**: Graceful degradation and comprehensive logging
- 🚀 **24/7 Operation**: Scripts for Mac background operation
- 📋 **Triple Output Modes**: Switch between Text, JSON, and Recipe Master formats
- ⌨️ **Persistent Bottom Menu**: Always-visible mode and model switching buttons
- 🎯 **Structured JSON**: Includes answer, recommendations, and author fields
- 👨‍🍳 **Recipe Master**: Expert cooking assistant creating step-by-step recipes in Russian
- 👤 **Per-User Preferences**: Each user's settings remembered (model, temperature, tokens, mode)
- 🌡️ **Temperature Control**: Adjustable AI creativity via `/temperature` command (0-2.0)
- 🎛️ **Token Limit Control**: Set maximum response tokens via `/maxTokens` command (100-4000)
- 🎭 **System Prompt Toggle**: Enable/disable system prompts via `/systemPrompt on|off`
- 🧹 **Conversation Management**: `/clear` command to reset chat history
- 🔧 **System Message Filtering**: Clean conversation context for AI processing

## Available AI Models

- **DeepSeek R1T2** (tngtech/deepseek-r1t2-chimera:free) - Default model, reasoning-focused
- **Nova 2 Lite** (amazon/nova-2-lite-v1:free) - Amazon's efficient language model
- **Google Gemma** (google/gemma-3n-e4b-it:free) - Google's instruction-tuned model

## Prerequisites

- Python 3.9+
- Telegram Bot Token (from [@BotFather](https://t.me/botfather))
- OpenRouter API Key (from [OpenRouter](https://openrouter.ai/))

## Quick Setup

1. **Clone the repository:**
```bash
git clone https://github.com/yourusername/telegram-openrouter-bot.git
cd telegram-openrouter-bot
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
OPENROUTER_API_KEY=your_openrouter_api_key
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

### OpenRouter API Key:
1. Visit [OpenRouter](https://openrouter.ai/)
2. Sign up for an account
3. Generate an API key in your dashboard
4. Copy the API key (starts with `sk-or-v1-`)

## Configuration

- **System prompts**: Separate prompts for text, JSON, and recipe modes in `openrouter_client.py`
- **Message history**: Keeps last 10 messages for text/json, 50 for recipes per user
- **Output modes**: Users can switch between Text, JSON, and Recipe Master formats using bottom menu buttons
- **Model selection**: Switch between three AI models with automatic conversation clearing
- **Token usage**: All responses show detailed token consumption information

## Output Modes

### Text Mode (Default)
- Standard paragraph responses from selected AI model
- Natural conversation format
- Configurable system prompt for consistent behavior

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
- `/temperature VALUE` - Set AI creativity (0-2.0, default: 0)
  - 0 = More focused and deterministic
  - 2.0 = More creative and varied responses
- `/maxTokens VALUE` - Set maximum response tokens (100-4000, default: 4000)
  - Controls response length and API costs
- `/systemPrompt on|off` - Enable/disable system prompts (default: on)
  - Disable for raw model responses without context
- `/clear` - Clear conversation history

### Chat Modes
1. **Start chatting**: Send any message to get a response
2. **Switch modes**: Use the bottom menu buttons:
   - 📝 Text Mode: Standard text responses
   - 🔧 JSON Mode: Structured JSON with recommendations
   - 👨‍🍳 Recipe Master: Step-by-step cooking recipes in Russian
   - 🔄 Change Model: Select between DeepSeek R1T2, Nova 2 Lite, or Google Gemma
3. **Your preferences are remembered** for future conversations (until bot restart)
4. **Model selection**: Choose your preferred AI model for different tasks
5. **Token tracking**: Monitor usage with detailed token counts in each response
6. **Recipe creation**: In Recipe Master mode, answer the chef's questions about ingredients, equipment, complexity, and time to get your custom recipe

## Files Structure

```
telegram-openrouter-bot/
├── telegram_bot.py          # Main bot implementation with multi-model support
├── openrouter_client.py     # OpenRouter API client with token tracking
├── requirements.txt         # Dependencies
├── .env.example            # Environment template
├── .gitignore              # Git ignore rules
├── setup_mac.sh            # Mac 24/7 setup
├── start_bot.sh            # Start bot in background
├── stop_bot.sh             # Stop bot
├── check_bot.sh            # Check bot status
├── restore_sleep.sh        # Restore sleep settings
├── CLAUDE.md               # Project memory and development notes
└── README.md               # This file
```

## Error Handling

- Returns "SYSTEM: Not available now, please, try again later" when OpenRouter is unavailable
- Comprehensive logging for debugging with request/response tracking
- System messages are prefixed with "SYSTEM:" and filtered from AI context
- Automatic conversation clearing when switching models to prevent context confusion

## Token Usage and Costs

- All responses display token usage: `(Prompt: X, Response: Y, Total: Z tokens)`
- Control response length with `/maxTokens` to manage costs
- Free tier models available through OpenRouter
- Monitor usage through detailed logging

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

MIT License - see LICENSE file for details

## Security Note

Never commit your `.env` file with real tokens to version control. The `.gitignore` file is configured to prevent this.