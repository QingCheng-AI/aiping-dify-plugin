"""
AIPing 模型工具类
从 v1/models API 动态获取模型并生成 YAML 配置
"""

import logging
import os
from typing import Any, Dict, List
from yarl import URL
import requests

from config import MAX_REQUEST_TIMEOUT

logger = logging.getLogger(__name__)


def fetch_models_from_api(endpoint_url: str) -> List[Dict[str, Any]]:
    """
    从 v1/models API 端点获取模型列表

    Args:
        endpoint_url: API endpoint URL (如 https://aiping.cn/api/v1)

    Returns:
        模型列表（已过滤外部模型和不可用模型）
    """
    try:
        url = str(URL(endpoint_url) / "models")

        response = requests.get(url, timeout=MAX_REQUEST_TIMEOUT)
        response.raise_for_status()

        data = response.json()
        if not data or not isinstance(data, dict):
            return []

        models_data = data.get("data", [])
        if not models_data:
            return []

        result = []

        for model in models_data:
            model_id = model.get("id")
            model_type = model.get("model_type")
            is_foreign = model.get("is_foreign", False)
            status = model.get("status", False)

            # 跳过外部模型和不可用模型
            if is_foreign or not status:
                continue

            # 获取上下文长度
            context_range = model.get("context_length_range", [131072, 131072])
            context_size = (
                context_range[1]
                if context_range and len(context_range) >= 2
                else 131072
            )

            result.append(
                {
                    "model_name": model_id,
                    "model_type": model_type,
                    "context_size": context_size,
                }
            )

        return result
    except Exception as e:
        print(f"Failed to fetch models from v1/models: {e}")
        return []


def is_vision_model(model_type: Any) -> bool:
    """根据模型名称和类型判断是否支持视觉能力"""
    return _model_type_contains(model_type, "vlm")


def _model_type_contains(model_type: Any, target: str) -> bool:
    """检查 model_type 是否包含目标类型（支持字符串和列表类型）"""
    if model_type is None:
        return False
    if isinstance(model_type, str):
        return model_type == target
    if isinstance(model_type, list):
        return target in model_type
    return False


def generate_all_yaml_files(endpoint_url: str, base_path: str = None) -> None:
    """
    从 API 获取模型并生成所有 YAML 配置文件

    Args:
        endpoint_url: API endpoint URL
        base_path: 基础路径（插件根目录）
    """
    if base_path is None:
        base_path = os.path.dirname(os.path.dirname(__file__))

    models = fetch_models_from_api(endpoint_url)
    if not models:
        print("No models fetched from API")
        return

    # 统计
    llm_count = 0
    vlm_count = 0
    embedding_count = 0
    reranker_count = 0
    t2i_count = 0
    i2i_count = 0

    # 生成 LLM YAML 文件
    llm_path = os.path.join(base_path, "models", "llm")
    os.makedirs(llm_path, exist_ok=True)
    for f in os.listdir(llm_path):
        if f.endswith(".yaml"):
            os.remove(os.path.join(llm_path, f))

    for model in models:
        model_type = model.get("model_type")
        if _model_type_contains(model_type, "llm") or _model_type_contains(
            model_type, "vlm"
        ):
            model_name = model.get("model_name")
            context_size = model.get("context_size", 131072)
            safe_name = _make_safe_filename(model_name)
            content = _generate_llm_yaml(model_name, model_type, context_size)
            with open(
                os.path.join(llm_path, f"{safe_name}.yaml"), "w", encoding="utf-8"
            ) as f:
                f.write(content)
            if _model_type_contains(model_type, "llm"):
                llm_count += 1
            if _model_type_contains(model_type, "vlm"):
                vlm_count += 1

    # 生成 Embedding YAML 文件
    embedding_path = os.path.join(base_path, "models", "embedding")
    os.makedirs(embedding_path, exist_ok=True)
    for f in os.listdir(embedding_path):
        if f.endswith(".yaml"):
            os.remove(os.path.join(embedding_path, f))

    for model in models:
        if _model_type_contains(model.get("model_type"), "embedding"):
            model_name = model.get("model_name")
            context_size = model.get("context_size", 32768)
            safe_name = _make_safe_filename(model_name)
            content = _generate_embedding_yaml(model_name, context_size)
            with open(
                os.path.join(embedding_path, f"{safe_name}.yaml"), "w", encoding="utf-8"
            ) as f:
                f.write(content)
            embedding_count += 1

    # 生成 Reranker YAML 文件
    reranker_path = os.path.join(base_path, "models", "reranker")
    os.makedirs(reranker_path, exist_ok=True)
    for f in os.listdir(reranker_path):
        if f.endswith(".yaml"):
            os.remove(os.path.join(reranker_path, f))

    for model in models:
        if _model_type_contains(model.get("model_type"), "reranker"):
            model_name = model.get("model_name")
            context_size = model.get("context_size", 30720)
            safe_name = _make_safe_filename(model_name)
            content = _generate_reranker_yaml(model_name, context_size)
            with open(
                os.path.join(reranker_path, f"{safe_name}.yaml"), "w", encoding="utf-8"
            ) as f:
                f.write(content)
            reranker_count += 1

    # 生成文生图和图生图 Tool YAML
    _generate_tool_yaml_files(base_path, models)
    for model in models:
        model_type = model.get("model_type")
        if _model_type_contains(model_type, "text2image"):
            t2i_count += 1
        if _model_type_contains(model_type, "image2image"):
            i2i_count += 1

    # 计算去重后的总计
    type_counts = [
        llm_count,
        vlm_count,
        embedding_count,
        reranker_count,
        t2i_count,
        i2i_count,
    ]
    total = sum(type_counts)
    # 重复计数：一个模型有多个类型的情况
    duplicate = 0
    for model in models:
        model_type = model.get("model_type")
        if model_type is None:
            continue
        if isinstance(model_type, list):
            duplicate += len(model_type) - 1  # 减去1个，多的都是重复
        elif isinstance(model_type, str):
            # 字符串类型不会重复
            pass
    unique = total - duplicate

    print(f"Generated YAML files in {base_path}")
    print(
        f"  LLM: {llm_count}, VLM: {vlm_count}, Embedding: {embedding_count}, Reranker: {reranker_count}, T2I: {t2i_count}, I2I: {i2i_count}"
    )
    print(f"  Total: {total} ({duplicate} duplicates, {unique} unique)")


