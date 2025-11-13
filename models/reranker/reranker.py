from yarl import URL
from dify_plugin.interfaces.model.openai_compatible.rerank import OAICompatRerankModel


class AipingRerankModel(OAICompatRerankModel):
    """
    AIPing Rerank Model implementation
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
        query: str,
        docs: list[str],
        score_threshold: float | None = None,
        top_n: int | None = None,
        user: str | None = None,
    ):
        """
        调用 Rerank 模型

        Args:
            model: 模型名称
            credentials: 认证信息
            query: 查询文本
            docs: 文档列表
            score_threshold: 分数阈值（可选）
            top_n: 返回前 N 个结果（可选）
            user: 用户标识（可选）

        Returns:
            RerankResult
        """
        self._add_custom_parameters(credentials)
        return super()._invoke(
            model, credentials, query, docs, score_threshold, top_n, user
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
