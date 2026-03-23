"""
LLM
OpenAI
"""

import json
import re
import time
from typing import Optional, Dict, Any, List
from openai import OpenAI, RateLimitError, APIError

from ..config import Config
from ..utils.logger import get_logger

logger = get_logger('mirofish.llm_client')

# Force all LLM outputs to be in English
ENGLISH_INSTRUCTION = "IMPORTANT: You MUST respond entirely in English. Do NOT use Chinese or any other language. All output, including analysis, reports, quotes, social media posts, comments, and any generated text must be in English only."

def _enforce_english(messages):
    """Prepend English instruction to the system message in messages list."""
    if not messages:
        return messages
    new_messages = list(messages)
    for i, msg in enumerate(new_messages):
        if msg.get("role") == "system":
            new_messages[i] = dict(msg)
            new_messages[i]["content"] = ENGLISH_INSTRUCTION + "\n\n" + msg["content"]
            return new_messages
    # If no system message, prepend one
    new_messages.insert(0, {"role": "system", "content": ENGLISH_INSTRUCTION})
    return new_messages




class LLMClient:
    """LLM"""

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        model: Optional[str] = None
    ):
        self.api_key = api_key or Config.LLM_API_KEY
        self.base_url = base_url or Config.LLM_BASE_URL
        self.model = model or Config.LLM_MODEL_NAME

        if not self.api_key:
            raise ValueError("LLM_API_KEY ")

        self.client = OpenAI(
            api_key=self.api_key,
            base_url=self.base_url
        )

    def _call_with_retry(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 4096,
        response_format: Optional[Dict] = None,
        max_retries: int = 5,
        initial_delay: float = 2.0
    ) -> str:
        """
        LLM

        429 RateLimitError。
        APIretry-after，。

        Args:
            messages: message list
            temperature: temperature parameter
            max_tokens: token
            response_format: 
            max_retries: 
            initial_delay: （）

        Returns:
            LLM
        """
        kwargs = {
            "model": self.model,
            "messages": _enforce_english(messages),
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

        if response_format:
            kwargs["response_format"] = response_format

        last_exception = None
        delay = initial_delay

        for attempt in range(max_retries + 1):
            try:
                response = self.client.chat.completions.create(**kwargs)
                content = response.choices[0].message.content
                #  (MiniMax M2.5) content<think>，
                content = re.sub(r'<think>[\s\S]*?</think>', '', content).strip()
                return content
            except RateLimitError as e:
                last_exception = e
                if attempt < max_retries:
                    #
                    wait_time = delay
                    error_msg = str(e)
                    try:
                        retry_match = re.search(r'try again in (\d+\.?\d*)\s*s', error_msg, re.IGNORECASE)
                        if retry_match:
                            wait_time = max(float(retry_match.group(1)), delay)
                    except Exception:
                        pass

                    logger.warning(
                        f"Rate limit hit (attempt {attempt + 1}/{max_retries}), "
                        f"waiting {wait_time:.1f}s before retry... Error: {error_msg}"
                    )
                    time.sleep(wait_time)
                    delay = min(delay * 2, 60.0)  # ，60
                else:
                    logger.error(f"Rate limit exceeded after {max_retries} retries: {e}")
                    raise
            except APIError as e:
                last_exception = e
                # 5xx
                if e.status_code and e.status_code >= 500 and attempt < max_retries:
                    logger.warning(
                        f"API server error {e.status_code} (attempt {attempt + 1}/{max_retries}), "
                        f"waiting {delay:.1f}s before retry..."
                    )
                    time.sleep(delay)
                    delay = min(delay * 2, 60.0)
                else:
                    raise

        raise last_exception

    def chat(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 4096,
        response_format: Optional[Dict] = None
    ) -> str:
        """
        

        Args:
            messages: message list
            temperature: temperature parameter
            max_tokens: token
            response_format: 

        Returns:
            LLM
        """
        return self._call_with_retry(
            messages=_enforce_english(messages),
            temperature=temperature,
            max_tokens=max_tokens,
            response_format=response_format
        )

    def chat_json(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.3,
        max_tokens: int = 4096
    ) -> Dict[str, Any]:
        """
        JSON

        Args:
            messages: message list
            temperature: temperature parameter
            max_tokens: token

        Returns:
            JSON
        """
        response = self._call_with_retry(
            messages=_enforce_english(messages),
            temperature=temperature,
            max_tokens=max_tokens,
            response_format={"type": "json_object"}
        )
        # markdown
        cleaned_response = response.strip()
        cleaned_response = re.sub(r'^```(?:json)?\s*\n?', '', cleaned_response, flags=re.IGNORECASE)
        cleaned_response = re.sub(r'\n?```\s*$', '', cleaned_response)
        cleaned_response = cleaned_response.strip()

        try:
            return json.loads(cleaned_response)
        except json.JSONDecodeError:
            raise ValueError(f"LLMJSON：{cleaned_response}")
