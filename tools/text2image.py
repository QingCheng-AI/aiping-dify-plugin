import base64
import re
import json
import requests
from urllib.parse import urlparse
from collections.abc import Generator
from dify_plugin.entities.tool import ToolInvokeMessage
from dify_plugin import Tool
import config


class Text2ImageTool(Tool):
    def _invoke(
        self, tool_parameters: dict
    ) -> Generator[ToolInvokeMessage, None, None]:
        """
        Invoke text-to-image generation tool
        """
        base_url = self.runtime.credentials.get("endpoint_url")

        if not base_url:
            base_url = "https://aiping.cn/api/v1"

        api_key = self.runtime.credentials.get("api_key")

        url_router = "/images/generations"

        model = tool_parameters.get("model", "Qwen-Image")

        prompt = tool_parameters.get("prompt", "")
        if not prompt:
            yield self.create_text_message("请输入提示词")
            return

        negative_prompt = tool_parameters.get("negative_prompt", "模糊，低质量")

        extra_body = json.loads(tool_parameters.get("extra_body", "{}"))

        try:
            yield self.create_text_message("正在使用AIPing API 生成图像...")

            url = base_url + url_router
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            }

            data = {
                "model": model,
                "input": {"prompt": prompt, "negative_prompt": negative_prompt},
                "extra_body": extra_body,
            }

            response = requests.post(
                url, headers=headers, json=data, timeout=config.MAX_REQUEST_TIMEOUT
            )

            response.encoding = "utf8"

            result = response.json()

            if response.status_code != 200:
                yield self.create_text_message(f"生成图像时出错: {str(result)}")

            images = result.get("data")
            if not images:
                yield self.create_text_message(f"生成图像时出错: 图像列表为{images}")

            # 处理结果
            for image in images:
                image = image.get("url")

                if not isinstance(image, str):
                    yield self.create_text_message(
                        f"生成图像时出错: 图片类型不是string {image}"
                    )
                    continue

                if not image.strip():
                    continue

                # 解码图像
                (mime_type, blob_image) = self._decode_image(image)

                # 创建二进制消息
                yield self.create_blob_message(
                    blob=blob_image, meta={"mime_type": mime_type}
                )
                yield self.create_text_message("图像生成成功！")

        except Exception as e:
            # 处理异常
            yield self.create_text_message(f"生成图像时出错: {str(e)}")

    @staticmethod
    def _decode_image(image_input: str) -> tuple[str, bytes]:
        """
        Decode an image from various input formats:
        - Pure base64 string (e.g., "iVBORw...")
        - Data URL (e.g., "data:image/png;base64,iVBORw...")
        - HTTP/HTTPS URL (e.g., "https://example.com/image.jpg")

        Returns:
            tuple: (mime_type: str, image_bytes: bytes)
        """
        # Case 1: Data URL (starts with "data:")
        if image_input.startswith("data:"):
            # Example: data:image/png;base64,iVBORw...
            match = re.match(r"data:(?P<mime>[^;]+);base64,(?P<data>.+)", image_input)
            if not match:
                raise ValueError("Invalid data URL format")
            mime_type = match.group("mime")
            b64_data = match.group("data")
            image_bytes = base64.b64decode(b64_data)
            return mime_type, image_bytes

        # Case 2: HTTP/HTTPS URL
        parsed = urlparse(image_input)
        if parsed.scheme in ("http", "https"):
            try:
                response = requests.get(image_input, timeout=30)
                response.raise_for_status()

                # Try to get MIME type from Content-Type header
                mime_type = response.headers.get("content-type", "image/unknown")
                # Normalize common types
                if mime_type.startswith("image/"):
                    return mime_type, response.content
                else:
                    # Fallback: try to infer from extension
                    ext = parsed.path.lower().split(".")[-1]
                    mime_map = {
                        "jpg": "image/jpeg",
                        "jpeg": "image/jpeg",
                        "png": "image/png",
                        "gif": "image/gif",
                        "webp": "image/webp",
                    }
                    mime_type = mime_map.get(ext, "image/unknown")
                    return mime_type, response.content
            except Exception as e:
                raise ValueError(f"Failed to fetch image from URL: {e}")

        # Case 3: Assume pure base64 string
        try:
            image_bytes = base64.b64decode(image_input, validate=True)
            # Default to PNG if unknown (or you could return "image/unknown")
            return "image/png", image_bytes
        except Exception as e:
            raise ValueError(
                f"Input is not a valid base64 string, data URL, or image URL: {e}"
            )
