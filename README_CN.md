## 概述

AI Ping 提供统一的 API，让您通过单个端点访问数百个 AI 模型，同时自动处理故障转移并选择最具成本效益的选项。只需几行代码即可开始使用您首选的 SDK 或框架。

本 Dify 插件提供对多种模型的访问（大语言模型、文本嵌入、重排序、图片生成等），可通过模型名称、API 密钥和其他参数进行配置。

## 安装

### 方式一：通过仓库地址安装（推荐）

1. 在 Dify 中选择 "Github" 安装方式
2. 输入本仓库地址
3. 将获得模型插件和工具插件两个独立插件包，分别安装

### 方式二：通过插件市场安装

1. 在 Dify 中选择 "Marketplace" 安装方式
2. 在插件市场中搜索 "AIPing"
3. 选择相应插件进行安装：
   - **模型插件**：包含 AI 推理功能（LLM、文本嵌入、重排序等）
   - **工具插件**：包含图片生成等功能

### 方式三：通过离线包安装

1. 在 Dify 中选择 "Local Package File" 安装方式
2. 在本仓库的 Release 页面下载插件包：
   - `aiping-dify-plugin-ai.difypkg`：模型功能包
   - `aiping-dify-plugin-tools.difypkg`：工具功能包
3. 根据需要安装对应的插件包

#### 备注

- 可以同时安装模型插件和工具插件
- 插件需要单独配置 API 密钥

## 配置

安装 AI Ping 插件后，需要配置您的 API 密钥。

**API 密钥获取**：请访问 [AI Ping](https://aiping.cn/user/apikey) 获取您的 API 密钥。

### AI 模型配置

在 Dify 的 **模型供应商** 页面配置 API 密钥：

![](./_assets/aiping_models_setting.png)

### 工具配置

在 Dify 的 **工具** 标签页配置 API 密钥：

![](./_assets/aiping_tools_setting.png)

## 相关链接

- [官方网站](https://aiping.cn/)
- [AI Ping 产品文档](https://aiping.cn/docs/PlatformOverview/product)
