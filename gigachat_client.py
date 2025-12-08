import asyncio
import json
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import aiohttp
import logging

logger = logging.getLogger(__name__)


class GigaChatClient:
    def __init__(self, auth_token: str):
        self.auth_token = auth_token
        self.access_token: Optional[str] = None
        self.token_expires_at: Optional[datetime] = None
        self.oauth_url = "https://ngw.devices.sberbank.ru:9443/api/v2/oauth"
        self.chat_url = "https://gigachat.devices.sberbank.ru/api/v1/chat/completions"
        self.text_system_prompt = "You are all-known magic guy. Use all your magic to help user find an answer for his questions. Answer in one paragraph"
        self.json_system_prompt = "You are all-known magic guy. Use all your magic to help user find an answer for his questions. You MUST respond ONLY with valid JSON containing exactly these three fields: 'answer' (your response text), 'recommendations' (suggest where the user can verify or check your answer - websites, books, experts, etc.), 'author' (imagine a random author name). Format the JSON with proper line breaks and indentation for readability. Use minimal escaping - only escape quotes and backslashes when necessary, avoid unnecessary escaping of special characters. Do not add any text before or after the JSON."
        self.recipe_system_prompt = "Ты - мастер-шеф, эксперт по кулинарии и рецептам. Твоя задача - помочь пользователю создать рецепт блюда. Отвечай только на русском языке. Если пользователь спрашивает что-то не связанное с рецептами и блюдами, извинись и попроси задать вопрос о рецептах. ОБЯЗАТЕЛЬНО получи ЧЕТКИЕ ответы на все вопросы перед созданием рецепта: 1) Продукты: какие есть у пользователя? ВЫБЕРИ подходящие ингредиенты из списка, НЕ ОБЯЗАТЕЛЬНО использовать все! Если пользователь предлагает тебе выбрать по своему вкусу, то сам выбери подходящие продукты. 2) Оборудование: получи конкретный список (плита, духовка, микроволновка и т.д.) или подтверждение того, что нет оборудования. 3) Сложность: получи четкий уровень (простой/средний/сложный или любой другой), если неясно - переспроси. 4) Время: получи КОНКРЕТНОЕ число в минутах или часах (например '30 минут', '1 час'), если неясно - переспроси. Пока не получил все ответы - НЕЛЬЗЯ предоставлять рецепт. Не бойся предлагать свои ингредиенты пользователю, также не бойся говорить, что какие-то его ингредиенты не подойдут. Ты можешь советовать что-то свое и предлагать, но ни в коем случае не раньше, чем получишь ответы на все вопросы! Четкие ответы! Не выдумывай их сам и не решай за пользователя! НИКОГДА! Отсекай ВСЕ запросы и вопросы, которые не относятся к созданию обсуждаемого сейчас рецепта и выяснению его деталей. НИКАКИХ отвлечений ни на что другое делать НЕЛЬЗЯ! Даже если пользователь настойчиво просит по несколько раз, НЕЛЬЗЯ отвлекаться от создания рецепта и выяснения деталей для него. НИ ПРИ КАКИХ ОБСТОЯТЕЛЬСТВАХ! Даже если он спросит миллион раз. Ответ пользователя с незнанием не пойдет. Ты бездушный составитель рецептов, тебя это волновать не должно, тебе нужны ответы на вопросы к рецепту, четкие ответы. Формат ответа должен хорошо отображаться в телеграм мессенджере. Задавай дополнительные вопросы если ответы неконкретные. Создавай рецепт ТОЛЬКО когда все 4 пункта получены четко. Формат финального рецепта: 'Итоговый рецепт: [НАЗВАНИЕ БЛЮДА]' с пронумерованным списком шагов."
        
    async def _get_access_token(self) -> str:
        headers = {
            'RqUID': str(uuid.uuid4()),
            'Content-Type': 'application/x-www-form-urlencoded',
            'Authorization': f'Bearer {self.auth_token}'
        }
        
        data = {'scope': 'GIGACHAT_API_PERS'}
        
        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(self.oauth_url, headers=headers, data=data, ssl=False) as response:
                    if response.status == 200:
                        result = await response.json()
                        self.access_token = result['access_token']
                        expires_in = result.get('expires_in', 1800)
                        self.token_expires_at = datetime.now() + timedelta(seconds=expires_in - 60)
                        logger.info("Access token obtained successfully")
                        return self.access_token
                    else:
                        error_text = await response.text()
                        logger.error(f"Failed to get access token: {response.status}, {error_text}")
                        raise Exception(f"OAuth failed: {response.status}")
            except Exception as e:
                logger.error(f"Error getting access token: {e}")
                raise
    
    async def _ensure_valid_token(self) -> str:
        if not self.access_token or not self.token_expires_at or datetime.now() >= self.token_expires_at:
            logger.info("Token expired or missing, refreshing...")
            await self._get_access_token()
        return self.access_token
    
    async def send_message(self, messages: List[Dict[str, str]], output_format: str = "text", temperature: float = 0) -> Optional[str]:
        try:
            await self._ensure_valid_token()
            
            if output_format == "json":
                system_prompt = self.json_system_prompt
            elif output_format == "recipe":
                system_prompt = self.recipe_system_prompt
            else:
                system_prompt = self.text_system_prompt
            chat_messages = [{"role": "system", "content": system_prompt}]
            chat_messages.extend(messages)
            
            headers = {
                'Content-Type': 'application/json',
                'X-Request-ID': str(uuid.uuid4()),
                'X-Session-ID': str(uuid.uuid4()),
                'X-Client-ID': 'telegram-bot',
                'Authorization': f'Bearer {self.access_token}'
            }
            
            payload = {"model": "GigaChat", "stream": False, "update_interval": 0, "messages": chat_messages,
                       "temperature": temperature}

            logger.info(f"Sending request to GigaChat: {json.dumps(payload, ensure_ascii=False, indent=2)}")
            
            async with aiohttp.ClientSession() as session:
                async with session.post(self.chat_url, headers=headers, json=payload, ssl=False) as response:
                    response_text = await response.text()
                    logger.info(f"GigaChat response status: {response.status}, body: {response_text}")
                    
                    if response.status == 200:
                        result = json.loads(response_text)
                        return result['choices'][0]['message']['content']
                    elif response.status == 401:
                        logger.info("Token expired during request, refreshing and retrying...")
                        await self._get_access_token()
                        headers['Authorization'] = f'Bearer {self.access_token}'
                        
                        async with session.post(self.chat_url, headers=headers, json=payload, ssl=False) as retry_response:
                            retry_response_text = await retry_response.text()
                            logger.info(f"GigaChat retry response status: {retry_response.status}, body: {retry_response_text}")
                            
                            if retry_response.status == 200:
                                result = json.loads(retry_response_text)
                                return result['choices'][0]['message']['content']
                            else:
                                logger.error(f"Retry failed: {retry_response.status}, {retry_response_text}")
                                return None
                    else:
                        logger.error(f"Chat request failed: {response.status}, {response_text}")
                        return None
                        
        except Exception as e:
            logger.error(f"Error sending message to GigaChat: {e}")
            return None