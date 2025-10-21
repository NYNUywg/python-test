#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GLA Family 新国家爬虫模板
使用方法：
1. 复制此文件到 scripts/ 目录
2. 修改下面的国家名称
3. 运行脚本
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from core_scraper import run_country_scraper

# 🌍 在这里修改目标国家名称
TARGET_COUNTRY = "Pakistan"  # 例如: "Pakistan", "India", "Germany", "United States"

if __name__ == "__main__":
    run_country_scraper(TARGET_COUNTRY) 