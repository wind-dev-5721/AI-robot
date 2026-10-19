# AI 智能伴侣（AI Companion）

基于 [DeepSeek](https://platform.deepseek.com) 大模型 API 的多轮对话 Web 应用，支持角色定制、上下文记忆与流式输出。使用 Python + Streamlit 开发。

## ✨ 功能特性

- **多轮对话**：基于会话状态管理历史消息，对话自然连贯
- **上下文记忆**：滑动窗口保留最近 N 轮对话，控制上下文长度（侧边栏可调）
- **角色定制**：自定义角色姓名、性格人设，修改后下一条消息即时生效
- **Prompt 工程**：系统提示词由「角色设定 + 行为准则」组装，通过"不确定就说不确定"等约束缓解幻觉
- **流式输出**：解析 SSE 增量数据，边生成边渲染（打字机效果）
- **密钥管理**：API Key 不硬编码，支持 `secrets.toml` / 环境变量两种方式

## 🛠 技术栈

Python ｜ Streamlit ｜ DeepSeek API（OpenAI 兼容协议）｜ requests ｜ Prompt 工程

## 🚀 快速开始

```bash
# 1. 克隆仓库
git clone https://github.com/wind-dev-5721/AI-robot.git
cd AI-robot

# 2. 安装依赖（建议使用虚拟环境）
python -m venv .venv
.venv\Scripts\activate        # Windows
pip install -r requirements.txt

# 3. 配置 API Key（在 DeepSeek 开放平台申请）
#    编辑 .streamlit/secrets.toml：
#    DEEPSEEK_API_KEY = "sk-xxxx"
#    （该文件已被 gitignore，不会提交到仓库）

# 4. 启动应用
streamlit run AI.py
```

浏览器自动打开 `http://localhost:8501`，在左侧边栏设置角色与参数后即可开始对话。

## 📁 项目结构

```
AI-robot/
├── AI.py                  # 应用入口：UI、对话逻辑、API 调用
├── requirements.txt       # 依赖清单
├── README.md
└── .streamlit/
    └── secrets.toml       # 本地密钥配置（已 gitignore，需自行创建）
```

## 🧠 Prompt 工程说明

系统提示词由三部分组装：

1. **角色身份**：`你是「{角色名}」，一位陪伴用户的 AI 伴侣`
2. **性格人设**：用户在侧边栏自定义的设定，如"温柔耐心的朋友，喜欢倾听"
3. **行为准则**：全局约束，例如
   - 回答简洁自然，像朋友聊天
   - 只回答确定的内容，不确定时直接说不知道（缓解幻觉）

对话时只携带「系统提示词 + 最近 N 轮消息」请求模型，实现记忆与成本之间的平衡。

## 🔭 后续规划

- **RAG**：接入知识库检索增强生成，让对话基于外部资料回答
- **后端化**：调研 SpringAI 框架，将对话能力封装为 Java 后端接口，与现有业务系统集成

## 📄 License

[MIT](LICENSE)
