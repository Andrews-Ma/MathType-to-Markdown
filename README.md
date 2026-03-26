# MathFlow (v1)

**MathFlow** 是一个用于优化 MathType 公式到 Markdown (Typora) 转换体验的自动化工具包。

## 🛠️ 脚本功能差异说明

本项目包含两个独立功能的 Python 脚本，请根据您的需求选择运行：

### 1. `mathflow_v1_hotkey.py` (剪贴板即时转换)
- **适用场景**：边写文档边转换。
- **功能**：监听全局快捷键 `Ctrl + Alt + V`。当你在 MathType 中复制公式后，按下快捷键，脚本会自动清洗 LaTeX 源码中的冗余标签、还原中文字符、并注入 `matrix` 环境以确保 Typora 渲染不重叠，最后将处理好的结果写回剪贴板。
- **特点**：无需保存文件，即复制即转换。

### 2. `mathflow_v1_batch_eps.py` (EPS 批量转换工具)
- **适用场景**：处理包含大量旧公式图片的文件夹。
- **功能**：通过命令行扫描指定文件夹下的所有 `.eps` 文件，解析其内嵌的 MathML 数据，并自动生成对应的 `.md` 公式文件。
- **特点**：支持批量处理，解决了 EPS 图片无法直接编辑的难题。

---

## 🚀 快速开始

### 环境配置 (Miniconda/Python)
在终端中进入项目目录，执行：
```bash
pip install -r requirements.txt