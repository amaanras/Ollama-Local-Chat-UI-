# Ollama-Local-Chat-UI-
🦙 A modern, feature-rich web interface for Ollama with conversation management, model comparison, and real-time analytics

# 🦙 Ollama Chat Interface

A modern, feature-rich chat interface for Ollama with enhanced UI/UX, conversation management, and advanced analytics.

![Python](https://img.shields.io/badge/python-v3.8+-blue.svg)
![Streamlit](https://img.shields.io/badge/streamlit-v1.28+-red.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

## ✨ Features

### Core Features
- 💬 **Multiple Conversations** - Manage multiple chat sessions simultaneously
- 🔄 **Model Comparison** - Compare responses from different models side-by-side
- 🎨 **Modern UI** - Clean, responsive interface with dark/light theme support
- 📋 **Easy Message Copy** - Reliable clipboard functionality for all messages
- ⏰ **Timestamps** - Track when each message was sent
- 🔍 **Search** - Search across all conversations
- 📊 **Analytics** - Track usage statistics and model performance

### Advanced Features
- 🎭 **System Prompts** - Customize AI behavior with templates
- 🔄 **Message Regeneration** - Regenerate any AI response
- ✏️ **Message Editing** - Edit and resend messages
- 📥 **Export Conversations** - Export to JSON, Markdown, or CSV
- 🏃 **Performance Benchmarking** - Test and compare model speeds
- 🔐 **Optional Authentication** - Password-protect your interface
- 📈 **Real-time Metrics** - Monitor system resources

## 🚀 Quick Start

### Prerequisites

1. **Install Ollama**
   ```bash
   # macOS
   brew install ollama

   # Linux
   curl -fsSL https://ollama.ai/install.sh | sh

   # Windows
   # Download from https://ollama.ai/download
   ```

2. **Start Ollama**
   ```bash
   ollama serve
   ```

3. **Pull a Model**
   ```bash
   ollama pull llama2
   # or any other model like mistral, codellama, etc.
   ```

### Installation

1. **Clone the Repository**
   ```bash
   git clone https://github.com/yourusername/ollama-chat.git
   cd ollama-chat
   ```

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure (Optional)**
   ```bash
   cp .env.example .env
   # Edit .env with your preferred settings
   ```

4. **Run the Interface**
   ```bash
   streamlit run app.py
   ```

5. **Open in Browser**
   - Navigate to http://localhost:8501

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the project root (optional):

```bash
# Ollama Configuration
OLLAMA_HOST=localhost
OLLAMA_PORT=11434

# App Configuration
APP_TITLE="My Ollama Chat"
MAX_MESSAGE_HISTORY=100

# Security
ENABLE_AUTH=true
AUTH_PASSWORD=your_secure_password

# Features
ENABLE_MODEL_COMPARISON=true
ENABLE_BENCHMARKING=true
```

See `.env.example` for all available options.

### Popular Models

| Model | Size | Use Case |
|-------|------|----------|
| `llama2:7b` | 3.8GB | General purpose |
| `llama2:13b` | 7.3GB | Better quality |
| `mistral:7b` | 4.1GB | Fast & efficient |
| `codellama:7b` | 3.8GB | Code generation |
| `phi:2.7b` | 1.6GB | Lightweight |
| `gemma:7b` | 4.8GB | Google's model |

Pull models with:
```bash
ollama pull model_name
```

## 📖 Usage Guide

### Basic Chat
1. Select a model from the sidebar
2. Type your message and press Enter
3. View responses with timestamps
4. Use the Actions menu to copy, regenerate, or edit messages

### Managing Conversations
- Click "➕ New Conversation" to start fresh
- Switch between conversations in the sidebar
- Delete old conversations with the 🗑️ button

### Comparing Models
1. Enable "🔄 Compare Models" in the sidebar
2. Select multiple models
3. Send a message to see all responses
4. Best response is automatically saved

### System Prompts
1. Choose from templates or write custom prompts
2. Save frequently used prompts
3. System prompts define the AI's behavior

### Exporting Data
1. Go to the Analytics tab
2. Choose export format (JSON, Markdown, CSV)
3. Select specific or all conversations
4. Download the file

## 🎨 Customization

### Themes
The interface supports automatic dark/light mode based on your system preferences. You can also toggle manually with the 🌓 button.

### Adding Custom Prompts
Edit the `templates` dictionary in `config.py`:
```python
"Custom Assistant": "You are a specialized assistant for..."
```

## 🐛 Troubleshooting

### Common Issues

**Ollama not connected**
- Ensure Ollama is running: `ollama serve`
- Check if it's accessible: `curl http://localhost:11434`
- Verify the host/port in your `.env` file

**No models available**
- Pull at least one model: `ollama pull llama2`
- Check available models: `ollama list`

**Slow responses**
- Try smaller models (7B instead of 13B)
- Reduce `max_tokens` in settings
- Check system resources in the sidebar

**Copy button not working**
- Use Ctrl+A to select all text in the copy area
- Then use Ctrl+C (Cmd+C on Mac) to copy

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Ollama](https://ollama.ai/) for the excellent local LLM platform
- [Streamlit](https://streamlit.io/) for the powerful web framework
- The open-source community for inspiration and contributions

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/ollama-chat/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/ollama-chat/discussions)
- **Email**: your.email@example.com

---<img width="1510" height="866" alt="Screenshot 2025-07-27 at 15 13 07" src="https://github.com/user-attachments/assets/cfbd7759-aa2b-45e2-a2fa-2038153d9ec1" />

<img width="1507" height="863" alt="Screenshot 2025-07-27 at 15 15 39" src="https://github.com/user-attachments/assets/25aba06f-c0cd-4919-b917-76f5d88f0e77" />

<img width="1508" height="864" alt="Screenshot 2025-07-27 at 15 16 16" src="https://github.com/user-attachments/assets/4adf2432-f555-4bb3-b548-4c5990fbf720" />


Made with ❤️ by amaanras.petersen@gmail.com
