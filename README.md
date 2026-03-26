Markdown[<image-card alt="License: MIT" src="https://img.shields.io/badge/License-MIT-yellow.svg?style=plastic" ></image-card>](https://github.com/Andrews-Ma/MathType-to-Markdown/blob/main/LICENSE.txt)
[<image-card alt="Python" src="https://img.shields.io/badge/Python-3.9+-3776AB.svg?style=plastic&logo=python&logoColor=ffdd54" ></image-card>](https://www.python.org/)
[<image-card alt="Stars" src="https://img.shields.io/github/stars/Andrews-Ma/MathType-to-Markdown?style=plastic&logo=github&logoColor=white&label=Stars" ></image-card>](https://github.com/Andrews-Ma/MathType-to-Markdown/stargazers)
[<image-card alt="Forks" src="https://img.shields.io/github/forks/Andrews-Ma/MathType-to-Markdown?style=plastic&logo=github&logoColor=white&label=Forks" ></image-card>](https://github.com/Andrews-Ma/MathType-to-Markdown/network/members)
[<image-card alt="Issues" src="https://img.shields.io/github/issues/Andrews-Ma/MathType-to-Markdown?style=plastic&logo=github&logoColor=white&label=Issues" ></image-card>](https://github.com/Andrews-Ma/MathType-to-Markdown/issues)
[<image-card alt="Last Commit" src="https://img.shields.io/github/last-commit/Andrews-Ma/MathType-to-Markdown?style=plastic&logo=github&logoColor=white&label=Last%20Commit" ></image-card>](https://github.com/Andrews-Ma/MathType-to-Markdown/commits/main)

# MathFlow

**Typora 用户的 MathType 公式救星**  
一键清洗 LaTeX + 批量还原 EPS 为可编辑 Markdown 公式

让学术写作、论文笔记、博客创作中的公式转换不再痛苦！

## ✨ 核心功能

- **实时快捷键转换**（`mathflow_v1_hotkey.py`）  
  在 MathType 中复制公式后，按 **Ctrl + Alt + V** 即可自动清洗 LaTeX 源码（去除冗余标签、还原中文字符、注入 `matrix` 环境），直接粘贴到 Typora 中完美显示。

- **EPS 批量转换**（`mathflow_v1_batch_eps.py`）  
  自动扫描文件夹中的所有 `.eps` 文件，提取 MathML 并生成可编辑 Markdown 公式，彻底解决旧公式无法编辑的问题。

- **纯 Python 实现**，轻量、无需复杂环境，专为 Typora 用户深度优化。

## 🎥 演示

**实时快捷键清洗 LaTeX（Ctrl + Alt + V）**  
<image-card alt="Hotkey Demo" src="assets/hotkey-demo.gif" ></image-card>

**EPS 文件批量转换为可编辑 Markdown 公式**  
<image-card alt="Batch Demo" src="assets/batch-demo.gif" ></image-card>

## 🚀 快速开始

### 1. 环境准备
```bash
git clone https://github.com/Andrews-Ma/MathType-to-Markdown.git
cd MathType-to-Markdown
pip install -r requirements.txt
2. 使用方法
实时转换（日常推荐）：

运行 python mathflow_v1_hotkey.py
在 MathType 中复制公式
按 Ctrl + Alt + V
在 Typora 中直接粘贴即可

批量转换 EPS：
Bashpython mathflow_v1_batch_eps.py --folder "你的EPS文件夹路径"
🛠️ 项目特点

智能清理 MathType 冗余标签
完美支持中文字符
自动注入 matrix 环境防止公式重叠
完全开源（MIT License）

📌 Roadmap

 打包成 pip 安装工具（pip install mathtype-to-markdown）
 支持自定义快捷键
 提供图形界面（GUI）
 Typora 插件集成

🤝 贡献
欢迎提交 Issue 和 Pull Request！
觉得好用请点个 Star ⭐ 支持持续更新～

MathFlow —— 让公式在 Typora 中丝滑流畅！
Made with ❤️ for Typora & Academic Writers
