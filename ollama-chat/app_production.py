import streamlit as st
from ollama_client import OllamaClient
import time
import json
import os
import psutil
from datetime import datetime
from dotenv import load_dotenv
from config import config
import streamlit_authenticator as stauth

# Load environment variables
load_dotenv()

# Authentication (if enabled)
def check_authentication():
    if not config.enable_auth:
        return True
    
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    
    if not st.session_state.authenticated:
        st.title("🔐 Login Required")
        password = st.text_input("Enter password:", type="password")
        
        if st.button("Login"):
            if password == config.auth_password:
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("Invalid password")
        return False
    
    return True

# System monitoring
def get_system_info():
    return {
        "cpu_percent": psutil.cpu_percent(interval=1),
        "memory_percent": psutil.virtual_memory().percent,
        "disk_percent": psutil.disk_usage('/').percent if os.name != 'nt' else psutil.disk_usage('C:').percent
    }

# Page configuration
st.set_page_config(
    page_title=config.app_title,
    page_icon="🦙",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Check authentication
if not check_authentication():
    st.stop()

# Helper functions
def get_messages_with_system(system_prompt=None):
    messages = []
    if system_prompt and system_prompt.strip():
        messages.append({"role": "system", "content": system_prompt})
    
    # Limit message history for performance
    recent_messages = st.session_state.messages[-config.max_message_history:]
    messages.extend(recent_messages)
    return messages

# Initialize Ollama client
@st.cache_resource
def get_ollama_client():
    return OllamaClient(base_url=config.ollama_base_url)

ollama = get_ollama_client()

# Initialize chat history early
if "messages" not in st.session_state:
    st.session_state.messages = []

# App header
col1, col2 = st.columns([3, 1])
with col1:
    st.title(f"🦙 {config.app_title}")
    st.markdown("Enterprise-ready Ollama chat interface")

with col2:
    if config.enable_auth:
        if st.button("🚪 Logout"):
            st.session_state.authenticated = False
            st.rerun()

# Sidebar configuration
with st.sidebar:
    st.header("⚙️ Configuration")
    
    # System Status
    with st.expander("🖥️ System Status", expanded=False):
        if ollama.is_available():
            st.success("✅ Ollama Connected")
            
            # System metrics
            sys_info = get_system_info()
            col1, col2, col3 = st.columns(3)
            col1.metric("CPU", f"{sys_info['cpu_percent']:.1f}%")
            col2.metric("RAM", f"{sys_info['memory_percent']:.1f}%")
            col3.metric("Disk", f"{sys_info['disk_percent']:.1f}%")
            
        else:
            st.error("❌ Ollama Disconnected")
            st.markdown(f"Check connection to: `{config.ollama_base_url}`")
            st.stop()
    
    # Model selection with caching
    @st.cache_data(ttl=60)  # Cache for 60 seconds
    def get_available_models():
        return ollama.list_models()
    
    models = get_available_models()
    if models:
        selected_model = st.selectbox("🤖 Select Model", models)
    else:
        st.error("No models found")
        st.stop()
    
    # Performance settings
    st.subheader("🎛️ Model Parameters")
    temperature = st.slider("Temperature", 0.0, 2.0, 0.7, 0.1, 
                           help="Controls randomness (0=deterministic, 2=very random)")
    max_tokens = st.slider("Max Tokens", 100, 4000, 1000, 100,
                          help="Maximum response length")
    
    # Advanced settings
    with st.expander("🔧 Advanced Settings", expanded=False):
        top_p = st.slider("Top P", 0.0, 1.0, 0.9, 0.05, 
                         help="Nucleus sampling parameter")
        top_k = st.slider("Top K", 1, 100, 40, 1,
                         help="Top-k sampling parameter")
        repeat_penalty = st.slider("Repeat Penalty", 0.5, 2.0, 1.1, 0.05,
                                 help="Penalty for repeating tokens")
    
    # System prompt
    st.subheader("🎭 System Prompt")
    system_prompt = st.text_area(
        "System behavior:",
        placeholder="You are a helpful AI assistant...",
        height=100,
        help="Defines the AI's personality and behavior"
    )
    
    # Preset prompts
    presets = {
        "Default": "",
        "Code Helper": "You are an expert programmer. Provide clean, well-commented code with explanations.",
        "Creative Writer": "You are a creative writer. Use vivid imagery and engaging storytelling.",
        "Teacher": "You are a patient teacher. Explain concepts clearly with examples and check understanding.",
        "Analyst": "You are a data analyst. Provide structured, evidence-based insights with clear reasoning."
    }
    
    selected_preset = st.selectbox("Quick Presets:", list(presets.keys()))
    if st.button("Apply Preset"):
        st.session_state.system_prompt = presets[selected_preset]
        st.rerun()
    
    # Model management (if enabled)
    if config.enable_model_management:
        st.subheader("📦 Model Management")
        
        with st.expander("Available Models", expanded=False):
            if models:
                for model in models:
                    col1, col2 = st.columns([3, 1])
                    col1.write(f"• {model}")
                    if col2.button("🗑️", key=f"unload_{model}", help="Unload from memory"):
                        if ollama.unload_model(model):
                            st.success(f"Unloaded {model}")
                        else:
                            st.error("Failed to unload")
        
        with st.expander("Pull New Model", expanded=False):
            popular_models = [
                "llama2:7b", "llama2:13b", "mistral:7b", 
                "codellama:7b", "phi:2.7b", "gemma:7b",
                "neural-chat:7b", "starling-lm:7b"
            ]
            
            st.markdown("**Popular Models:**")
            for model in popular_models:
                if st.button(f"📥 {model}", key=f"pull_{model}"):
                    st.info(f"Run: `ollama pull {model}`")
    
    # Chat statistics and export
    if st.session_state.messages:
        st.subheader("📊 Chat Analytics")
        
        # Statistics
        user_msgs = len([m for m in st.session_state.messages if m["role"] == "user"])
        ai_msgs = len([m for m in st.session_state.messages if m["role"] == "assistant"])
        total_chars = sum(len(m["content"]) for m in st.session_state.messages)
        
        col1, col2 = st.columns(2)
        col1.metric("Messages", f"{user_msgs + ai_msgs}")
        col2.metric("Characters", f"{total_chars:,}")
        
        # Export options
        with st.expander("💾 Export Chat", expanded=False):
            export_format = st.selectbox("Format:", ["JSON", "Markdown", "Text"])
            
            if export_format == "JSON":
                export_data = {
                    "metadata": {
                        "timestamp": datetime.now().isoformat(),
                        "model": selected_model,
                        "system_prompt": system_prompt,
                        "parameters": {
                            "temperature": temperature,
                            "max_tokens": max_tokens,
                            "top_p": top_p,
                            "top_k": top_k
                        }
                    },
                    "messages": st.session_state.messages,
                    "statistics": {
                        "user_messages": user_msgs,
                        "ai_messages": ai_msgs,
                        "total_characters": total_chars
                    }
                }
                chat_data = json.dumps(export_data, indent=2)
                filename = f"chat_export_{datetime.now().strftime('%Y%m%d_%H%M')}.json"
            
            elif export_format == "Markdown":
                chat_data = f"# Chat Export\n\n"
                chat_data += f"**Model:** {selected_model}\n"
                chat_data += f"**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n"
                if system_prompt:
                    chat_data += f"**System Prompt:** {system_prompt}\n\n"
                chat_data += "---\n\n"
                
                for msg in st.session_state.messages:
                    role = "🧑 **User**" if msg["role"] == "user" else "🤖 **Assistant**"
                    chat_data += f"{role}\n\n{msg['content']}\n\n---\n\n"
                filename = f"chat_export_{datetime.now().strftime('%Y%m%d_%H%M')}.md"
            
            else:  # Text
                chat_data = f"Chat Export - {datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
                chat_data += f"Model: {selected_model}\n"
                chat_data += "="*60 + "\n\n"
                
                for msg in st.session_state.messages:
                    role = "USER" if msg["role"] == "user" else "ASSISTANT"
                    chat_data += f"{role}: {msg['content']}\n\n"
                filename = f"chat_export_{datetime.now().strftime('%Y%m%d_%H%M')}.txt"
            
            st.download_button(
                f"📥 Download {export_format}",
                data=chat_data,
                file_name=filename,
                mime=f"text/{export_format.lower()}"
            )
    
    # Clear chat
    if st.button("🗑️ Clear Chat", type="secondary", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# Main chat interface
st.subheader("💬 Chat")

# Show active system prompt
if system_prompt and system_prompt.strip():
    st.info(f"🎭 **Active Behavior:** {system_prompt[:100]}{'...' if len(system_prompt) > 100 else ''}")

# Display message count warning
if len(st.session_state.messages) > config.max_message_history:
    st.warning(f"⚠️ Chat history limited to last {config.max_message_history} messages for performance")

# Chat history
for message in st.session_state.messages[-config.max_message_history:]:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("Type your message..."):
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Generate response
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        
        # Prepare messages with system prompt
        messages_with_system = get_messages_with_system(system_prompt)
        
        try:
            # Stream response
            for chunk in ollama.chat_stream(
                model=selected_model,
                messages=messages_with_system,
                options={
                    "temperature": temperature,
                    "num_predict": max_tokens,
                    "top_p": top_p,
                    "top_k": top_k,
                    "repeat_penalty": repeat_penalty
                }
            ):
                full_response += chunk
                message_placeholder.markdown(full_response + "▌")
            
            # Final response
            message_placeholder.markdown(full_response)
            
        except Exception as e:
            st.error(f"Error generating response: {str(e)}")
            full_response = "Sorry, I encountered an error. Please try again."
            message_placeholder.markdown(full_response)
    
    # Add to history
    st.session_state.messages.append({"role": "assistant", "content": full_response})