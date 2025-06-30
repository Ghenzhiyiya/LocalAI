#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
路径修复脚本
将model_config.json中的相对路径转换为绝对路径
"""

import os
import json
from pathlib import Path

def fix_model_paths():
    """修复模型配置文件中的路径"""
    config_file = "model_config.json"
    
    if not os.path.exists(config_file):
        print("❌ 配置文件不存在")
        return
    
    # 读取配置
    with open(config_file, 'r', encoding='utf-8') as f:
        model_info = json.load(f)
    
    # 修复路径
    updated = False
    for model_id, info in model_info.items():
        old_path = info.get('path', '')
        if old_path and not os.path.isabs(old_path):
            # 转换为绝对路径
            abs_path = os.path.abspath(old_path)
            info['path'] = abs_path
            updated = True
            print(f"✅ 修复路径: {model_id}")
            print(f"   旧路径: {old_path}")
            print(f"   新路径: {abs_path}")
            
            # 检查文件是否存在
            if os.path.exists(abs_path):
                print(f"   状态: ✅ 文件存在")
            else:
                print(f"   状态: ❌ 文件不存在")
            print()
    
    if updated:
        # 保存更新后的配置
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(model_info, f, ensure_ascii=False, indent=2)
        print("✅ 配置文件已更新")
    else:
        print("ℹ️  所有路径都已是绝对路径，无需修复")

if __name__ == "__main__":
    print("🔧 开始修复模型路径...")
    fix_model_paths()
    print("🎉 修复完成！")
    input("按回车键退出...")