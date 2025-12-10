[中文文档](README_CN.md)

## Overview

AI Ping provides a unified API that gives you access to hundreds of AI models through a single endpoint, while automatically handling fallbacks and selecting the most cost-effective options. Get started with just a few lines of code using your preferred SDK or framework.

This Dify plugin provides access to various models (Large Language Models, text embedding, reranking, image generation, etc.), configurable via model name, API key, and other parameters.

## Installation

### Method 1: Install via Repository (Recommended - Full Features)

1. Select "Github" installation method in Dify
2. Enter the repository URL
3. You'll get the complete feature package including AI inference and image generation tools

### Method 2: Install via Marketplace

1. Select "Marketplace" installation method in Dify
2. Search for "AIPing" in the plugin marketplace
3. Choose and install the appropriate plugin:
   - **Model Plugin**: Contains AI inference capabilities (LLM, text embedding, reranking, etc.)
   - **Tool Plugin**: Contains image generation and other tools

### Method 3: Install via Offline Package

1. Select "Local Package File" installation method in Dify
2. Download the plugin package from the Release page:
   - `aiping-dify-plugin-full.difypkg`: Complete feature package
   - `aiping-dify-plugin-ai.difypkg`: Models-only package
   - `aiping-dify-plugin-tools.difypkg`: Tools-only package
3. Install the corresponding package based on your needs

#### Note
1. Starting from version V0.0.3, packages are differentiated into complete feature packages and individual function packages. Before V0.0.3, only the model plugin package aiping-dify-plugin.difypkg was available.
2. The complete feature package is only supported for installation via GitHub method on locally deployed Dify and must be installed individually, not alongside other AIPing plugin packages.
3. Individual function packages support simultaneous installation, such as installing both aiping-dify-plugin-ai.difypkg and aiping-dify-plugin-tools.difypkg together.

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