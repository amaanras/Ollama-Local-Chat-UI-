import os
from dataclasses import dataclass, field
from typing import Optional, Dict, List

@dataclass
class Config:
    # Ollama Configuration
    ollama_host: str = os.getenv("OLLAMA_HOST", "localhost")
    ollama_port: int = int(os.getenv("OLLAMA_PORT", "11434"))
    ollama_timeout: int = int(os.getenv("OLLAMA_TIMEOUT", "300"))
    
    # App Configuration
    app_title: str = os.getenv("APP_TITLE", "Ollama Chat Interface")
    max_message_history: int = int(os.getenv("MAX_MESSAGE_HISTORY", "100"))
    enable_model_management: bool = os.getenv("ENABLE_MODEL_MANAGEMENT", "true").lower() == "true"
    
    # Security
    enable_auth: bool = os.getenv("ENABLE_AUTH", "false").lower() == "true"
    auth_password: Optional[str] = os.getenv("AUTH_PASSWORD")
    
    # Performance
    concurrent_requests: int = int(os.getenv("CONCURRENT_REQUESTS", "3"))
    
    # UI/UX Features
    enable_dark_mode: bool = os.getenv("ENABLE_DARK_MODE", "true").lower() == "true"
    enable_timestamps: bool = os.getenv("ENABLE_TIMESTAMPS", "true").lower() == "true"
    enable_message_search: bool = os.getenv("ENABLE_MESSAGE_SEARCH", "true").lower() == "true"
    enable_conversation_tabs: bool = os.getenv("ENABLE_CONVERSATION_TABS", "true").lower() == "true"
    enable_model_comparison: bool = os.getenv("ENABLE_MODEL_COMPARISON", "true").lower() == "true"
    
    # Advanced Features
    enable_file_upload: bool = os.getenv("ENABLE_FILE_UPLOAD", "true").lower() == "true"
    max_file_size_mb: int = int(os.getenv("MAX_FILE_SIZE_MB", "10"))
    allowed_file_types: List[str] = field(default_factory=lambda: os.getenv("ALLOWED_FILE_TYPES", "txt,md,py,js,html,css,json,csv").split(","))
    
    # Conversation Management
    max_conversations: int = int(os.getenv("MAX_CONVERSATIONS", "50"))
    auto_save_interval: int = int(os.getenv("AUTO_SAVE_INTERVAL", "30"))  # seconds
    conversation_export_formats: List[str] = field(default_factory=lambda: os.getenv("CONVERSATION_EXPORT_FORMATS", "json,md,csv,txt").split(","))
    
    # Model Benchmarking
    enable_benchmarking: bool = os.getenv("ENABLE_BENCHMARKING", "true").lower() == "true"
    benchmark_iterations: int = int(os.getenv("BENCHMARK_ITERATIONS", "3"))
    benchmark_prompt: str = os.getenv("BENCHMARK_PROMPT", "Hello, how are you?")
    
    # Prompt Management
    enable_prompt_library: bool = os.getenv("ENABLE_PROMPT_LIBRARY", "true").lower() == "true"
    default_prompts: Dict[str, str] = field(default_factory=lambda: {
        "Default": "",
        "Code Expert": "You are an expert programmer. Provide clean, well-commented code with explanations.",
        "Creative Writer": "You are a creative writer. Use vivid imagery and engaging storytelling.",
        "Teacher": "You are a patient teacher. Explain concepts clearly with examples.",
        "Analyst": "You are a data analyst. Provide structured, evidence-based insights.",
        "Debugger": "You are a debugging assistant. Help identify and fix code issues systematically.",
        "Translator": "You are a professional translator. Provide accurate, context-aware translations.",
        "Technical Writer": "You are a technical writer. Create clear, structured documentation.",
        "Code Reviewer": "You are a code reviewer. Analyze code for best practices, security, and performance.",
        "Tutor": "You are a personal tutor. Adapt your teaching style to the student's needs.",
        "Research Assistant": "You are a research assistant. Help gather, analyze, and synthesize information."
    })
    
    # UI Customization
    message_bubble_style: str = os.getenv("MESSAGE_BUBBLE_STYLE", "rounded")  # rounded, square, minimal
    color_scheme: str = os.getenv("COLOR_SCHEME", "blue")  # blue, green, purple, orange
    font_size: str = os.getenv("FONT_SIZE", "medium")  # small, medium, large
    
    # Analytics
    enable_analytics: bool = os.getenv("ENABLE_ANALYTICS", "true").lower() == "true"
    track_response_times: bool = os.getenv("TRACK_RESPONSE_TIMES", "true").lower() == "true"
    track_token_usage: bool = os.getenv("TRACK_TOKEN_USAGE", "true").lower() == "true"
    
    @property
    def ollama_base_url(self) -> str:
        return f"http://{self.ollama_host}:{self.ollama_port}"
    
    @property
    def theme_config(self) -> Dict[str, str]:
        themes = {
            "blue": {
                "primary": "#0066cc",
                "secondary": "#e3f2fd",
                "accent": "#1976d2"
            },
            "green": {
                "primary": "#2e7d32",
                "secondary": "#e8f5e9",
                "accent": "#388e3c"
            },
            "purple": {
                "primary": "#6a1b9a",
                "secondary": "#f3e5f5",
                "accent": "#7b1fa2"
            },
            "orange": {
                "primary": "#e65100",
                "secondary": "#fff3e0",
                "accent": "#ef6c00"
            }
        }
        return themes.get(self.color_scheme, themes["blue"])

config = Config()