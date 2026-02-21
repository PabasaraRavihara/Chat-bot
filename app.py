import streamlit as st
import google.generativeai as genai
import os
import tempfile
from dotenv import load_dotenv

# --- CONFIGURATION ---
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
    .stChatFloatingInputContainer {padding-bottom: 20px;}
</style>
""", unsafe_allow_html=True)

st.title("✨ My Modern AI Assistant")
st.caption("Powered by Charlie Production ⚡ Fast & Advanced PDF Vision")

# --- PDF UPLOAD (SIDEBAR) ---
with st.sidebar:
    st.title("📄 Document Upload")
    st.write("Upload any PDF (even Scanned ones up to 100MB+), then ask questions!")
    
    uploaded_file = st.file_uploader("Upload a PDF", type="pdf")
    
    # Check if a new file is uploaded
    if uploaded_file is not None:
        if "current_pdf_name" not in st.session_state or st.session_state.current_pdf_name != uploaded_file.name:
            with st.spinner("Analyzing document... This might take a few seconds for large files."):
                try:
                    # 1. Save the uploaded file temporarily
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
                        tmp_file.write(uploaded_file.getvalue())
                        tmp_file_path = tmp_file.name
                    
                    # 2. Upload directly to Google Gemini's servers (Advanced Vision!)
                    uploaded_gemini_file = genai.upload_file(path=tmp_file_path, display_name=uploaded_file.name)
                    
                    # 3. Save details in memory
                    st.session_state.gemini_file = uploaded_gemini_file
                    st.session_state.current_pdf_name = uploaded_file.name
                    
                    # 4. Restart chat so it knows we have a new file
                    model = genai.GenerativeModel("gemini-2.5-flash")
                    st.session_state.chat_session = model.start_chat(history=[])
                    
                    st.success("✅ PDF loaded and analyzed successfully! Ask anything.")
                    
                    # Clean up temp file
                    os.remove(tmp_file_path)
                    
                except Exception as e:
                    st.error(f"❌ Error uploading file: {e}")
    else:
        # If user removes the file, clear the memory
        if "current_pdf_name" in st.session_state:
            del st.session_state.current_pdf_name
            if "gemini_file" in st.session_state:
                del st.session_state.gemini_file
            
            # Restart normal chat
            model = genai.GenerativeModel("gemini-2.5-flash")
            st.session_state.chat_session = model.start_chat(history=[])

# --- AI MEMORY SETUP ---
if "chat_session" not in st.session_state:
    model = genai.GenerativeModel("gemini-2.5-flash")
    st.session_state.chat_session = model.start_chat(history=[])

# --- CHAT HISTORY ---
for message in st.session_state.chat_session.history:
    role = "assistant" if message.role == "model" else "user"
    avatar_icon = "✨" if role == "assistant" else "🧑‍💻"
    
    # Safely extract text (ignoring the background PDF file object)
    display_text = ""
    for part in message.parts:
        try:
            if part.text:
                display_text += part.text
        except:
            pass
            
    if display_text.strip():
        with st.chat_message(role, avatar=avatar_icon):
            st.markdown(display_text)

# --- CHAT LOGIC ---
if prompt := st.chat_input("Ask me anything or query the PDF..."):
    
    with st.chat_message("user", avatar="🧑‍💻"):
        st.markdown(prompt)
    
    with st.chat_message("assistant", avatar="✨"):
        message_placeholder = st.empty()
        full_response = ""
        
        # Determine what to send to Gemini
        message_content = prompt
        

        if "gemini_file" in st.session_state and len(st.session_state.chat_session.history) == 0:
            message_content = [st.session_state.gemini_file, prompt]
        
        try:
            response = st.session_state.chat_session.send_message(message_content, stream=True)
            
            for chunk in response:
                full_response += chunk.text
                message_placeholder.markdown(full_response + "▌")
            
            message_placeholder.markdown(full_response)
            
        except Exception as e:
            message_placeholder.error(f"❌ An error occurred: {e}")
