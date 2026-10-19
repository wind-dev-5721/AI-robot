"""AI 智能伴侣 —— 基于 DeepSeek 大模型 API 的多轮对话应用。

功能特性：
- 多轮对话与上下文记忆（滑动窗口，保留最近 N 轮）
- 角色姓名、性格人设定制（侧边栏即时生效）
- Prompt 工程：角色设定 + 行为准则 + 幻觉约束
- 流式输出：解析 SSE 增量，边生成边渲染
"""
import json
import os

import requests
import streamlit as st

# ---------- 基础配置 ----------
API_URL = "https://api.deepseek.com/chat/completions"
MODEL = "deepseek-chat"

# 行为约束（Prompt 工程：语境约束 + 缓解幻觉）
BEHAVIOR_RULES = [
    "回答简洁自然，像朋友聊天，不要使用列表或分点。",
    "只回答你确定的内容；不确定或不知道时，直接说不知道，不要编造。",
    "始终以设定角色的身份和口吻说话。",
]

st.set_page_config(
    page_title="AI 智能伴侣",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="auto",
    menu_items={
        "Get Help": None,
        "Report a bug": None,
        "About": "### AI 智能伴侣\n基于 DeepSeek API 的多轮对话应用，开源地址见 README。",
    },
)


# ---------- 工具函数 ----------
def load_api_key() -> str:
    """优先读 Streamlit secrets，其次读环境变量，避免密钥硬编码进代码。"""
    return st.secrets.get("DEEPSEEK_API_KEY") or os.environ.get("DEEPSEEK_API_KEY", "")


def build_system_prompt(name: str, persona: str) -> str:
    """Prompt 工程：把角色设定与行为约束组装成系统提示词。"""
    return (
        f"你是「{name}」，一位陪伴用户的 AI 伴侣。\n"
        f"你的人设：{persona}\n"
        "行为准则：\n"
        + "\n".join(f"- {rule}" for rule in BEHAVIOR_RULES)
    )


def chat_stream(api_key: str, messages: list[dict], temperature: float):
    """调用 DeepSeek API（OpenAI 兼容协议），逐段产出回复文本。

    使用 stream=True 获取 SSE 流，逐行解析增量内容，
    边生成边交给前端渲染，实现打字机效果。
    """
    payload = {
        "model": MODEL,
        "messages": messages,
        "temperature": temperature,
        "stream": True,
    }
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    with requests.post(API_URL, json=payload, headers=headers, stream=True, timeout=60) as resp:
        resp.raise_for_status()
        for line in resp.iter_lines():
            if not line:
                continue
            line = line.decode("utf-8")
            if not line.startswith("data:"):
                continue
            data = line[len("data:"):].strip()
            if data == "[DONE]":
                break
            try:
                delta = json.loads(data)["choices"][0]["delta"].get("content")
            except (json.JSONDecodeError, KeyError, IndexError):
                continue
            if delta:
                yield delta


# ---------- 侧边栏：角色与参数定制 ----------
with st.sidebar:
    st.header("角色设定")
    persona_name = st.text_input("角色名", value="小智")
    persona_desc = st.text_area(
        "性格人设",
        value="温柔耐心的朋友，喜欢倾听，会记住聊过的内容，偶尔开个小玩笑。",
    )
    st.header("对话参数")
    temperature = st.slider("回复随机性", 0.0, 1.5, 0.7, 0.1,
                            help="越高越天马行空，越低越严谨")
    memory_rounds = st.slider("记忆轮数", 1, 10, 6,
                              help="保留最近 N 轮对话作为上下文（滑动窗口）")
    if st.button("清空对话", width="stretch"):
        st.session_state.messages = []
        st.rerun()
    st.divider()
    st.caption("基于 DeepSeek API ｜ 开源项目")

# ---------- 会话状态初始化 ----------
if "messages" not in st.session_state:
    st.session_state.messages = []

# ---------- 主界面 ----------
st.title("AI 智能伴侣")
st.caption(f"当前角色：{persona_name} ｜ 记忆 {memory_rounds} 轮 ｜ 修改角色与参数后下一条消息即生效")

api_key = load_api_key()
if not api_key:
    st.warning(
        "尚未配置 DeepSeek API Key。请在 `.streamlit/secrets.toml` 中写入：\n\n"
        "```toml\nDEEPSEEK_API_KEY = \"sk-xxxx\"\n```\n\n"
        "或设置环境变量 `DEEPSEEK_API_KEY` 后重启应用。",
        title="缺少 API Key",
    )
    st.stop()

# 渲染历史消息
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# 处理新输入
if prompt := st.chat_input("和 TA 聊点什么…", submit_mode="disable"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    # 滑动窗口：只把最近 N 轮对话发给模型，控制上下文长度
    window = st.session_state.messages[-(memory_rounds * 2):]
    api_messages = [
        {"role": "system", "content": build_system_prompt(persona_name, persona_desc)},
        *window,
    ]

    with st.chat_message("assistant"):
        try:
            reply = st.write_stream(chat_stream(api_key, api_messages, temperature))
        except Exception as exc:
            reply = "（抱歉，我刚刚走神了，请再说一次～）"
            st.error(f"请求失败：{exc}")
        st.session_state.messages.append({"role": "assistant", "content": reply})
