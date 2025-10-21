#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GLA Family UAE 企业爬虫
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from core_scraper import run_country_scraper

# 🌍 目标国家：阿联酋
TARGET_COUNTRY = "UAE"

if __name__ == "__main__":
    run_country_scraper(TARGET_COUNTRY) 