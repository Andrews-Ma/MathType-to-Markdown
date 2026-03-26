[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](https://github.com/Andrews-Ma/MathType-to-Markdown/blob/main/LICENSE.txt)
[![Python](https://img.shields.io/badge/Python-3.9+-3776AB.svg?style=for-the-badge&logo=python&logoColor=ffdd54)](https://www.python.org/)
[![Stars](https://img.shields.io/github/stars/Andrews-Ma/MathType-to-Markdown?style=for-the-badge&logo=github&logoColor=white&label=Stars)](https://github.com/Andrews-Ma/MathType-to-Markdown/stargazers)
[![Forks](https://img.shields.io/github/forks/Andrews-Ma/MathType-to-Markdown?style=for-the-badge&logo=github&logoColor=white&label=Forks)](https://github.com/Andrews-Ma/MathType-to-Markdown/network/members)
[![Issues](https://img.shields.io/github/issues/Andrews-Ma/MathType-to-Markdown?style=for-the-badge&logo=github&logoColor=white&label=Issues)](https://github.com/Andrews-Ma/MathType-to-Markdown/issues)
[![Last Commit](https://img.shields.io/github/last-commit/Andrews-Ma/MathType-to-Markdown?style=for-the-badge&logo=github&logoColor=white&label=Last%20Commit)](https://github.com/Andrews-Ma/MathType-to-Markdown/commits/main)

# MathFlow

**Typora 用户的 MathType 公式救星**  
一键清洗 LaTeX + 批量还原 EPS 为可编辑 Markdown 公式

让学术写作、论文笔记、博客创作中的公式转换不再痛苦！

## ✨ 核心功能

- **实时快捷键转换**（`mathflow_v1_hotkey.py`）  
  在 MathType 中复制公式后，按 **Ctrl + Alt + V** 即可自动清洗 LaTeX 源码（去除冗余标签、还原中文字符、注入 `matrix` 环境），直接粘贴到 Typora 中完美显示。

- **EPS 批量转换**（`mathflow_v1_batch_eps.py`）  
  扫描指定文件夹中的所有 `.eps` 文件，自动提取 MathML 并生成对应的 `.md` 可编辑公式文件，彻底解决旧公式图片无法直接使用的难题。

- **纯 Python 实现**，轻量、无需复杂环境，专为 Typora 用户优化。

## 🎥 演示（建议在此处添加 GIF）

**实时快捷键演示**  
![Hotkey Demo](assets/hotkey-demo.gif)

**EPS 批量转换演示**  
![Batch Demo](assets/batch-demo.gif)

> **提示**：请在 `assets/` 文件夹中放入对应的 GIF 文件，效果会非常直观。

## 🚀 快速开始

### 1. 环境准备

```bash
# 克隆仓库
git clone https://github.com/Andrews-Ma/MathType-to-Markdown.git
cd MathType-to-Markdown

# 安装依赖（推荐使用 Miniconda 或虚拟环境）
pip install -r requirements.txt
