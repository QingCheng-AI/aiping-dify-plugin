import json
from collections.abc import Generator
from typing import Optional, Union
from dify_plugin.entities.model.llm import LLMMode, LLMResult
from dify_plugin.entities.model.message import PromptMessage, PromptMessageTool
from yarl import URL
from dify_plugin import OAICompatLargeLanguageModel


class AipingLargeLanguageModel(OAICompatLargeLanguageModel):
    def _invoke(
        self,
        model: str,
        credentials: dict,
        prompt_messages: list[PromptMessage],
        model_parameters: dict,
        tools: Optional[list[PromptMessageTool]] = None,
        stop: Optional[list[str]] = None,
        stream: bool = True,
        user: Optional[str] = None,
    ) -> Union[LLMResult, Generator]:
        """
        调用 LLM
        Args:
            model: 模型名称
            credentials: 认证信息
            prompt_messages: 提示消息列表
            model_parameters: 模型参数
            tools: 工具列表（可选）
            stop: 停止词列表（可选）
            stream: 是否流式返回
            user: 用户标识（可选）

        Returns:
            LLMResult 或 Generator
        """

        # 构建 extra_body，整合 enable_thinking 和 sort 字段
        extra_body = {}
        
        # 处理 enable_thinking 字段
        if "enable_thinking" in model_parameters:
            extra_body["enable_thinking"] = model_parameters.pop("enable_thinking")
        
        # 处理 sort 字段
        if "sort" in model_parameters:
            sort_value = model_parameters.pop("sort")
            if sort_value and sort_value != "none":
                extra_body["provider"] = {
                    "only": [],
                    "order": [],
                    "sort": sort_value,
                    "input_price_range": [],
                    "output_price_range": [],
                    "throughput_range": [],
                    "latency_range": [],
                    "input_length_range": [],
                    "allow_filter_prompt_length": True,
                    "ignore": [],
                    "allow_fallbacks": True
                }
        
        # 如果 extra_body 不为空，添加到 model_parameters
        if extra_body:
            model_parameters["extra_body"] = extra_body

        self._add_custom_parameters(credentials)
        return super()._invoke(
            model,
            credentials,
            prompt_messages,
            model_parameters,
            tools,
            stop,
            stream,
            user,
        )

    def validate_credentials(self, model: str, credentials: dict) -> None:
        """
        验证认证信息

        Args:
            model: 模型名称
            credentials: 认证信息
        """
        self._add_custom_parameters(credentials)
        super().validate_credentials(model, credentials)

    @staticmethod
    def _add_custom_parameters(credentials: dict) -> None:
        """
        添加 AIPing 特定的参数

        Args:
            credentials: 认证信息字典
        """
        credentials["endpoint_url"] = str(
            URL(credentials.get("endpoint_url", "https://aiping.cn/api/v1"))
        )
        credentials["mode"] = LLMMode.CHAT.value