def _generate_tool_yaml_files(base_path: str, models: List[Dict[str, Any]]) -> None:
    """生成文生图和图生图 Tool YAML"""
    t2i_models = []
    i2i_models = []

    for model in models:
        model_type = model.get("model_type")
        model_name = model.get("model_name")

        # 图生图模型添加到 i2i_models
        if _model_type_contains(model_type, "image2image"):
            i2i_models.append(model_name)

        # 文生图模型添加到 t2i_models
        if _model_type_contains(model_type, "text2image"):
            t2i_models.append(model_name)

    t2i_yaml = _build_tool_yaml("text2image", t2i_models, "Qwen-Image")
    t2i_path = os.path.join(base_path, "tools", "text2image.yaml")
    with open(t2i_path, "w", encoding="utf-8") as f:
        f.write(t2i_yaml)

    i2i_yaml = _build_tool_yaml("image2image", i2i_models, "Qwen-Image-Edit")
    i2i_path = os.path.join(base_path, "tools", "image2image.yaml")
    with open(i2i_path, "w", encoding="utf-8") as f:
        f.write(i2i_yaml)


def _build_tool_yaml(tool_type: str, models: List[str], default_model: str) -> str:
    """构建 Tool YAML 内容"""
    options = []
    for model in models:
        options.append(
            f'''  - label:
      en_US: {model}
      zh_CN: {model}
    value: "{model}"'''
        )
    options_str = "\n".join(options)

    if tool_type == "text2image":
        return f"""description:
  human:
    en_US: Generate images with AIPing AI.
    zh_CN: 使用AIPing AI 生成图像。
  llm: This tool is used to generate images from text prompts using AIPing AI.
extra:
  python:
    source: tools/text2image.py
identity:
  author: AIping Writer
  icon: icon.svg
  label:
    en_US: Text to Image
    zh_CN: 文生图
  name: text2image
parameters:
- form: llm
  human_description:
    en_US: The text prompt used to generate the image.
    zh_CN: 用于生成图像的文本提示。
  label:
    en_US: Prompt
    zh_CN: 提示词
  llm_description: This prompt text will be used to generate image.
  name: prompt
  required: true
  type: string
- form: llm
  human_description:
    en_US: The text negative prompt used to generate the image.
    zh_CN: 用于生成图像的负向文本提示。
  label:
    en_US: Negative Prompt
    zh_CN: 负向提示词
  llm_description: This prompt text will be used to generate image.
  name: negative_prompt
  required: false
  type: string
- form: form
  human_description:
    en_US: Model to use for image generation (for details, please go to： https://aiping.cn/docs/product).
    zh_CN: 用于图像生成的模型 (详情请前往：https://aiping.cn/docs/product)。
  label:
    en_US: Model
    zh_CN: 模型
  name: model
  options:
{options_str}
  required: true
  type: select
  default: "{default_model}"
- form: form
  human_description:
    en_US: Advanced parameters for image generation (for details, please go to： https://aiping.cn/docs/product).
    zh_CN: 高级参数，用于图像生成 (详情请前往：https://aiping.cn/docs/product)。
  label:
    en_US: Extra Body
    zh_CN: Extra Body
  name: extra_body
  required: false
  type: string
  default: "{{}}"
"""
    else:
        return f"""description:
  human:
    en_US: Generate images from images with AIPing AI.
    zh_CN: 使用AIPing AI 进行图生图。
  llm: This tool is used to generate images from images and text prompts using AIPing AI.
extra:
  python:
    source: tools/image2image.py
identity:
  author: AIping Writer
  icon: icon.svg
  label:
    en_US: Image to Image
    zh_CN: 图生图
  name: image2image
parameters:
- form: llm
  human_description:
    en_US: The text prompt used to generate the image.
    zh_CN: 用于生成图像的文本提示。
  label:
    en_US: Prompt
    zh_CN: 提示词
  llm_description: This prompt text will be used to generate image.
  name: prompt
  required: true
  type: string
- form: llm
  human_description:
    en_US: The image file to be used for image-to-image generation.
    zh_CN: 用于图生图生成的图片文件。
  label:
    en_US: Image
    zh_CN: 图片文件
  llm_description: This image will be used as the input for image-to-image generation.
  name: image
  required: true
  type: file
- form: llm
  human_description:
    en_US: The text negative prompt used to generate the image.
    zh_CN: 用于生成图像的负向文本提示。
  label:
    en_US: Negative Prompt
    zh_CN: 负向提示词
  llm_description: This prompt text will be used to generate image.
  name: negative_prompt
  required: false
  type: string
- form: form
  human_description:
    en_US: Model to use for image generation (for details, please go to： https://aiping.cn/docs/product).
    zh_CN: 用于图像生成的模型 (详情请前往：https://aiping.cn/docs/product)。
  label:
    en_US: Model
    zh_CN: 模型
  name: model
  options:
{options_str}
  required: true
  type: select
  default: "{default_model}"
- form: form
  human_description:
    en_US: Advanced parameters for image generation (for details, please go to： https://aiping.cn/docs/product).
    zh_CN: 高级参数，用于图像生成 (详情请前往：https://aiping.cn/docs/product)。
  label:
    en_US: Extra Body
    zh_CN: Extra Body
  name: extra_body
  required: false
  type: string
  default: "{{}}"
"""


