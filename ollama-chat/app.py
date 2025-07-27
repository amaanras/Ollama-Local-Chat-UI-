import streamlit as st
from ollama_client import OllamaClient
import time
import json
import os
import psutil
from datetime import datetime
from dotenv import load_dotenv
from config import config
import hashlib
import re

# Load environment variables
load_dotenv()

# Custom CSS for enhanced UI
def load_custom_css():
    st.markdown("""
    <style>
    /* Message styling */
    .stChatMessage {
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 1rem;
    }
    
    /* Dark mode support */
    @media (prefers-color-scheme: dark) {
        .stApp {
            background-color: #1a1a1a;
        }
    }
    
    /* Message actions */
    .message-actions {
        margin-top: 0.5rem;
        padding-top: 0.5rem;
        border-top: 1px solid rgba(128, 128, 128, 0.2);
    }
    
    /* Timestamp styling */
    .message-timestamp {
        font-size: 0.8em;
        color: #888;
        margin-bottom: 0.5rem;
    }
    
    /* Search box styling */
    .search-box {
        background: rgba(255,255,255,0.05);
        border-radius: 20px;
        padding: 0.5rem 1rem;
        margin-bottom: 1rem;
    }
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        padding: 0.5rem 1rem;
    }
    
    /* Copy text area styling */
    .copy-text-area {
        font-family: monospace;
        font-size: 0.9em;
        background-color: #f0f0f0;
        border: 1px solid #ddd;
        border-radius: 4px;
        padding: 0.5rem;
        margin-top: 0.5rem;
    }
    </style>
    """, unsafe_allow_html=True)

# Authentication
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

# Theme management
def toggle_theme():
    if 'theme' not in st.session_state:
        st.session_state.theme = 'light'
    st.session_state.theme = 'dark' if st.session_state.theme == 'light' else 'light'

# Initialize conversation management
def init_conversation_state():
    if 'conversations' not in st.session_state:
        st.session_state.conversations = {}
    if 'active_conversation' not in st.session_state:
        st.session_state.active_conversation = 'default'
    if st.session_state.active_conversation not in st.session_state.conversations:
        st.session_state.conversations[st.session_state.active_conversation] = {
            'messages': [],
            'created_at': datetime.now(),
            'last_modified': datetime.now(),
            'title': 'New Chat'
        }

# Message management functions
def add_message(role, content, conversation_id=None):
    if conversation_id is None:
        conversation_id = st.session_state.active_conversation
    
    message = {
        "role": role,
        "content": content,
        "timestamp": datetime.now().isoformat(),
        "id": hashlib.md5(f"{role}{content}{datetime.now()}".encode()).hexdigest()[:8]
    }
    
    st.session_state.conversations[conversation_id]['messages'].append(message)
    st.session_state.conversations[conversation_id]['last_modified'] = datetime.now()
    
    # Auto-generate title from first user message
    if len(st.session_state.conversations[conversation_id]['messages']) == 1:
        st.session_state.conversations[conversation_id]['title'] = content[:50] + "..." if len(content) > 50 else content

def search_messages(query):
    results = []
    for conv_id, conv_data in st.session_state.conversations.items():
        for msg in conv_data['messages']:
            if query.lower() in msg['content'].lower():
                results.append({
                    'conversation': conv_id,
                    'message': msg,
                    'context': conv_data['title']
                })
    return results

