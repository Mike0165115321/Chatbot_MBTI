import streamlit as st
import uuid
import config
import database_manager as db
from gemini_client import get_gemini_response

def format_history_for_prompt(messages: list[dict]) -> str:
    if not messages:
        return "ยังไม่มีประวัติการสนทนา"
    history_str = []
    for msg in messages:
        role = msg['role']
        content = msg.get('content', '').strip()
        history_str.append(f"{role}: {content}")
    return "\n".join(history_str)

st.set_page_config(page_title="Persona AI Chatbot", page_icon="🤖", layout="wide")

with st.sidebar:
    st.header("เลือกตัวตน AI")
    persona_names = config.get_persona_names()
    selected_persona_name = st.selectbox(
        "เลือกบุคลิกที่คุณต้องการคุยด้วย:",
        options=persona_names,
        key="persona_selector"
    )
    system_instruction = config.load_persona_instruction(selected_persona_name)
    st.divider()

    st.header("ประวัติการสนทนา")
    if st.button("➕ เริ่มการสนทนาใหม่", use_container_width=True):
        st.session_state.session_id = str(uuid.uuid4())
        st.session_state.messages = []
        st.session_state.current_persona = selected_persona_name
        st.rerun()

    chat_sessions = db.get_chat_sessions() 

    for session in chat_sessions:
        session_id = session['session_id']
        title = session['title']
        display_title = (title[:20] + '...') if len(title) > 20 else title

        col1, col2 = st.columns([3, 1])

        with col1:
            if st.button(f"📜 {display_title}", key=f"select_{session_id}", use_container_width=True):
                st.session_state.session_id = session_id
                st.session_state.messages = db.get_full_history_by_session_id(session_id)
                st.session_state.current_persona = selected_persona_name
                st.rerun()
        
        with col2:
            if st.button("🗑️", key=f"delete_{session_id}", use_container_width=True):
                db.delete_session(session_id)
                if st.session_state.session_id == session_id:
                    st.session_state.session_id = str(uuid.uuid4())
                    st.session_state.messages = []
                st.rerun()


if 'session_id' not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
    st.session_state.messages = []
    st.session_state.current_persona = selected_persona_name
    db.init_db()

st.title(f"AI Persona: {selected_persona_name}")

if not st.session_state.messages:
    st.info(f"เริ่มต้นการสนทนากับ {selected_persona_name} ได้เลย!")
else:
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

if user_input := st.chat_input(f"สนทนากับ {selected_persona_name}..."):
    sanitized_user_input = user_input.encode('utf-8', 'replace').decode('utf-8')
    st.session_state.messages.append({"role": "user", "content": sanitized_user_input})
    db.add_message(st.session_state.session_id, 'user', sanitized_user_input)

    with st.spinner(f"{selected_persona_name} กำลังคิด..."):
        history_dicts = db.get_recent_messages(st.session_state.session_id)
        formatted_history = format_history_for_prompt(history_dicts)
        
        full_prompt = (
            f"{system_instruction}\n\n"
            f"--- ประวัติการสนทนาที่ผ่านมา ---\n"
            f"{formatted_history}\n\n"
            f"--- การสนทนาปัจจุบัน ---\n"
            f"user: {sanitized_user_input}\n"
            f"model:"
        )
        
        response = get_gemini_response(full_prompt)
        sanitized_response = response.encode('utf-8', 'replace').decode('utf-8').strip()
        
        st.session_state.messages.append({"role": "assistant", "content": sanitized_response})
        db.add_message(st.session_state.session_id, 'model', sanitized_response)
        
        st.rerun()