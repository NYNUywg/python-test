# 🌍 GLA Family 多国家企业爬虫系统

## 📁 目录结构

```
country_scrapers/
├── templates/           # 模板文件
│   └── country_template.py    # 通用国家爬虫模板
├── scripts/            # 可执行脚本
│   ├── china.py       # 中国企业爬虫
│   ├── saudi_arabia.py # 沙特阿拉伯企业爬虫
│   ├── uae.py         # 阿联酋企业爬虫
│   └── main.py        # 多国家管理器
├── data/              # 生成的数据文件
│   ├── CHINA_companies.xlsx
│   ├── SAUDI_ARABIA_companies.xlsx
│   └── UAE_companies.xlsx
└── docs/              # 文档
    ├── README_COUNTRY_SCRAPER.md
    └── FINAL_SUMMARY.md
```

## 🚀 快速开始

### 1. 激活虚拟环境
```bash
cd /Users/sm3246/Documents/python/python-test/glafamiy
source venv/bin/activate
```

### 2. 运行现有脚本
```bash
# 运行中国企业爬虫
python country_scrapers/scripts/china.py

# 运行沙特阿拉伯企业爬虫
python country_scrapers/scripts/saudi_arabia.py

# 运行阿联酋企业爬虫
python country_scrapers/scripts/uae.py
```

### 3. 创建新国家脚本
```bash
# 复制模板
cp country_scrapers/templates/country_template.py country_scrapers/scripts/pakistan.py

# 编辑文件，修改 TARGET_COUNTRY = "PAKISTAN"
# 然后运行
python country_scrapers/scripts/pakistan.py
```

## 📊 数据输出

所有生成的Excel文件会自动保存到 `country_scrapers/data/` 目录下：
- `CHINA_companies.xlsx` - 中国企业数据
- `SAUDI_ARABIA_companies.xlsx` - 沙特企业数据  
- `UAE_companies.xlsx` - 阿联酋企业数据

## 📚 文档

详细使用说明请查看：
- `docs/README_COUNTRY_SCRAPER.md` - 完整使用指南
- `docs/FINAL_SUMMARY.md` - 功能总结

## ✨ 特性

- ✅ Cookie登录支持
- ✅ 国家筛选功能
- ✅ 邮箱自动提取
- ✅ 断点续传
- ✅ Excel格式输出
- ✅ 实时数据保存

---
**版本**: v2.0  
**最后更新**: 2025-01-06 