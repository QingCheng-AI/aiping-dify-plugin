import os
import sys
from dify_plugin import Plugin, DifyPluginEnv
import config

# 确保工具 YAML 文件存在
plugin_dir = os.path.dirname(__file__)

# 每次都重新生成 YAML 文件
try:
    from models.aiping_models import generate_all_yaml_files
    generate_all_yaml_files(config.AIPING_BASE_URL, plugin_dir)
    print("Model YAML files generated successfully")
except Exception as e:
    print(f"Warning: Failed to generate model YAML files: {e}", file=sys.stderr)

plugin = Plugin(DifyPluginEnv(MAX_REQUEST_TIMEOUT=config.MAX_REQUEST_TIMEOUT))

if __name__ == "__main__":
    plugin.run()