def _make_safe_filename(name: str) -> str:
    """生成安全的文件名"""
    name = name.replace("/", "-").replace("\\", "-").replace(" ", "-")
    return name.lower()


def _generate_llm_yaml(
    model_name: str, model_type: str, context_size: int = 131072
) -> str:
    """生成 LLM 模型 YAML"""
    is_vision = is_vision_model(model_type)

    features = ["multi-tool-call", "stream-tool-call", "tool-call"]
    if is_vision:
        features.append("vision")

    features_str = "\n".join([f"  - {f}" for f in features])

    yaml_content = f"""model: {model_name}
label:
  en_US: {model_name}
  zh_Hans: {model_name}
model_type: llm
features:
{features_str}
model_properties:
  mode: chat
  context_size: {context_size}
parameter_rules:
- name: max_tokens
  use_template: max_tokens
  type: int
  min: 1
  max: 8192
  default: 2048
- name: temperature
  use_template: temperature
  type: float
  min: 0.0
  max: 2.0
- name: top_p
  use_template: top_p
  type: float
  min: 0.0
  max: 1.0
- name: top_k
  use_template: top_k
  type: int
- name: presence_penalty
  use_template: presence_penalty
  type: float
  min: -2.0
  max: 2.0
- name: stream
  label:
    en_US: Stream
    zh_Hans: 流式输出
  type: boolean
  default: false
  required: false
  help:
    en_US: Whether to stream the response. If true, the response will be streamed back as it is generated.
    zh_Hans: 是否流式返回响应。如果为 true，响应将在生成时流式返回。
- name: modalities
  label:
    en_US: Modalities
    zh_Hans: 模态
  type: string
  required: false
  options:
  - text
  help:
    en_US: The type of output the model should generate. Most models can generate text, text is the default type
    zh_Hans: 希望模型生成的输出类型。大多数模型都可以生成文本，文本是默认类型
- name: response_format
  use_template: response_format
  type: string
  options:
  - text
  - json_object
- name: enable_thinking
  label:
    en_US: Enable Thinking
    zh_Hans: 启用思考模式
  type: boolean
  default: true
  required: false
  help:
    en_US: Whether to enable thinking mode for models that support it
    zh_Hans: 是否为支持思考模式的模型启用思考功能（部分模型可能不支持思考）
- name: sort
  label:
    en_US: Sort By
    zh_Hans: 智能路由策略
  type: string
  default: none
  required: false
  options:
  - input_price
  - output_price
  - latency
  - throughput
  - input_length
  - none
  help:
    en_US: 'Sort providers by: input_price, output_price, throughput, latency, or context_length'
    zh_Hans: 按以下方式排序供应商：input_price（输入价格）、output_price（输出价格）、throughput（吞吐量）、latency（延迟）或 context_length（上下文长度）
"""
    return yaml_content


def _generate_embedding_yaml(model_name: str, context_size: int = 32768) -> str:
    """生成 Embedding 模型 YAML"""
    return f"""model: {model_name}
label:
  en_US: {model_name}
  zh_Hans: {model_name}
model_type: text-embedding
model_properties:
  context_size: {context_size}
  max_chunks: 1
"""


def _generate_reranker_yaml(model_name: str, context_size: int = 30720) -> str:
    """生成 Reranker 模型 YAML"""
    return f"""model: {model_name}
label:
  en_US: {model_name}
  zh_Hans: {model_name}
model_type: rerank
model_properties:
  context_size: {context_size}
"""
