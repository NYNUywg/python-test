#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GLA Family 沙特阿拉伯企业爬虫
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from core_scraper import run_country_scraper

if __name__ == "__main__":
    run_country_scraper("Saudi Arabia") 