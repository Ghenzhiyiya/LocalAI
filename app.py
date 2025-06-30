import gradio as gr
import os
import json
import logging
from pathlib import Path
from huggingface_hub import hf_hub_download, list_models, HfApi
from llama_cpp import Llama
import threading
import time
from typing import Optional, List, Dict
from config import *
from datetime import datetime

class ModelManager:
    def __init__(self):
        self.models_dir = Path(DIRECTORY_CONFIG["models_dir"])
        self.models_dir.mkdir(exist_ok=True)
        self.config_file = DIRECTORY_CONFIG["config_file"]
        self.current_model: Optional[Llama] = None
        self.model_info = self.load_model_config()
        self.setup_logging()
        
    def load_model_config(self) -> Dict:
        """加载模型配置"""
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    
    def save_model_config(self):
        """保存模型配置"""
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(self.model_info, f, ensure_ascii=False, indent=2)
    
    def setup_logging(self):
        """设置日志"""
        logs_dir = Path(DIRECTORY_CONFIG["logs_dir"])
        logs_dir.mkdir(exist_ok=True)
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(logs_dir / f"localai_{datetime.now().strftime('%Y%m%d')}.log", encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def get_small_models_from_hf(self) -> List[str]:
        """从Hugging Face获取小于7B的模型列表"""
        try:
            models = list_models(
                filter="gguf",
                sort="downloads",
                direction=-1,
                limit=50
            )
            
            small_models = []
            include_keywords = MODEL_FILTER["include_keywords"]
            exclude_keywords = MODEL_FILTER["exclude_keywords"]
            
            for model in models:
                model_name = model.modelId.lower()
                # 检查是否包含小模型关键词且不包含大模型关键词
                if any(keyword in model_name for keyword in include_keywords) and \
                   not any(keyword in model_name for keyword in exclude_keywords):
                    small_models.append(model.modelId)
                    if len(small_models) >= DOWNLOAD_CONFIG["max_models_display"]:
                        break
            
            # 添加推荐模型
            for model in RECOMMENDED_MODELS:
                if model not in small_models:
                    small_models.append(model)
            
            return small_models[:DOWNLOAD_CONFIG["max_models_display"]]
            
        except Exception as e:
            self.logger.error(f"获取模型列表失败: {e}")
            return RECOMMENDED_MODELS[:10]
    
    def download_model(self, model_id: str, progress_callback=None) -> str:
        """下载模型"""
        try:
            if progress_callback:
                progress_callback(f"开始下载模型: {model_id}")
            
            # 查找GGUF文件
            from huggingface_hub import HfApi
            api = HfApi()
            
            try:
                files = api.list_repo_files(model_id)
                gguf_files = [f for f in files if f.endswith('.gguf')]
                
                if not gguf_files:
                    raise Exception("未找到GGUF格式文件")
                
                # 选择最小的GGUF文件
                gguf_file = sorted(gguf_files)[0]
                
            except:
                # 如果无法获取文件列表，尝试常见的文件名
                possible_files = [
                    "model.gguf",
                    "ggml-model.gguf",
                    f"{model_id.split('/')[-1]}.gguf",
                    "pytorch_model.gguf"
                ]
                gguf_file = possible_files[0]
            
            if progress_callback:
                progress_callback(f"下载文件: {gguf_file}")
            
            # 下载模型文件
            model_path = hf_hub_download(
                repo_id=model_id,
                filename=gguf_file,
                local_dir=self.models_dir / model_id.replace('/', '_'),
                local_dir_use_symlinks=False
            )
            
            # 保存模型信息（使用绝对路径）
            abs_model_path = os.path.abspath(model_path)
            self.model_info[model_id] = {
                "path": abs_model_path,
                "downloaded": True,
                "file": gguf_file
            }
            self.save_model_config()
            
            if progress_callback:
                progress_callback(f"模型下载完成: {model_path}")
            
            return model_path
            
        except Exception as e:
            error_msg = f"下载模型失败: {str(e)}"
            if progress_callback:
                progress_callback(error_msg)
            raise Exception(error_msg)
    
    def load_model(self, model_path: str) -> bool:
        """加载模型"""
        try:
            # 确保使用绝对路径
            if not os.path.isabs(model_path):
                model_path = os.path.abspath(model_path)
            
            # 检查文件是否存在
            if not os.path.exists(model_path):
                self.logger.error(f"模型文件不存在: {model_path}")
                return False
            
            # 检查文件大小
            file_size = os.path.getsize(model_path)
            self.logger.info(f"准备加载模型: {model_path} (大小: {file_size/(1024**3):.2f} GB)")
            
            if self.current_model:
                del self.current_model
            
            self.current_model = Llama(
                model_path=model_path,
                n_ctx=MODEL_CONFIG["n_ctx"],
                n_threads=MODEL_CONFIG["n_threads"],
                verbose=MODEL_CONFIG["verbose"]
            )
            self.logger.info(f"模型加载成功: {model_path}")
            return True
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            self.logger.error(f"加载模型失败: {str(e)}")
            self.logger.error(f"详细错误信息: {error_details}")
            return False
    
    def generate_response(self, prompt: str, max_tokens: int = None) -> str:
        """生成回复"""
        if not self.current_model:
            return "请先选择并加载模型"
        
        if max_tokens is None:
            max_tokens = MODEL_CONFIG["max_tokens"]
        
        try:
            response = self.current_model(
                prompt,
                max_tokens=max_tokens,
                temperature=MODEL_CONFIG["temperature"],
                top_p=MODEL_CONFIG["top_p"],
                repeat_penalty=MODEL_CONFIG["repeat_penalty"],
                echo=False,
                stop=["\n用户:", "\n\n", "用户:", "助手:", "\n助手:"]
            )
            return response['choices'][0]['text'].strip()
        except Exception as e:
            self.logger.error(f"生成回复时出错: {e}")
            return f"生成回复时出错: {str(e)}"

# 全局模型管理器
model_manager = ModelManager()

def get_available_models():
    """获取可用模型列表"""
    return model_manager.get_small_models_from_hf()

def download_and_load_model(model_id: str, progress=gr.Progress()):
    """下载并加载模型"""
    try:
        progress(0, desc="开始下载模型...")
        
        def progress_callback(msg):
            print(msg)
        
        # 检查模型是否已下载
        if model_id in model_manager.model_info and model_manager.model_info[model_id].get('downloaded'):
            model_path = model_manager.model_info[model_id]['path']
            progress(0.8, desc="模型已存在，正在加载...")
        else:
            progress(0.2, desc="正在下载模型...")
            model_path = model_manager.download_model(model_id, progress_callback)
            progress(0.8, desc="下载完成，正在加载...")
        
        # 加载模型
        if model_manager.load_model(model_path):
            progress(1.0, desc="模型加载完成")
            return f"✅ 模型 {model_id} 加载成功", gr.update(interactive=True)
        else:
            return f"❌ 模型 {model_id} 加载失败", gr.update(interactive=False)
            
    except Exception as e:
        return f"❌ 错误: {str(e)}", gr.update(interactive=False)

def chat_response(message, history):
    """聊天回复函数"""
    if not model_manager.current_model:
        history.append({"role": "user", "content": message})
        history.append({"role": "assistant", "content": "请先选择并加载模型"})
        return history
    
    # 限制历史长度，只保留最近的6轮对话（12条消息）
    if len(history) > 12:
        history = history[-12:]
    
    # 构建对话历史，使用更自然的格式
    conversation = "你是一个友好、有帮助的AI助手。请根据对话历史，自然地回复用户的问题。\n\n"
    
    # 添加历史对话
    for msg in history:
        if msg["role"] == "user":
            conversation += f"用户: {msg['content']}\n"
        elif msg["role"] == "assistant":
            conversation += f"助手: {msg['content']}\n"
    
    # 添加当前用户消息
    conversation += f"用户: {message}\n助手: "
    
    # 生成回复
    response = model_manager.generate_response(conversation, max_tokens=256)
    
    # 清理回复，移除可能的重复内容
    response = response.replace("助手:", "").replace("用户:", "").strip()
    
    # 如果回复为空，尝试用更简单的提示重新生成
    if not response or len(response.strip()) < 2:
        simple_prompt = f"请回复用户的话：{message}"
        response = model_manager.generate_response(simple_prompt, max_tokens=128)
        response = response.strip()
        
        # 如果仍然为空，提供友好的默认回复
        if not response:
            response = "我正在学习中，请多包涵。您能换个方式问问吗？"
    
    history.append({"role": "user", "content": message})
    history.append({"role": "assistant", "content": response})
    return history

def create_interface():
    """创建Gradio界面"""
    theme = getattr(gr.themes, UI_CONFIG["theme"].capitalize(), gr.themes.Soft)()
    
    with gr.Blocks(title=UI_CONFIG["title"], theme=theme) as app:
        gr.Markdown(f"# 🤖 {UI_CONFIG['title']}")
        gr.Markdown(UI_CONFIG["description"])
        
        with gr.Row():
            with gr.Column(scale=1):
                gr.Markdown("## 📥 模型管理")
                
                model_dropdown = gr.Dropdown(
                    choices=get_available_models(),
                    label="选择模型",
                    info="选择要下载的AI模型（小于7B参数）"
                )
                
                download_btn = gr.Button("📥 下载并加载模型", variant="primary")
                model_status = gr.Textbox(
                    label="模型状态",
                    value="未加载模型",
                    interactive=False
                )
                
                gr.Markdown("## ⚙️ 设置")
                refresh_btn = gr.Button("🔄 刷新模型列表")
                
            with gr.Column(scale=2):
                gr.Markdown("## 💬 对话")
                
                chatbot = gr.Chatbot(
                    height=UI_CONFIG["chatbot_height"],
                    placeholder="选择并加载模型后开始对话...",
                    type="messages"
                )
                
                with gr.Row():
                    msg_input = gr.Textbox(
                        placeholder="输入您的消息...",
                        scale=4,
                        interactive=False
                    )
                    send_btn = gr.Button("发送", scale=1, interactive=False)
                
                clear_btn = gr.Button("🗑️ 清空对话")
        
        # 事件绑定
        download_btn.click(
            download_and_load_model,
            inputs=[model_dropdown],
            outputs=[model_status, msg_input]
        ).then(
            lambda: gr.update(interactive=True),
            outputs=[send_btn]
        )
        
        refresh_btn.click(
            lambda: gr.update(choices=get_available_models()),
            outputs=[model_dropdown]
        )
        
        msg_input.submit(
            chat_response,
            inputs=[msg_input, chatbot],
            outputs=[chatbot]
        ).then(
            lambda: "",
            outputs=[msg_input]
        )
        
        send_btn.click(
            chat_response,
            inputs=[msg_input, chatbot],
            outputs=[chatbot]
        ).then(
            lambda: "",
            outputs=[msg_input]
        )
        
        clear_btn.click(
            lambda: [],
            outputs=[chatbot]
        )
    
    return app

if __name__ == "__main__":
    print(f"🚀 启动 {UI_CONFIG['title']}...")
    print("📋 功能特性:")
    print("   - 自动获取Hugging Face上小于7B的模型")
    print("   - 本地运行，保护隐私")
    print("   - 支持模型下载和管理")
    print("   - 友好的对话界面")
    print("   - 完整的日志记录")
    print("   - 可配置的模型参数")
    print(f"\n🌐 服务器将在 http://localhost:{SERVER_CONFIG['port']} 启动")
    
    app = create_interface()
    app.launch(
        server_name=SERVER_CONFIG["host"],
        server_port=SERVER_CONFIG["port"],
        share=SERVER_CONFIG["share"],
        inbrowser=SERVER_CONFIG["inbrowser"],
        show_error=SERVER_CONFIG["show_error"]
    )