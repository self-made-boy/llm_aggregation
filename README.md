# LLM 聚合 API

这个项目用于聚合各大模型 API，包括 OpenAI、DeepSeek、Claude 等，通过一个域名加路由前缀进行区分。

## 功能特点

- 统一的 API 接口
- 支持多种 LLM 服务：OpenAI、DeepSeek、Claude 等
- 通过路由前缀区分不同的 LLM 服务
- 错误处理和日志记录

## 安装

使用 Poetry 安装依赖：

```bash
poetry install
```

导出requirements.txt
```bash
poetry export -f requirements.txt --output requirements.txt --without-hashes
```
