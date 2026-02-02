[中文文档](README_CN.md)

## Overview

AI Ping provides a unified API that gives you access to hundreds of AI models through a single endpoint, while automatically handling fallbacks and selecting the most cost-effective options. Get started with just a few lines of code using your preferred SDK or framework.

This Dify plugin provides access to various models (Large Language Models, text embedding, reranking, image generation, etc.), configurable via model name, API key, and other parameters.

## Installation

### Method 1: Install via Repository (Recommended)

1. Select "Github" installation method in Dify
2. Enter the repository URL
3. You'll get two separate plugin packages - Model Plugin and Tool Plugin

### Method 2: Install via Marketplace

1. Select "Marketplace" installation method in Dify
2. Search for "AIPing" in the plugin marketplace
3. Choose and install the appropriate plugin:
   - **Model Plugin**: Contains AI inference capabilities (LLM, text embedding, reranking, etc.)
   - **Tool Plugin**: Contains image generation and other tools

### Method 3: Install via Offline Package

1. Select "Local Package File" installation method in Dify
2. Download the plugin package from the Release page:
   - `aiping-dify-plugin-ai.difypkg`: Models package
   - `aiping-dify-plugin-tools.difypkg`: Tools package
3. Install the corresponding package based on your needs

#### Note

- You can install both Model Plugin and Tool Plugin simultaneously
- Each plugin requires separate API key configuration

## Configuration

After installing the AI Ping plugin, you need to configure your API key.

**Get your API Key**: Please visit [AI Ping](https://aiping.cn/user/apikey) to get your API key.

### AI Model Configuration

Configure your API key in the **Model Providers** page:

![](./_assets/aiping_models_setting.png)

### Tool Configuration

Configure your API key in the **Tools** tab:

![](./_assets/aiping_tools_setting.png)

## Related Links

- [Website](https://aiping.cn/)
- [AI Ping Quick Start](https://aiping.cn/docs/quickstart)
