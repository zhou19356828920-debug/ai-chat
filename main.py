import streamlit as st
# from openai import OpenAI
import ollama as o
import  json
import datetime
import os
# ollama = OpenAI(
#   api_key="dummy",
#   base_url="http://localhost:11434/v1"
# )

client = o.Client(host="http://localhost:11434")

st.set_page_config(
    page_title="AI智能伴侣",
    layout="wide",
    page_icon="😂",
    initial_sidebar_state="expanded")

def now_time():
    return datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

def save():
    if st.button("新建会话",width="stretch",icon="🐁"):
        if st.session_state.messages:
            if st.session_state.current_session:
                session_data = {"current_session":st.session_state.current_session,
                                "model_name":st.session_state.model_name,
                                "model_character":st.session_state.model_character,
                                "messages": st.session_state.messages}
                if not os.path.exists("./历史会话"):
                    os.mkdir("历史会话")
                with open(f"历史会话/{st.session_state.current_session}.json","w",encoding="utf-8") as f:
                    json.dump(session_data,f,ensure_ascii=False,indent=4)
        st.session_state.messages = []
        st.session_state.current_session = now_time()
        st.rerun()


#加载所有会话
def load_sessions():
    session_list = []
    if os.path.exists("历史会话"):
        flie_list = os.listdir("历史会话")
        for file in flie_list:
            if file.endswith(".json"):
                session_list.append(file[:-5])
    return session_list

#加载指定会话数据
def load_session(session_name):
    try:
        if os.path.exists(f"历史会话/{session_name}.json"):
            with open(f"历史会话/{session_name}.json",'r',encoding="utf-8") as f:
                json_data = json.load(f)
                st.session_state.messages = json_data["messages"]
                st.session_state.current_session = json_data["current_session"]
                st.session_state.model_name = json_data["model_name"]
                st.session_state.model_character = json_data["model_character"]
            st.rerun()
    except Exception as e:
        st.error(f"加载会话失败: {e}")
# 删除会话信息的函数
def del_session(session_name):
    try:
        if os.path.exists(f"历史会话/{session_name}.json"):
            os.remove(f"历史会话/{session_name}.json")
            if session_name == st.session_state.current_session:
                st.session_state.messages = []
                st.session_state.current_session = now_time()
            st.rerun()
    except Exception as e:
        st.error(f"删除会话失败: {e}")

st.logo('🤖')
st.title('AI智能伴侣')

#初始化聊天消息
if "messages" not in st.session_state:
  st.session_state.messages = []
#初始化名称
if "model_name" not in st.session_state:
    st.session_state.model_name = "小甜甜"
#初始化性格
if "model_character" not in st.session_state:
    st.session_state.model_character = "开放东北女孩"
if "current_session" not in st.session_state:
    st.session_state.current_session = now_time()

prompt_model = f"""
                你叫{st.session_state.model_name}，现在是用户的真实伴侣，请完全代入伴侣角色。:规则:
                1.每次只回1条消息
                2.禁止任何场景或状态描述性文字
                3.匹配用户的语言
                4.回复简短，像微信聊天一样
                5.有需要的话可以用等emoji表情6.用符合伴侣性格的方式对话
                7.回复的内容，要充分体现伴侣的性格特征
                伴侣性格:
                - {st.session_state.model_character}。
                """


# 侧边栏
# with 是streamlit里的上下文管理器
with st.sidebar:
    st.subheader("AI控制面板")

    #调用自定义函数
    save()

    st.text("历史会话")
    # 显示当前会话
    current = st.session_state.get("current_session", "")
    if current:
        st.caption(f"📍 当前: {current}")
    for session in load_sessions():
        col1,col2 = st.columns([4,1])
        with col1:
            label = f"● {session}" if session == current else session
            if st.button(label,icon="❤️",width="stretch"):
                load_session(session)
        with col2:
            if st.button("❌",key=f"del_{session}",width="stretch"):
                del_session(session)

    st.subheader("伴侣信息")
    model_name = st.text_input("伴侣名字",placeholder="请输入伴侣名字",value=st.session_state.model_name)
    if model_name:
        st.session_state.model_name = model_name
    model_character = st.text_area("伴侣性格",placeholder="请输入伴侣性格",value=st.session_state.model_character)
    if model_character:
        st.session_state.model_character = model_character




#展示历史聊天记录
for message in st.session_state.messages:
  if message["role"] =="user":
    st.chat_message(name="user",avatar="🤣").write(message["content"])
  else:
    st.chat_message(name="assistant").write(message["content"])


prompt = st.chat_input("请输入")

if prompt:
  print(*st.session_state.messages)

  # 用户输入显示
  st.chat_message("user",avatar="🤣").write(prompt)


  #上下文添加
  st.session_state.messages.append({"role" : "user" ,"content": prompt})
  # ollama协议输出
  response = client.chat(
    model="qwen3:8b",
    messages=[{"role":"system","content": prompt_model},*st.session_state.messages],
    stream=True
  )
  #输出回复 （非流式输出）
  # st.chat_message("assistant").write(response.message.content)
  #上下文添加
  # st.session_state.messages.append({"role":"assistant","content":response.message.content})
  #输出回复 (流式输出)
  response_message = st.empty()
  full_response = ""
  for temp in response:
      if temp.message.content is not None:
          full_response += temp.message.content
          response_message.chat_message("assistant").write(full_response)
  st.session_state.messages.append({"role":"assistant","content":full_response})
  if st.session_state.messages:
      if st.session_state.current_session:
          session_data = {"current_session": st.session_state.current_session,
                          "model_name": st.session_state.model_name,
                          "model_character": st.session_state.model_character,
                          "messages": st.session_state.messages}
          if not os.path.exists("./历史会话"):
              os.mkdir("历史会话")
          with open(f"历史会话/{st.session_state.current_session}.json", "w", encoding="utf-8") as f:
              json.dump(session_data, f, ensure_ascii=False, indent=4)
  # openai协议输出
#   response = ollama.chat.completions.create(
#     model="gemma3:1b",
#     messages=[
#       {"role":"system","content":"你是一个萌萌的妹子"},
#       {"role":"user","content" : prompt}
#     ]
#   )
#   st.chat_message(name="assistant",avatar="🤖").write(response.choices[0].message.content)
