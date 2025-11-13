from yarl import URL
from dify_plugin.entities.model import EmbeddingInputType
from dify_plugin.interfaces.model.openai_compatible.text_embedding import (
    OAICompatEmbeddingModel,
)


class AipingTextEmbeddingModel(OAICompatEmbeddingModel):
    """
    AIPing Text Embedding Model implementation
    """

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

    def _invoke(
        self,
        model: str,
        credentials: dict,
        texts: list[str],
        user: str | None = None,
        input_type: EmbeddingInputType = EmbeddingInputType.DOCUMENT,
    ):
        """
        调用 Embedding 模型

        Args:
            model: 模型名称
            credentials: 认证信息
            texts: 文本列表
            user: 用户标识（可选）
            input_type: 输入类型（可选）

        Returns:
            TextEmbeddingResult
        """
        self._add_custom_parameters(credentials)
        return super()._invoke(model, credentials, texts, user, input_type)

    def get_num_tokens(self, model: str, credentials: dict, texts: list[str]) -> int:
        """
        获取文本数量

        Args:
            model: 模型名称
            credentials: 认证信息
            texts: 文本列表
        """
        self._add_custom_parameters(credentials)
        return super().get_num_tokens(model, credentials, texts)

    def validate_credentials(self, model: str, credentials: dict) -> None:
        """
        验证认证信息

        Args:
            model: 模型名称
            credentials: 认证信息
        """
        self._add_custom_parameters(credentials)
        super().validate_credentials(model, credentials)
