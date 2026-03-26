import pyperclip
import re
import keyboard
import sys
from datetime import datetime

class MathFlowConverter:
    def __init__(self):
        self.symbol_map = {
            r'\~': r'\sim ',
            r'\_': '_',
            r'\^': '^',
            r'\sin \}': r'\sin ',
            r'\cos \}': r'\cos ',
            r'\tan \}': r'\tan ',
        }

    def decode_unicode(self, text):
        return re.sub(r'\\unicode\{0x([0-9a-fA-F]+)\}',
                      lambda m: chr(int(m.group(1), 16)), text)

    def clean_redundancy(self, text):
        text = re.sub(r'\\begin\{(gathered|aligned|array|equation|displaymath|center)\}', '', text, flags=re.I)
        text = re.sub(r'\\end\{(gathered|aligned|array|equation|displaymath|center)\}', '', text, flags=re.I)
        text = re.sub(r'^\s*(\\\[|\$\$?)\s*', '', text, flags=re.DOTALL)
        text = re.sub(r'\s*(\\\]|\$\$?)\s*$', '', text, flags=re.DOTALL)
        text = text.replace(r'\hfill', '').replace('\\hfill', '')
        text = re.sub(r'\\text\{([\s\S]*?)\}', r'\1', text)
        last_text = ""
        while last_text != text:
            last_text = text
            text = re.sub(r'(?<!\\)\{\{([^{}]*?)\}\}', r'{\1}', text)
        return text.replace('{}', '').strip()

    def fix_symbols(self, text):
        for err, fix in self.symbol_map.items():
            text = text.replace(err, fix)
        # \{ \} 只在非 \left\{ / \right\} 上下文中替换为裸括号
        text = re.sub(r'(?<!\\left)(?<!\\right)\\(\{|\})', lambda m: m.group(1), text)
        return text

    def inject_matrix(self, text):
        """
        后处理：在 \left\{...\right. 块中
          - \left\{ 后追加 \begin{matrix}
          - \right. 前追加 \end{matrix}
          - 各方程行之间追加 \\
        """
        def replacer(m):
            inner = m.group(1)
            lines = [l.strip() for l in inner.splitlines() if l.strip()]
            # 去掉每行末尾可能残留的 \\
            lines = [re.sub(r'\s*\\\\\s*$', '', l) for l in lines]
            body = " \\\\\n".join(lines)
            return (
                r'\left\{' + '\n'
                + r'\begin{matrix}' + '\n'
                + body + '\n'
                + r'\end{matrix}' + '\n'
                + r'\right.'
            )

        return re.sub(
            r'\\left\s*\\\{([\s\S]*?)\\right\s*\.',
            replacer,
            text
        )

    def reformat_layout(self, text):
        text = text.replace(r'\\', '\n')
        lines = [l.strip() for l in text.splitlines() if l.strip()]

        final_lines = []
        i = 0
        while i < len(lines):
            line = lines[i]

            # \left\{ 块：收集到 \right 结束，整体包进一个 $$ 块
            if re.search(r'\\left', line):
                block_lines = [line]
                j = i + 1
                while j < len(lines):
                    block_lines.append(lines[j])
                    if re.search(r'\\right', lines[j]):
                        break
                    j += 1
                i = j
                formula = "\n".join(block_lines)
                final_lines.append(f"$$\n{formula}\n$$")

            # 普通含 LaTeX 的行
            elif re.search(r'[\x5c\^/_\{]', line):
                split_match = re.match(r'^([\u4e00-\u9fa5\uff1a:]+)(.*)$', line)
                if split_match and split_match.group(2).strip():
                    title, formula = split_match.groups()
                    final_lines.append(title.strip())
                    final_lines.append(f"$$\n{formula.strip()}\n$$")
                else:
                    final_lines.append(f"$$\n{line}\n$$")

            # 纯文字行
            else:
                final_lines.append(line)

            i += 1

        return re.sub(r'\n{3,}', '\n\n', "\n".join(final_lines))

    def run(self):
        try:
            raw = pyperclip.paste()
            if not raw or not raw.strip():
                return

            processed = self.decode_unicode(raw)
            processed = self.clean_redundancy(processed)
            processed = self.fix_symbols(processed)
            processed = self.inject_matrix(processed)   # 注入 matrix 环境
            processed = self.reformat_layout(processed)

            if processed.strip() != raw.strip():
                pyperclip.copy(processed)
                now = datetime.now().strftime("%H:%M:%S")
                print(f"[{now}] ✓ MathFlow 处理完成")
            else:
                print(".", end="", flush=True)
        except Exception as e:
            print(f"\n[运行异常]: {e}")


if __name__ == "__main__":
    converter = MathFlowConverter()
    print("========================================")
    print("   MathFlow v11 (inject matrix env)     ")
    print("========================================")
    print("状态: 监听中 (Ctrl + Alt + V)")
    keyboard.add_hotkey('ctrl+alt+v', converter.run)
    try:
        keyboard.wait()
    except KeyboardInterrupt:
        sys.exit(0)