# Page configuration
st.set_page_config(
    page_title=config.app_title,
    page_icon="🦙",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load custom CSS
load_custom_css()

# Check authentication
if not check_authentication():
    st.stop()

# Initialize Ollama client
@st.cache_resource
def get_ollama_client():
    return OllamaClient(base_url=config.ollama_base_url)

ollama = get_ollama_client()

# Initialize conversation state
init_conversation_state()

# App header with theme toggle
col1, col2, col3 = st.columns([3, 1, 1])
with col1:
    st.title(f"🦙 {config.app_title}")
    st.markdown("Enhanced AI chat experience with Ollama")

with col2:
    if st.button("🌓 Theme", help="Toggle dark/light theme"):
        toggle_theme()
        st.rerun()

with col3:
    if config.enable_auth:
        if st.button("🚪 Logout"):
            st.session_state.authenticated = False
            st.rerun()

# Sidebar configuration with tabs
with st.sidebar:
    # Connection status at the top
    if ollama.is_available():
        st.success("✅ Ollama Connected")
    else:
        st.error("❌ Ollama Disconnected")
        st.markdown("Please start Ollama:")
        st.code("ollama serve")
        st.stop()
    
    # Create tabs for better organization
    sidebar_tabs = st.tabs(["💬 Chat", "⚙️ Model", "🎭 Prompts", "📊 System"])
    
    # Tab 1: Chat & Conversations
    with sidebar_tabs[0]:
        st.markdown("### Conversations")
        
        # New conversation button
        if st.button("➕ New Conversation", use_container_width=True, type="primary"):
            new_id = f"chat_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            st.session_state.conversations[new_id] = {
                'messages': [],
                'created_at': datetime.now(),
                'last_modified': datetime.now(),
                'title': 'New Chat'
            }
            st.session_state.active_conversation = new_id
            st.rerun()
        
        # Search conversations
        search_conv = st.text_input("🔍 Search conversations", placeholder="Type to search...")
        
        # List conversations with scroll area
        st.markdown("#### Recent Chats")
        conversation_container = st.container()
        with conversation_container:
            conversations_to_show = sorted(
                st.session_state.conversations.items(),
                key=lambda x: x[1]['last_modified'],
                reverse=True
            )
            
            # Filter by search if provided
            if search_conv:
                conversations_to_show = [
                    (conv_id, conv_data) for conv_id, conv_data in conversations_to_show
                    if search_conv.lower() in conv_data['title'].lower()
                ]
            
            # Display conversations
            for conv_id, conv_data in conversations_to_show[:20]:  # Limit to 20 most recent
                col1, col2 = st.columns([5, 1])
                with col1:
                    is_active = conv_id == st.session_state.active_conversation
                    if st.button(
                        f"{'🔵' if is_active else '⚪'} {conv_data['title'][:30]}...", 
                        key=f"conv_{conv_id}",
                        use_container_width=True,
                        disabled=is_active
                    ):
                        st.session_state.active_conversation = conv_id
                        st.rerun()
                    
                    # Show last modified time
                    last_mod = conv_data['last_modified']
                    time_diff = datetime.now() - last_mod
                    if time_diff.days > 0:
                        time_str = f"{time_diff.days}d ago"
                    elif time_diff.seconds > 3600:
                        time_str = f"{time_diff.seconds // 3600}h ago"
                    else:
                        time_str = f"{time_diff.seconds // 60}m ago"
                    st.caption(f"↳ {time_str}")
                
                with col2:
                    if st.button("🗑️", key=f"del_{conv_id}", help="Delete"):
                        if len(st.session_state.conversations) > 1:
                            del st.session_state.conversations[conv_id]
                            if conv_id == st.session_state.active_conversation:
                                st.session_state.active_conversation = list(st.session_state.conversations.keys())[0]
                            st.rerun()
    
    # Tab 2: Model Settings
    with sidebar_tabs[1]:
        st.markdown("### Model Configuration")
        
        # Model selection
        models = ollama.list_models()
        if not models:
            st.error("No models found")
            st.markdown("Pull a model first:")
            st.code("ollama pull llama2")
            st.stop()
        
        selected_model = st.selectbox(
            "Select Model",
            models,
            help="Choose the AI model for responses"
        )
        
        # Model info
        with st.expander("ℹ️ Model Info", expanded=False):
            if selected_model:
                st.markdown(f"**Active:** {selected_model}")
                st.markdown(f"**Available:** {len(models)} models")
                if st.button("🔄 Refresh Models"):
                    st.cache_data.clear()
                    st.rerun()
        
        # Model comparison
        st.markdown("### Advanced Options")
        compare_mode = st.checkbox(
            "🔄 Compare Models",
            help="Generate responses from multiple models"
        )
        if compare_mode:
            compare_models = st.multiselect(
                "Models to compare:",
                models,
                default=[selected_model] if selected_model in models else [],
                max_selections=4  # Limit to prevent UI issues
            )
        
        # Model Parameters in collapsible sections
        st.markdown("### Generation Settings")
        
        # Basic parameters (always visible)
        temperature = st.slider(
            "Temperature",
            0.0, 2.0, 0.7, 0.1,
            help="Controls randomness (0=deterministic, 2=very random)"
        )
        
        max_tokens = st.slider(
            "Max Tokens",
            100, 4000, 1000, 100,
            help="Maximum response length"
        )
        
        # Advanced parameters in expander
        with st.expander("🔧 Advanced Parameters"):
            top_p = st.slider(
                "Top P",
                0.0, 1.0, 0.9, 0.05,
                help="Nucleus sampling parameter"
            )
            top_k = st.slider(
                "Top K",
                1, 100, 40, 1,
                help="Top-k sampling parameter"
            )
            repeat_penalty = st.slider(
                "Repeat Penalty",
                0.5, 2.0, 1.1, 0.05,
                help="Penalty for repeating tokens"
            )
    
    # Tab 3: Prompts
    with sidebar_tabs[2]:
        st.markdown("### System Prompts")
        
        # Quick templates in dropdown
        templates = {
            "Default": "",
            "Code Expert": "You are an expert programmer. Provide clean, well-commented code with explanations.",
            "Creative Writer": "You are a creative writer. Use vivid imagery and engaging storytelling.",
            "Teacher": "You are a patient teacher. Explain concepts clearly with examples.",
            "Analyst": "You are a data analyst. Provide structured, evidence-based insights.",
            "Debugger": "You are a debugging assistant. Help identify and fix code issues systematically.",
            "Translator": "You are a professional translator. Provide accurate, context-aware translations.",
            "Technical Writer": "You are a technical writer. Create clear, structured documentation.",
            "Code Reviewer": "You are a code reviewer. Analyze code for best practices, security, and performance."
        }
        
        # Template selector
        template_choice = st.selectbox(
            "Quick Templates",
            list(templates.keys()),
            help="Select a pre-defined prompt template"
        )
        
        # Apply template button
        if st.button("Apply Template", use_container_width=True):
            st.session_state.current_system_prompt = templates[template_choice]
        
        # System prompt editor
        system_prompt = st.text_area(
            "System Prompt",
            value=st.session_state.get('current_system_prompt', templates[template_choice]),
            height=150,
            help="Define the AI's behavior and personality"
        )
        
        # Save custom prompt
        st.markdown("### Save Custom Prompt")
        with st.form("save_prompt_form"):
            prompt_name = st.text_input("Prompt name")
            save_button = st.form_submit_button("💾 Save Prompt", use_container_width=True)
            
            if save_button and prompt_name:
                if 'custom_prompts' not in st.session_state:
                    st.session_state.custom_prompts = {}
                st.session_state.custom_prompts[prompt_name] = system_prompt
                st.success(f"Saved '{prompt_name}'!")
        
        # Display saved prompts
        if st.session_state.get('custom_prompts'):
            st.markdown("### Saved Prompts")
            for name in st.session_state.custom_prompts:
                col1, col2 = st.columns([4, 1])
                with col1:
                    if st.button(f"📝 {name}", key=f"load_{name}", use_container_width=True):
                        st.session_state.current_system_prompt = st.session_state.custom_prompts[name]
                        st.rerun()
                with col2:
                    if st.button("❌", key=f"del_prompt_{name}"):
                        del st.session_state.custom_prompts[name]
                        st.rerun()
    
    # Tab 4: System & Analytics
    with sidebar_tabs[3]:
        st.markdown("### System Status")
        
        # System metrics
        sys_info = get_system_info()
        col1, col2 = st.columns(2)
        with col1:
            st.metric("CPU", f"{sys_info['cpu_percent']:.1f}%")
            st.metric("Memory", f"{sys_info['memory_percent']:.1f}%")
        with col2:
            st.metric("Disk", f"{sys_info['disk_percent']:.1f}%")
            if st.button("🔄 Refresh", key="refresh_metrics"):
                st.rerun()
        
        # Quick stats
        st.markdown("### Session Statistics")
        total_messages = sum(len(conv['messages']) for conv in st.session_state.conversations.values())
        st.metric("Total Messages", total_messages)
        st.metric("Active Conversations", len(st.session_state.conversations))
        
        # Settings
        st.markdown("### Settings")
        
        # Theme toggle
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🌓 Toggle Theme", use_container_width=True):
                toggle_theme()
                st.rerun()
        
        with col2:
            if st.button("🗑️ Clear All", use_container_width=True):
                if st.checkbox("Confirm clear all conversations"):
                    st.session_state.conversations = {}
                    init_conversation_state()
                    st.rerun()
        
        # Advanced settings link
        if st.button("⚙️ Advanced Configuration", use_container_width=True):
            st.info("Advanced settings can be configured via environment variables. See .env.example for details.")

