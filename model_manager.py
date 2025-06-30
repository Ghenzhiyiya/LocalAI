#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LocalAI 模型管理工具
用于管理已下载的模型，查看模型信息，清理缓存等
"""

import os
import json
import shutil
from pathlib import Path
from typing import Dict, List
from config import DIRECTORY_CONFIG

class ModelManagerCLI:
    def __init__(self):
        self.models_dir = Path(DIRECTORY_CONFIG["models_dir"])
        self.config_file = DIRECTORY_CONFIG["config_file"]
        self.model_info = self.load_model_config()
    
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
    
    def get_model_size(self, model_path: str) -> str:
        """获取模型文件大小"""
        try:
            size_bytes = os.path.getsize(model_path)
            if size_bytes < 1024**2:
                return f"{size_bytes/1024:.1f} KB"
            elif size_bytes < 1024**3:
                return f"{size_bytes/(1024**2):.1f} MB"
            else:
                return f"{size_bytes/(1024**3):.1f} GB"
        except:
            return "未知"
    
    def list_models(self):
        """列出所有已下载的模型"""
        print("\n" + "="*60)
        print("📋 已下载的模型列表")
        print("="*60)
        
        if not self.model_info:
            print("❌ 没有找到已下载的模型")
            return
        
        for i, (model_id, info) in enumerate(self.model_info.items(), 1):
            if info.get('downloaded', False):
                model_path = info.get('path', '')
                size = self.get_model_size(model_path) if os.path.exists(model_path) else "文件不存在"
                status = "✅ 可用" if os.path.exists(model_path) else "❌ 文件缺失"
                
                print(f"\n{i}. {model_id}")
                print(f"   路径: {model_path}")
                print(f"   大小: {size}")
                print(f"   状态: {status}")
                print(f"   文件: {info.get('file', '未知')}")
    
    def delete_model(self, model_id: str):
        """删除指定模型"""
        if model_id not in self.model_info:
            print(f"❌ 模型 {model_id} 不存在")
            return
        
        model_path = self.model_info[model_id].get('path', '')
        
        # 删除模型文件
        if os.path.exists(model_path):
            try:
                os.remove(model_path)
                print(f"✅ 已删除模型文件: {model_path}")
            except Exception as e:
                print(f"❌ 删除模型文件失败: {e}")
                return
        
        # 删除模型目录（如果为空）
        model_dir = Path(model_path).parent
        try:
            if model_dir.exists() and not any(model_dir.iterdir()):
                model_dir.rmdir()
                print(f"✅ 已删除空目录: {model_dir}")
        except:
            pass
        
        # 从配置中移除
        del self.model_info[model_id]
        self.save_model_config()
        print(f"✅ 已从配置中移除模型: {model_id}")
    
    def clean_cache(self):
        """清理缓存和无效文件"""
        print("\n🧹 开始清理缓存...")
        
        # 检查配置中的模型文件是否存在
        invalid_models = []
        for model_id, info in self.model_info.items():
            model_path = info.get('path', '')
            if not os.path.exists(model_path):
                invalid_models.append(model_id)
        
        # 移除无效的模型配置
        for model_id in invalid_models:
            del self.model_info[model_id]
            print(f"🗑️  移除无效配置: {model_id}")
        
        if invalid_models:
            self.save_model_config()
        
        # 清理空目录
        if self.models_dir.exists():
            for item in self.models_dir.rglob('*'):
                if item.is_dir() and not any(item.iterdir()):
                    try:
                        item.rmdir()
                        print(f"🗑️  删除空目录: {item}")
                    except:
                        pass
        
        print("✅ 缓存清理完成")
    
    def show_stats(self):
        """显示统计信息"""
        print("\n" + "="*60)
        print("📊 模型统计信息")
        print("="*60)
        
        total_models = len(self.model_info)
        valid_models = 0
        total_size = 0
        
        for model_id, info in self.model_info.items():
            model_path = info.get('path', '')
            if os.path.exists(model_path):
                valid_models += 1
                try:
                    total_size += os.path.getsize(model_path)
                except:
                    pass
        
        print(f"总模型数量: {total_models}")
        print(f"有效模型数量: {valid_models}")
        print(f"无效模型数量: {total_models - valid_models}")
        print(f"总占用空间: {total_size/(1024**3):.2f} GB")
        print(f"模型存储目录: {self.models_dir.absolute()}")
    
    def interactive_menu(self):
        """交互式菜单"""
        while True:
            print("\n" + "="*60)
            print("🤖 LocalAI 模型管理工具")
            print("="*60)
            print("1. 📋 列出所有模型")
            print("2. 🗑️  删除指定模型")
            print("3. 🧹 清理缓存")
            print("4. 📊 显示统计信息")
            print("5. 🚪 退出")
            print("="*60)
            
            choice = input("请选择操作 (1-5): ").strip()
            
            if choice == '1':
                self.list_models()
            elif choice == '2':
                self.list_models()
                if self.model_info:
                    model_id = input("\n请输入要删除的模型ID: ").strip()
                    if model_id:
                        confirm = input(f"确认删除模型 '{model_id}' 吗? (y/N): ").strip().lower()
                        if confirm == 'y':
                            self.delete_model(model_id)
            elif choice == '3':
                confirm = input("确认清理缓存吗? (y/N): ").strip().lower()
                if confirm == 'y':
                    self.clean_cache()
            elif choice == '4':
                self.show_stats()
            elif choice == '5':
                print("👋 再见！")
                break
            else:
                print("❌ 无效选择，请重试")
            
            input("\n按回车键继续...")

def main():
    """主函数"""
    import sys
    
    manager = ModelManagerCLI()
    
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        if command == 'list':
            manager.list_models()
        elif command == 'clean':
            manager.clean_cache()
        elif command == 'stats':
            manager.show_stats()
        elif command == 'delete' and len(sys.argv) > 2:
            model_id = sys.argv[2]
            manager.delete_model(model_id)
        else:
            print("用法:")
            print("  python model_manager.py list     - 列出所有模型")
            print("  python model_manager.py clean    - 清理缓存")
            print("  python model_manager.py stats    - 显示统计信息")
            print("  python model_manager.py delete <model_id> - 删除指定模型")
            print("  python model_manager.py          - 交互式菜单")
    else:
        manager.interactive_menu()

if __name__ == "__main__":
    main()