"""
LLM客户端封装
统一使用OpenAI格式调用
"""

import json
import re
import time
from typing import Optional, Dict, Any, List
from openai import OpenAI, RateLimitError, APIError

from ..config import Config
from ..utils.logger import get_logger

logger = get_logger('mirofish.llm_client')


class LLMClient:
    """LLM客户端"""

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
            raise ValueError("LLM_API_KEY 未配置")

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
        带重试逻辑的LLM调用

        对429 RateLimitError使用指数退避重试。
        如果API返回了retry-after头，优先使用该值。

        Args:
            messages: 消息列表
            temperature: 温度参数
            max_tokens: 最大token数
            response_format: 响应格式
            max_retries: 最大重试次数
            initial_delay: 初始重试延迟（秒）

        Returns:
            LLM响应内容字符串
        """
        kwargs = {
            "model": self.model,
            "messages": messages,
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
                # 部分模型 (如MiniMax M2.5) 会在content中包含<think>思考内容，需要移除
                content = re.sub(r'<think>[\s\S]*?</think>', '', content).strip()
                return content
            except RateLimitError as e:
                last_exception = e
                if attempt < max_retries:
                    # 尝试从错误信息中解析建议等待时间
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
                    delay = min(delay * 2, 60.0)  # 指数退避，最大60秒
                else:
                    logger.error(f"Rate limit exceeded after {max_retries} retries: {e}")
                    raise
            except APIError as e:
                last_exception = e
                # 对5xx服务端错误也进行重试
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
        发送聊天请求

        Args:
            messages: 消息列表
            temperature: 温度参数
            max_tokens: 最大token数
            response_format: 响应格式

        Returns:
            LLM响应内容字符串
        """
        return self._call_with_retry(
            messages=messages,
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
        发送聊天请求并返回JSON

        Args:
            messages: 消息列表
            temperature: 温度参数
            max_tokens: 最大token数

        Returns:
            解析后的JSON对象
        """
        response = self._call_with_retry(
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            response_format={"type": "json_object"}
        )
        # 清理markdown代码块标记
        cleaned_response = response.strip()
        cleaned_response = re.sub(r'^```(?:json)?\s*\n?', '', cleaned_response, flags=re.IGNORECASE)
        cleaned_response = re.sub(r'\n?```\s*$', '', cleaned_response)
        cleaned_response = cleaned_response.strip()

        try:
            return json.loads(cleaned_response)
        except json.JSONDecodeError:
            raise ValueError(f"LLM返回的JSON格式无效：{cleaned_response}")
