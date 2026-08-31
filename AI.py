import streamlit as st

st.set_page_config(
    page_title="AI智能伴侣",      # 浏览器标签标题
    page_icon="🤖",            # 标签图标
    layout="wide",             # 布局：wide宽屏 / centered居中（默认）
    initial_sidebar_state="auto", # 侧边栏：auto / expanded展开 / collapsed收起
    menu_items={               # 右上角菜单约束
        'Get Help': None,
        'Report a bug': None,
        'About': "### 系统说明"
    }
)

#大标题
st.title("AI智能伴侣")
st.write("欢迎使用AI智能伴侣！")

