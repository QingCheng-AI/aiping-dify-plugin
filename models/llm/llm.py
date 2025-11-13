import json
from collections.abc import Generator
from typing import Optional, Union
from dify_plugin.entities.model.llm import LLMMode, LLMResult
from dify_plugin.entities.model.message import PromptMessage, PromptMessageTool
from yarl import URL
from dify_plugin import OAICompatLargeLanguageModel


class AipingLargeLanguageModel(OAICompatLargeLanguageModel):
    pass

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

        # 处理 extra_body 和 stream_options
        if "extra_body" in model_parameters and isinstance(
            model_parameters["extra_body"], str
        ):
            try:
                model_parameters["extra_body"] = json.loads(
                    model_parameters["extra_body"]
                )
            except json.JSONDecodeError:
                pass  # 保持原样或抛出错误

        if "stream_options" in model_parameters and isinstance(
            model_parameters["stream_options"], str
        ):
            try:
                model_parameters["stream_options"] = json.loads(
                    model_parameters["stream_options"]
                )
            except json.JSONDecodeError:
                pass

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
