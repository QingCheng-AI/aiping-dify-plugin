import base64
import re
import json
import requests
from urllib.parse import urlparse
from collections.abc import Generator
from dify_plugin.entities.tool import ToolInvokeMessage
from dify_plugin import Tool
import config
import traceback

class Image2ImageTool(Tool):
    def _encode_image(self, file_data):
        """将图片文件编码为base64"""
        try:
            # 记录图片大小
            image_size = len(file_data) / 1024  # KB
            encoded = base64.b64encode(file_data).decode("utf-8")
            encoded_size = len(encoded) / 1024  # KB
            debug_info = f"图片编码完成: 原始大小={image_size:.2f}KB, 编码后大小={encoded_size:.2f}KB"
            return encoded, debug_info
        except Exception as e:
            stack_trace = traceback.format_exc()
            raise Exception(f"图片编码失败: {str(e)}\n堆栈跟踪: {stack_trace}")
        
    def _invoke(
        self, tool_parameters: dict
    ) -> Generator[ToolInvokeMessage, None, None]:
        """
        Invoke text-to-image generation tool
        """
        base_url = self.runtime.credentials.get("endpoint_url")

        print(base_url)

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

        image_file = tool_parameters.get("image")
        print(image_file)
        if not image_file:
            yield self.create_text_message("请上传图片")
            return

        # 处理图片文件
        try:
            # 处理不同类型的图片输入
            file_content = None

            
            # 检查文件类型并获取文件内容
            if hasattr(image_file, 'url') and image_file.url:
                # 如果文件是通过URL提供的
                file_url = image_file.url
                yield self.create_text_message(f"正在从URL获取图片: {file_url[:30]}...")
                try:
                    response = requests.get(file_url, timeout=60)
                    response.raise_for_status()
                    file_content = response.content
                    yield self.create_text_message(f"成功下载图片: 大小={len(file_content)/1024:.2f}KB")
                except Exception as e:
                    yield self.create_text_message(f"从URL下载图片失败: {str(e)}")
                    return
            
            # 如果URL下载失败或没有URL，尝试其他方法
            if file_content is None and hasattr(image_file, 'blob'):
                try:
                    file_content = image_file.blob
                    yield self.create_text_message(f"从blob属性获取文件数据: 大小={len(image_file.blob)/1024:.2f}KB")
                except Exception as e:
                    yield self.create_text_message(f"获取blob属性失败: {str(e)}")
            
            # 尝试从read方法获取
            if file_content is None and hasattr(image_file, 'read'):
                try:
                    file_content = image_file.read()
                    yield self.create_text_message("从可读对象获取文件数据")
                    # 如果是文件对象，可能需要重置文件指针
                    if hasattr(image_file, 'seek'):
                        image_file.seek(0)
                except Exception as e:
                    yield self.create_text_message(f"从read方法获取文件数据失败: {str(e)}")
            
            # 尝试作为文件路径处理
            if file_content is None and isinstance(image_file, str):
                try:
                    with open(image_file, 'rb') as f:
                        file_content = f.read()
                    yield self.create_text_message(f"从文件路径获取文件数据: {image_file}, 大小={len(file_content)/1024:.2f}KB")
                except (TypeError, IOError) as e:
                    yield self.create_text_message(f"从文件路径获取文件数据失败: {str(e)}")
            
            # 尝试本地文件缓存方式
            if file_content is None and hasattr(image_file, 'path'):
                try:
                    with open(image_file.path, 'rb') as f:
                        file_content = f.read()
                    yield self.create_text_message(f"从本地缓存路径获取文件数据: {image_file.path}, 大小={len(file_content)/1024:.2f}KB")
                except (TypeError, IOError) as e:
                    yield self.create_text_message(f"从本地缓存路径获取文件数据失败: {str(e)}")
            
            # 如果所有方法都失败
            if file_content is None:
                yield self.create_text_message("无法获取图片数据。请尝试重新上传图片或使用较小的图片文件")
                return
            
            # 编码图片数据为base64
            try:
                encoded_image, encoding_debug = self._encode_image(file_content)
                yield self.create_text_message(encoding_debug)
                
                # 构建图片URL (AIPing API需要可访问的URL或base64数据)
                image_data_url = f"data:image/png;base64,{encoded_image}"
            except Exception as e:
                yield self.create_text_message(f"图片编码失败: {str(e)}")
                return
                
        except Exception as e:
            stack_trace = traceback.format_exc()
            yield self.create_text_message(f"处理图片文件失败: {str(e)}\n堆栈跟踪:\n{stack_trace}")
            return

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
                "input": {"prompt": prompt, "negative_prompt": negative_prompt, "image": image_data_url},
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
