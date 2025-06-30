# LocalAI 配置文件

# 服务器配置
SERVER_CONFIG = {
    "host": "0.0.0.0",
    "port": 7860,
    "share": False,
    "inbrowser": True,
    "show_error": True
}

# 模型配置
MODEL_CONFIG = {
    "max_tokens": 512,
    "temperature": 0.8,
    "top_p": 0.95,
    "repeat_penalty": 1.15,
    "n_ctx": 2048,
    "n_threads": 4,
    "verbose": False
}

# 下载配置
DOWNLOAD_CONFIG = {
    "max_models_display": 20,
    "timeout": 300,
    "retry_times": 3
}

# 推荐的小模型列表（备用）
RECOMMENDED_MODELS = [
    "TinyLlama/TinyLlama-1.1B-Chat-v1.0",
    "microsoft/DialoGPT-small",
    "microsoft/DialoGPT-medium",
    "Qwen/Qwen1.5-1.8B-Chat",
    "google/gemma-2b",
    "stabilityai/stablelm-2-1_6b",
    "microsoft/DialoGPT-large",
    "facebook/blenderbot_small-90M",
    "microsoft/GODEL-v1_1-base-seq2seq",
    "EleutherAI/gpt-neo-1.3B"
]

# 模型筛选关键词
MODEL_FILTER = {
    "include_keywords": ['1b', '2b', '3b', '4b', '5b', '6b', '7b', 'small', 'mini', 'tiny', 'chat', 'instruct'],
    "exclude_keywords": ['8b', '9b', '10b', '11b', '12b', '13b', '14b', '15b', '20b', '30b', '70b', '175b'],
    "required_formats": ['.gguf', '.bin'],
    "max_size_gb": 7
}

# UI配置
UI_CONFIG = {
    "title": "LocalAI 对话助手",
    "description": "基于 llama-cpp-python 的本地AI对话系统",
    "theme": "soft",
    "chatbot_height": 400,
    "max_history_length": 50
}

# 目录配置
DIRECTORY_CONFIG = {
    "models_dir": "models",
    "config_file": "model_config.json",
    "logs_dir": "logs",
    "cache_dir": "cache"
}