#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GLA Family 爬虫启动器
快速选择和运行国家爬虫
"""

import os
import sys
import subprocess

def main():
    print("🌍 GLA Family 多国家企业爬虫系统")
    print("=" * 50)
    
    # 可用的脚本
    scripts = {
        "1": ("中国", "country_scrapers/scripts/china.py"),
        "2": ("沙特阿拉伯", "country_scrapers/scripts/saudi_arabia.py"),
        "3": ("阿联酋", "country_scrapers/scripts/uae.py"),
        "4": ("多国家管理器", "country_scrapers/scripts/main.py")
    }
    
    print("\n📋 可用的爬虫脚本:")
    for key, (name, _) in scripts.items():
        print(f"  {key}. {name}")
    
    print("\n💡 提示:")
    print("  - 数据文件会保存到 country_scrapers/data/ 目录")
    print("  - 支持断点续传，可随时中断和恢复")
    print("  - 建议同时运行不超过3个脚本")
    
    while True:
        choice = input("\n请选择要运行的脚本 (1-4, q退出): ").strip()
        
        if choice.lower() == 'q':
            print("👋 再见！")
            break
        
        if choice in scripts:
            name, script_path = scripts[choice]
            print(f"\n🚀 启动 {name} 爬虫...")
            
            # 检查脚本文件是否存在
            if not os.path.exists(script_path):
                print(f"❌ 错误: 找不到脚本文件 {script_path}")
                continue
            
            try:
                # 运行脚本
                subprocess.run([sys.executable, script_path], check=True)
            except KeyboardInterrupt:
                print(f"\n⏹️ {name} 爬虫已停止")
            except subprocess.CalledProcessError as e:
                print(f"❌ {name} 爬虫运行出错: {e}")
            except Exception as e:
                print(f"❌ 未知错误: {e}")
        else:
            print("❌ 无效选择，请输入 1-4 或 q")

if __name__ == "__main__":
    main() 