---
title: First Agent Template
emoji: ⚡
colorFrom: pink
colorTo: yellow
sdk: gradio
sdk_version: 5.49.1
app_file: app.py
pinned: false
tags:
- smolagents
- agent
- smolagent
- tool
- agent-course
---

# First Agent Template：使用 DeepSeek

本项目用 smolagents 的 `CodeAgent` 管理“生成代码 → 执行工具 → 观察结果 → 返回答案”的循环，
用 Gradio 展示执行过程。模型通过 DeepSeek API 调用，网页和工具在本机运行。
不需要启动 Ollama，也不需要部署 Hugging Face Space；DeepSeek API 按实际 token 用量计费。

## 本地运行

需要 Python 3.10 或以上，建议使用 Python 3.12。项目统一使用 `.venv`；
本机该环境已重建为 Python 3.12，旧 Python 3.9 环境保存在 `.venv-python39-backup-*`。
首次安装时，在项目目录执行：

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
cp -n .env.example .env
```

在本机编辑 `.env`，填入自己的 Key：

```dotenv
DEEPSEEK_API_KEY=你的DeepSeek密钥
DEEPSEEK_MODEL=deepseek-flash
```

`.env` 已加入 Git 忽略规则。也可以直接设置同名环境变量，环境变量优先于 `.env`。
IDE 的 Python 解释器应选择 `.venv/bin/python`。

在 PyCharm 中，打开 Settings → Python → Interpreter（部分版本在 Project 下），
选择 Add Interpreter → Add Local Interpreter → Python（复用已有环境），
指定项目内的 `.venv/bin/python`。Run → Edit Configurations 中的 `app`
也应选择该解释器或项目默认解释器。不要把虚拟环境的 `site-packages` 标记为 Sources Root。
如果重建环境后 IDE 仍显示旧 Python 版本或导入标红，重新打开项目以刷新解释器索引。

启动应用：

```bash
.venv/bin/python app.py
```

打开终端显示的本地地址（通常为 http://127.0.0.1:7860；端口被占用时会自动选择后续端口）。
应用启动时会自动将 `127.0.0.1,localhost,::1` 加入本进程的 `NO_PROXY` 和 `no_proxy`，
使 Gradio 的本地启动检查直连。已有代理例外和外部 HTTP(S) 代理配置会保留，Clash 可以保持开启。

先尝试：

- “请使用 Python 计算 123 × 456，并返回结果。”
- “请调用 get_current_time_in_timezone 查询 Asia/Shanghai 的当前时间，用中文回答。”

## 接入方式

`app.py` 的 `create_agent()` 从环境变量或 `.env` 读取 Key，然后配置：

- 适配器：`OpenAIServerModel`，对应固定的 `smolagents==1.13.0`。
- API 地址：`https://api.deepseek.com`。
- 默认模型：`deepseek-flash`，可通过 `DEEPSEEK_MODEL` 修改。
- 使用非思考模式，便于旧版适配器处理多轮普通聊天消息。
- 注册工具：`final_answer` 和 `get_current_time_in_timezone`。
- 最多 6 轮行动，每次生成上限为 2048 tokens；一条任务可能调用模型多次。

`OpenAIServerModel` 表示采用 OpenAI 兼容协议，实际请求发给 DeepSeek。
工具执行结果会作为后续模型请求的一部分发送给 DeepSeek。

为匹配 1.13.0，入口使用库自带的完整提示词和 `GradioUI`：项目原有的 `prompts.yaml`
缺少最终答案兜底配置，旧 `Gradio_UI.py` 尚未适配 `FinalAnswerStep`。
这两个课程文件保留作学习参考，当前入口不再加载它们。`agent.json` 也不是入口读取的配置。
原来启动时下载远程图片生成工具的步骤已移除，示例占位工具仍保留但未注册。

## 常见问题

- 缺少 `DEEPSEEK_API_KEY`：检查 `.env` 是否位于 `app.py` 同一目录，且值不为空。
- HTTP 401：检查 Key 是否有效。
- HTTP 402：检查 DeepSeek 账户可用余额。
- 本地 `/gradio_api/startup-events` 返回 502：通常是 Gradio 自检请求经过了代理。
  当前入口已自动配置本地地址绕过代理；修改代码后应停止旧进程再重新运行。
- 导入 `OpenAIServerModel` 失败或找不到 `smolagents`：确认 IDE/终端使用项目内的 `.venv/bin/python`，
  并用 `.venv/bin/python -m pip install -r requirements.txt` 安装指定版本。
- `cannot import name '_imaging' from 'PIL'`：检查是否混用了不同 Python 版本的依赖目录。
  移除 IDE 中指向虚拟环境 `site-packages` 的 Sources Root，项目和运行配置统一使用 `.venv/bin/python`。
- 达到最大步数或代码解析失败：查看界面中的模型输出和工具日志，先用上面的简单任务验证。

官方文档：[首次调用 API](https://api-docs.deepseek.com/zh-cn/)、
[模型与价格](https://api-docs.deepseek.com/zh-cn/quick_start/pricing/)。
