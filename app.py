import streamlit as st
import google.generativeai as genai
import PyPDF2
import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=API_KEY)

# Modern UI Settings
st.set_page_config(page_title="My AI Bot", page_icon="✨", layout="centered")

st.markdown("""
<style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    /* Chat input box eka lassanata thiyaganna */
    .stChatFloatingInputContainer {padding-bottom: 20px;}
</style>
""", unsafe_allow_html=True)

st.title("✨ My Modern AI Assistant")
st.caption("Powered by Google Gemini ⚡ Fast, Smooth & PDF Ready")

# --- PDF UPLOAD (SIDEBAR) ---
pdf_text = ""
with st.sidebar:
    st.title("📄 Document Upload")
    st.write("Upload your PDF here, then ask questions about its content!")
    uploaded_file = st.file_uploader("Upload a PDF", type="pdf")
    
    if uploaded_file is not None:
        try:
            
            pdf_reader = PyPDF2.PdfReader(uploaded_file)
            for page in pdf_reader.pages:
                text = page.extract_text()
                if text:
                    pdf_text += text
            st.success("✅ PDF loaded successfully! You can now ask questions.")        
        except Exception as e:
            st.error("❌ Failed to read the PDF. Please try again.")

# --- AI MEMORY & PDF SETUP ---


if "current_pdf" not in st.session_state:
    st.session_state.current_pdf = None

pdf_changed = False
if uploaded_file is not None:
   
    if st.session_state.current_pdf != uploaded_file.name:
        st.session_state.current_pdf = uploaded_file.name
        pdf_changed = True
else:
    
    if st.session_state.current_pdf is not None:
        st.session_state.current_pdf = None
        pdf_changed = True


if "chat_session" not in st.session_state or pdf_changed:
    if pdf_text != "":
       
        instruction = f"You are a helpful assistant. Answer the user's questions based on this document: {pdf_text}"
        model = genai.GenerativeModel("gemini-2.5-flash", system_instruction=instruction)
    else:
       
        model = genai.GenerativeModel("gemini-2.5-flash")
        
    st.session_state.chat_session = model.start_chat(history=[])


# --- CHAT HISTORY ---

for message in st.session_state.chat_session.history:
    role = "assistant" if message.role == "model" else "user"
    avatar_icon = "✨" if role == "assistant" else "🧑‍💻"
    with st.chat_message(role, avatar=avatar_icon):
        st.markdown(message.parts[0].text)

# --- CHAT LOGIC ---
if prompt := st.chat_input("Type your message here..."):
    
    with st.chat_message("user", avatar="🧑‍💻"):
        st.markdown(prompt)
    
    with st.chat_message("assistant", avatar="✨"):
        message_placeholder = st.empty()
        full_response = ""
        
        response = st.session_state.chat_session.send_message(prompt, stream=True)
        
        for chunk in response:
            full_response += chunk.text
            message_placeholder.markdown(full_response + "▌")
        
        message_placeholder.markdown(full_response)