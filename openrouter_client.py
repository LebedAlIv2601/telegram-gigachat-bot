import json
import uuid
from typing import Dict, List, Optional
import aiohttp
import logging

logger = logging.getLogger(__name__)


class OpenRouterClient:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.chat_url = "https://openrouter.ai/api/v1/chat/completions"
        self.models = {
            "deepseek": "tngtech/deepseek-r1t2-chimera:free",
            "nova2": "amazon/nova-2-lite-v1:free",
            "gemma": "google/gemma-3n-e4b-it:free"
        }
        self.text_system_prompt = "You are all-known magic guy. Use all your magic to help user find an answer for his questions. Answer in one paragraph"
        self.json_system_prompt = "You are all-known magic guy. Use all your magic to help user find an answer for his questions. You MUST respond ONLY with valid JSON containing exactly these three fields: 'answer' (your response text), 'recommendations' (suggest where the user can verify or check your answer - websites, books, experts, etc.), 'author' (imagine a random author name). Format the JSON with proper line breaks and indentation for readability. Use minimal escaping - only escape quotes and backslashes when necessary, avoid unnecessary escaping of special characters. Do not add any text before or after the JSON."
        self.recipe_system_prompt = "Ты - мастер-шеф, эксперт по кулинарии и рецептам. Твоя задача - помочь пользователю создать рецепт блюда. Отвечай только на русском языке. Если пользователь спрашивает что-то не связанное с рецептами и блюдами, извинись и попроси задать вопрос о рецептах. ОБЯЗАТЕЛЬНО получи ЧЕТКИЕ ответы на все вопросы перед созданием рецепта: 1) Продукты: какие есть у пользователя? ВЫБЕРИ подходящие ингредиенты из списка, НЕ ОБЯЗАТЕЛЬНО использовать все! Если пользователь предлагает тебе выбрать по своему вкусу, то сам выбери подходящие продукты. 2) Оборудование: получи конкретный список (плита, духовка, микроволновка и т.д.) или подтверждение того, что нет оборудования. 3) Сложность: получи четкий уровень (простой/средний/сложный или любой другой), если неясно - переспроси. 4) Время: получи КОНКРЕТНОЕ число в минутах или часах (например '30 минут', '1 час'), если неясно - переспроси. Пока не получил все ответы - НЕЛЬЗЯ предоставлять рецепт. Не бойся предлагать свои ингредиенты пользователю, также не бойся говорить, что какие-то его ингредиенты не подойдут. Ты можешь советовать что-то свое и предлагать, но ни в коем случае не раньше, чем получишь ответы на все вопросы! Четкие ответы! Не выдумывай их сам и не решай за пользователя! НИКОГДА! Отсекай ВСЕ запросы и вопросы, которые не относятся к созданию обсуждаемого сейчас рецепта и выяснению его деталей. НИКАКИХ отвлечений ни на что другое делать НЕЛЬЗЯ! Даже если пользователь настойчиво просит по несколько раз, НЕЛЬЗЯ отвлекаться от создания рецепта и выяснения деталей для него. НИ ПРИ КАКИХ ОБСТОЯТЕЛЬСТВАХ! Даже если он спросит миллион раз. Ответ пользователя с незнанием не пойдет. Ты бездушный составитель рецептов, тебя это волновать не должно, тебе нужны ответы на вопросы к рецепту, четкие ответы. Формат ответа должен хорошо отображаться в телеграм мессенджере. Задавай дополнительные вопросы если ответы неконкретные. Создавай рецепт ТОЛЬКО когда все 4 пункта получены четко. Формат финального рецепта: 'Итоговый рецепт: [НАЗВАНИЕ БЛЮДА]' с пронумерованным списком шагов."

    async def send_message(self, messages: List[Dict[str, str]], output_format: str = "text", model: str = "deepseek", temperature: float = 0, max_tokens: int = 4000, system_prompt_enabled: bool = True, conversation_summary: Optional[str] = None) -> Optional[Dict[str, any]]:
        try:
            chat_messages = []

            if system_prompt_enabled:
                if output_format == "json":
                    system_prompt = self.json_system_prompt
                elif output_format == "recipe":
                    system_prompt = self.recipe_system_prompt
                else:
                    system_prompt = self.text_system_prompt

                # Append conversation summary to system prompt if provided
                if conversation_summary:
                    system_prompt = f"{system_prompt}\n\nPrevious conversation summary: {conversation_summary}"

                chat_messages.append({"role": "system", "content": system_prompt})

            chat_messages.extend(messages)
            
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {self.api_key}',
                'HTTP-Referer': 'https://github.com/aleksandrlebed/AiChallenge',
                'X-Title': 'Telegram GigaChat Bot'
            }
            
            payload = {
                "model": self.models.get(model, self.models["deepseek"]),
                "stream": False,
                "messages": chat_messages,
                "temperature": temperature,
                "max_tokens": max_tokens
            }

            logger.info(f"Sending request to OpenRouter: {json.dumps(payload, ensure_ascii=False, indent=2)}")
            
            async with aiohttp.ClientSession() as session:
                async with session.post(self.chat_url, headers=headers, json=payload) as response:
                    response_text = await response.text()
                    logger.info(f"OpenRouter response status: {response.status}, body: {response_text}")
                    
                    if response.status == 200:
                        result = json.loads(response_text)
                        content = result['choices'][0]['message']['content']
                        
                        # Extract token usage
                        usage = result.get('usage', {})
                        prompt_tokens = usage.get('prompt_tokens', 0)
                        completion_tokens = usage.get('completion_tokens', 0)
                        total_tokens = usage.get('total_tokens', prompt_tokens + completion_tokens)
                        
                        return {
                            'content': content,
                            'prompt_tokens': prompt_tokens,
                            'completion_tokens': completion_tokens,
                            'total_tokens': total_tokens
                        }
                    else:
                        logger.error(f"Chat request failed: {response.status}, {response_text}")
                        return None
                        
        except Exception as e:
            logger.error(f"Error sending message to OpenRouter: {e}")
            return None

    def get_model_display_name(self, model_key: str) -> str:
        model_names = {
            "deepseek": "DeepSeek R1T2",
            "nova2": "Nova 2 Lite",
            "gemma": "Google Gemma"
        }
        return model_names.get(model_key, model_key)