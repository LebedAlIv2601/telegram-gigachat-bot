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
    
    async def send_message(self, messages: List[Dict[str, str]], output_format: str = "text") -> Optional[str]:
        try:
            await self._ensure_valid_token()
            
            system_prompt = self.json_system_prompt if output_format == "json" else self.text_system_prompt
            chat_messages = [{"role": "system", "content": system_prompt}]
            chat_messages.extend(messages)
            
            headers = {
                'Content-Type': 'application/json',
                'X-Request-ID': str(uuid.uuid4()),
                'X-Session-ID': str(uuid.uuid4()),
                'X-Client-ID': 'telegram-bot',
                'Authorization': f'Bearer {self.access_token}'
            }
            
            payload = {
                "model": "GigaChat",
                "stream": False,
                "update_interval": 0,
                "messages": chat_messages
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(self.chat_url, headers=headers, json=payload, ssl=False) as response:
                    if response.status == 200:
                        result = await response.json()
                        return result['choices'][0]['message']['content']
                    elif response.status == 401:
                        logger.info("Token expired during request, refreshing and retrying...")
                        await self._get_access_token()
                        headers['Authorization'] = f'Bearer {self.access_token}'
                        
                        async with session.post(self.chat_url, headers=headers, json=payload, ssl=False) as retry_response:
                            if retry_response.status == 200:
                                result = await retry_response.json()
                                return result['choices'][0]['message']['content']
                            else:
                                error_text = await retry_response.text()
                                logger.error(f"Retry failed: {retry_response.status}, {error_text}")
                                return None
                    else:
                        error_text = await response.text()
                        logger.error(f"Chat request failed: {response.status}, {error_text}")
                        return None
                        
        except Exception as e:
            logger.error(f"Error sending message to GigaChat: {e}")
            return None