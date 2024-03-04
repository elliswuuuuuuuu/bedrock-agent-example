import streamlit as st
import json
from datetime import datetime
import boto3


agent_id = ""
agent_alias_id = ""

client = boto3.client("bedrock-agent-runtime")
#response = client.prepare_agent(agentId=agent_id)

# App title
st.set_page_config(page_title="bedrock agent solution guide")

with st.sidebar:
    st.title('智能订票助手测试')
    st.subheader('Parameters')
    language = st.radio("Choose a language",('english', 'chinese', 'chinese-tc'))
    model_id = st.radio("Choose a model",('Claude Instant v1.3', 'Claude v2',
                                          'Claude v2.1'))
    

st.write("## Bedrock Agent Solution Guide")


# Store LLM generated responses
if "messages" not in st.session_state.keys():
    # st.session_state.messages = [{"role": "assistant", "content": "Hello,How may I assist you today?"}]
    if language == 'english':
        st.session_state.messages = [{"role": "assistant", "content": "How may I assist you today?"}]
    elif language == 'chinese':
        st.session_state.messages = [{"role": "assistant", "content": "您好，请问有什么可以帮助您吗?"}]
    elif language == 'chinese-tc':
        st.session_state.messages = [{"role": "assistant", "content": "您好，請問有什麽可以幫助您嗎?"}]
        
    now = datetime.now()
    timestamp = datetime.timestamp(now)
    st.session_state.sessionId = 'qa'+str(timestamp)

# Display or clear chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

def clear_chat_history():
    if language == 'english':
        st.session_state.messages = [{"role": "assistant", "content": "How may I assist you today?"}]
    elif language == 'chinese':
        st.session_state.messages = [{"role": "assistant", "content": "您好，请问有什么可以帮助您吗?"}]
    elif language == 'chinese-tc':
        st.session_state.messages = [{"role": "assistant", "content": "您好，請問有什麽可以幫助您嗎?"}]

    now = datetime.now()
    timestamp = datetime.timestamp(now)
    st.session_state.sessionId = 'qa'+str(timestamp)
st.sidebar.button('Clear Chat History', on_click=clear_chat_history)


def invoke(question: str, enable_trace=False):
    enable_trace = True
    print("sessionId:", st.session_state.sessionId)
    final_answer = ""
    response = client.invoke_agent(
        inputText=question, # 输入文本
        agentId=agent_id,  # 创建的 Agent 的 ID
        agentAliasId=agent_alias_id, # 创建的 Agent alias id
        sessionId=st.session_state.sessionId, # 当前会话的session id
        enableTrace=enable_trace # 是否打开 trace
    )
    event_stream = response['completion']
    try:
        for event in event_stream:
            # print(event)
            if 'chunk' in event:
                data = event['chunk']['bytes']
                final_answer = data.decode('utf8')
                print(f"Final answer ->\n{final_answer}")
                end_event_received = True
                # End event indicates that the request finished successfully
            elif 'trace' in event:
                trace = event['trace']
                print("trace:", json.dumps(event['trace']))
            else:
                raise Exception("unexpected event.", event)
    except Exception as e:
        raise Exception("unexpected event.", e)

    return final_answer


# User-provided prompt
if prompt := st.chat_input():
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

# Generate a new response if last message is not from assistant
if st.session_state.messages[-1]["role"] != "assistant":
    answer = ''
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            placeholder = st.empty()
            try:
                answer = invoke(prompt)
                placeholder.markdown(answer)
            except:
                try:
                    answer = invoke(prompt)
                    placeholder.markdown(answer)
                except:
                    placeholder.markdown("Sorry,please try again!")
    message = {"role": "assistant", "content": answer}
    st.session_state.messages.append(message)