# Main chat area with tabs
tab1, tab2, tab3 = st.tabs(["💬 Chat", "🔍 Search", "📊 Analytics"])

with tab1:
    # Current conversation info
    current_conv = st.session_state.conversations[st.session_state.active_conversation]
    st.caption(f"📅 Created: {current_conv['created_at'].strftime('%Y-%m-%d %H:%M')}")
    
    # Display messages
    messages = current_conv['messages']
    
    for i, message in enumerate(messages):
        with st.chat_message(message["role"]):
            # Timestamp
            if 'timestamp' in message:
                st.caption(datetime.fromisoformat(message['timestamp']).strftime('%H:%M:%S'))
            
            # Message content
            st.markdown(message["content"])
            
            # Message actions in an expander for cleaner UI
            with st.expander("Actions", expanded=False):
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    # Copy functionality using text_area for reliable copying
                    if st.button("📋 Copy", key=f"copy_btn_{i}"):
                        st.session_state[f"show_copy_{i}"] = True
                    
                    if st.session_state.get(f"show_copy_{i}", False):
                        st.text_area(
                            "Copy this text (Ctrl+A to select all, then Ctrl+C):",
                            value=message["content"],
                            height=100,
                            key=f"copy_text_{i}"
                        )
                        if st.button("✓ Done", key=f"done_copy_{i}"):
                            st.session_state[f"show_copy_{i}"] = False
                            st.rerun()
                
                with col2:
                    if message["role"] == "assistant":
                        if st.button("🔄 Regenerate", key=f"regen_{i}"):
                            # Remove this and subsequent messages
                            current_conv['messages'] = messages[:i]
                            st.rerun()
                
                with col3:
                    if st.button("✏️ Edit", key=f"edit_{i}"):
                        st.session_state[f"editing_{i}"] = True
                
                # Edit mode
                if st.session_state.get(f"editing_{i}", False):
                    edited_content = st.text_area(
                        "Edit message:",
                        value=message["content"],
                        key=f"edit_text_{i}"
                    )
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("💾 Save", key=f"save_edit_{i}"):
                            message["content"] = edited_content
                            st.session_state[f"editing_{i}"] = False
                            st.rerun()
                    with col2:
                        if st.button("❌ Cancel", key=f"cancel_edit_{i}"):
                            st.session_state[f"editing_{i}"] = False
                            st.rerun()

    # Chat input
    if prompt := st.chat_input("Type your message..."):
        add_message("user", prompt)
        
        with st.chat_message("user"):
            st.caption(datetime.now().strftime('%H:%M:%S'))
            st.markdown(prompt)
        
        # Generate response(s)
        if compare_mode and compare_models:
            # Compare mode - generate from multiple models
            responses = {}
            cols = st.columns(len(compare_models))
            
            for idx, model in enumerate(compare_models):
                with cols[idx]:
                    st.markdown(f"**{model}**")
                    with st.chat_message("assistant"):
                        message_placeholder = st.empty()
                        full_response = ""
                        
                        messages_for_model = [{"role": "system", "content": system_prompt}] if system_prompt else []
                        messages_for_model.extend([{"role": m["role"], "content": m["content"]} for m in messages])
                        messages_for_model.append({"role": "user", "content": prompt})
                        
                        for chunk in ollama.chat_stream(
                            model=model,
                            messages=messages_for_model,
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
                        
                        message_placeholder.markdown(full_response)
                        responses[model] = full_response
            
            # Save the best response (from selected model)
            add_message("assistant", responses.get(selected_model, list(responses.values())[0]))
            
        else:
            # Single model mode
            with st.chat_message("assistant"):
                st.caption(datetime.now().strftime('%H:%M:%S'))
                message_placeholder = st.empty()
                full_response = ""
                
                messages_for_model = [{"role": "system", "content": system_prompt}] if system_prompt else []
                messages_for_model.extend([{"role": m["role"], "content": m["content"]} for m in messages])
                
                try:
                    for chunk in ollama.chat_stream(
                        model=selected_model,
                        messages=messages_for_model,
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
                    
                    message_placeholder.markdown(full_response)
                    
                except Exception as e:
                    st.error(f"Error: {str(e)}")
                    full_response = "Sorry, I encountered an error."
                    message_placeholder.markdown(full_response)
            
            add_message("assistant", full_response)

with tab2:
    # Message search functionality
    st.subheader("🔍 Search Messages")
    
    search_query = st.text_input("Search across all conversations:", placeholder="Enter search term...")
    
    if search_query:
        results = search_messages(search_query)
        
        if results:
            st.write(f"Found {len(results)} results:")
            
            for result in results:
                with st.expander(f"💬 {result['context']} - {result['message']['role'].title()}"):
                    st.caption(f"Conversation: {result['conversation']}")
                    if 'timestamp' in result['message']:
                        st.caption(f"Time: {datetime.fromisoformat(result['message']['timestamp']).strftime('%Y-%m-%d %H:%M:%S')}")
                    
                    # Highlight search term
                    highlighted = re.sub(
                        f"({re.escape(search_query)})",
                        r"**\1**",
                        result['message']['content'],
                        flags=re.IGNORECASE
                    )
                    st.markdown(highlighted)
                    
                    if st.button(f"Go to conversation", key=f"goto_{result['message']['id']}"):
                        st.session_state.active_conversation = result['conversation']
                        st.rerun()
        else:
            st.info("No results found")

with tab3:
    # Analytics dashboard
    st.subheader("📊 Chat Analytics")
    
    # Overall statistics
    total_conversations = len(st.session_state.conversations)
    total_messages = sum(len(conv['messages']) for conv in st.session_state.conversations.values())
    total_user_messages = sum(len([m for m in conv['messages'] if m['role'] == 'user']) for conv in st.session_state.conversations.values())
    total_assistant_messages = sum(len([m for m in conv['messages'] if m['role'] == 'assistant']) for conv in st.session_state.conversations.values())
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Conversations", total_conversations)
    col2.metric("Total Messages", total_messages)
    col3.metric("User Messages", total_user_messages)
    col4.metric("AI Messages", total_assistant_messages)
    
    # Performance metrics
    if st.button("🏃 Run Performance Benchmark"):
        st.info("Running benchmark...")
        
        test_prompt = "Hello, how are you?"
        benchmark_results = []
        
        progress_bar = st.progress(0)
        for i, model in enumerate(models[:5]):  # Test up to 5 models
            start_time = time.time()
            
            response = ollama.chat(
                model=model,
                messages=[{"role": "user", "content": test_prompt}],
                options={"temperature": 0.7, "num_predict": 100}
            )
            
            end_time = time.time()
            response_time = end_time - start_time
            
            benchmark_results.append({
                "Model": model,
                "Response Time (s)": f"{response_time:.2f}",
                "Tokens/sec": f"{len(response.split()) / response_time:.1f}"
            })
            
            progress_bar.progress((i + 1) / min(5, len(models)))
        
        st.dataframe(benchmark_results)
    
    # Export options
    st.subheader("💾 Export Options")
    
    export_format = st.selectbox("Export Format:", ["JSON", "Markdown", "CSV"])
    include_all = st.checkbox("Include all conversations", value=False)
    
    if st.button("📥 Generate Export"):
        if include_all:
            export_data = st.session_state.conversations
        else:
            export_data = {st.session_state.active_conversation: current_conv}
        
        if export_format == "JSON":
            export_content = json.dumps(export_data, indent=2, default=str)
            mime_type = "application/json"
            file_ext = "json"
        elif export_format == "Markdown":
            export_content = ""
            for conv_id, conv_data in export_data.items():
                export_content += f"# {conv_data['title']}\n\n"
                for msg in conv_data['messages']:
                    role = "User" if msg['role'] == 'user' else "Assistant"
                    export_content += f"**{role}**: {msg['content']}\n\n"
                export_content += "---\n\n"
            mime_type = "text/markdown"
            file_ext = "md"
        else:  # CSV
            import csv
            import io
            output = io.StringIO()
            writer = csv.writer(output)
            writer.writerow(["Conversation", "Timestamp", "Role", "Content"])
            
            for conv_id, conv_data in export_data.items():
                for msg in conv_data['messages']:
                    writer.writerow([
                        conv_data['title'],
                        msg.get('timestamp', ''),
                        msg['role'],
                        msg['content']
                    ])
            
            export_content = output.getvalue()
            mime_type = "text/csv"
            file_ext = "csv"
        
        st.download_button(
            label=f"Download {export_format}",
            data=export_content,
            file_name=f"ollama_chat_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{file_ext}",
            mime=mime_type
        )