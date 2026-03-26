"""
MathFlow v13
============
两个功能：

1. 快捷键模式（默认）：监听 Ctrl+Alt+V，清洗剪贴板中从 MathType 复制的
   AMSLaTeX 文本，处理后写回剪贴板，直接粘贴到 Typora 即可。

2. EPS 批量转换模式：处理当前文件夹下所有 .eps 文件（MathType 导出），
   将每个 EPS 中嵌入的 MathML 解析为 LaTeX，输出同名 .md 文件。
   运行方式：
       python mathtype_clean_to_claude_better.py --eps
   或指定目录：
       python mathtype_clean_to_claude_better.py --eps /path/to/folder
"""

import pyperclip
import re
import keyboard
import sys
import argparse
from pathlib import Path
from datetime import datetime
from xml.etree import ElementTree as ET

# ──────────────────────────────────────────────────────────────────────────────
#  常量表
# ──────────────────────────────────────────────────────────────────────────────
GREEK = {
    'α':'\\alpha','β':'\\beta','γ':'\\gamma','δ':'\\delta','ε':'\\epsilon',
    'ζ':'\\zeta','η':'\\eta','θ':'\\theta','λ':'\\lambda','μ':'\\mu',
    'ν':'\\nu','ξ':'\\xi','π':'\\pi','ρ':'\\rho','σ':'\\sigma','τ':'\\tau',
    'υ':'\\upsilon','φ':'\\phi','χ':'\\chi','ψ':'\\psi','ω':'\\omega',
    'Γ':'\\Gamma','Δ':'\\Delta','Θ':'\\Theta','Λ':'\\Lambda','Ξ':'\\Xi',
    'Π':'\\Pi','Σ':'\\Sigma','Φ':'\\Phi','Ψ':'\\Psi','Ω':'\\Omega',
}
OP_MAP = {
    '·':'\\cdot ','⋅':'\\cdot ','×':'\\times ','÷':'\\div ',
    '±':'\\pm ','∓':'\\mp ','≤':'\\leq ','≥':'\\geq ','≠':'\\neq ',
    '∞':'\\infty','∈':'\\in ','∉':'\\notin ','⊂':'\\subset ','⊃':'\\supset ',
    '∩':'\\cap ','∪':'\\cup ','→':'\\rightarrow ','←':'\\leftarrow ',
    '−':'-','＋':'+',
}
ACC_MAP = {'→':'\\vec','⃗':'\\vec','˙':'\\dot','¨':'\\ddot','¯':'\\bar','^':'\\hat'}
MML_NS = 'http://www.w3.org/1998/Math/MathML'


# ──────────────────────────────────────────────────────────────────────────────
#  功能一：剪贴板 AMSLaTeX 清洗器
# ──────────────────────────────────────────────────────────────────────────────
class MathFlowConverter:
    def __init__(self):
        # 注意：\{ \} 已移出此处，在 fix_symbols 中精确处理
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
        """在 \left\{...\right. 块中注入 \begin{matrix}...\end{matrix} 和 \\"""
        def replacer(m):
            inner = m.group(1)
            lines = [l.strip() for l in inner.splitlines() if l.strip()]
            lines = [re.sub(r'\s*\\\\\s*$', '', l) for l in lines]
            body = " \\\\\n".join(lines)
            return (r'\left\{' + '\n'
                    + r'\begin{matrix}' + '\n'
                    + body + '\n'
                    + r'\end{matrix}' + '\n'
                    + r'\right.')
        return re.sub(r'\\left\s*\\\{([\s\S]*?)\\right\s*\.', replacer, text)

    def reformat_layout(self, text):
        text = text.replace(r'\\', '\n')
        lines = [l.strip() for l in text.splitlines() if l.strip()]
        final_lines = []
        i = 0
        while i < len(lines):
            line = lines[i]
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
            elif re.search(r'[\x5c\^/_\{]', line):
                split_match = re.match(r'^([\u4e00-\u9fa5\uff1a:]+)(.*)$', line)
                if split_match and split_match.group(2).strip():
                    title, formula = split_match.groups()
                    final_lines.append(title.strip())
                    final_lines.append(f"$$\n{formula.strip()}\n$$")
                else:
                    final_lines.append(f"$$\n{line}\n$$")
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
            processed = self.inject_matrix(processed)
            processed = self.reformat_layout(processed)
            if processed.strip() != raw.strip():
                pyperclip.copy(processed)
                now = datetime.now().strftime("%H:%M:%S")
                print(f"[{now}] ✓ MathFlow 处理完成")
            else:
                print(".", end="", flush=True)
        except Exception as e:
            print(f"\n[运行异常]: {e}")


# ──────────────────────────────────────────────────────────────────────────────
#  功能二：EPS → MD 批量转换器
# ──────────────────────────────────────────────────────────────────────────────
# 已知 MathML 标签集，按长度从长到短排序（防止短标签名误匹配长标签名的前缀）
_KNOWN_MML_TAGS = sorted([
    'munderover', 'mmultiscripts', 'mlabeledtr', 'semantics', 'annotation',
    'msubsup', 'mfenced', 'menclose', 'mphantom', 'mpadded', 'mstyle',
    'merror', 'mspace', 'mtext', 'mfrac', 'msqrt', 'mroot', 'munder',
    'mover', 'mtable', 'msub', 'msup', 'mrow', 'mtr', 'mtd', 'math',
    'mi', 'mn', 'mo', 'ms', 'maction',
], key=len, reverse=True)
# 匹配：<已知标签名 紧跟 属性名= （标签名和属性名之间缺空格）
_TAG_SPACE_PAT = re.compile(
    r'<(' + '|'.join(re.escape(t) for t in _KNOWN_MML_TAGS) + r')([a-zA-Z]+=)'
)


def _fix_mathml(raw_ml):
    """修复 MathType 输出的非标准 MathML，使其可被 ElementTree 解析"""
    fixes = [
        (r"display='block'",                        'display="block"'),
        (r"xmlns='([^']*)'",                        r'xmlns="\1"'),
        (r"columnalign='([^']*)'",                  r'columnalign="\1"'),
        (r"stretchy='([^']*)'",                     r'stretchy="\1"'),
        (r'<mostretchy="([^"]*)"(?:>|/>)',          r'<mo stretchy="\1">'),
        (r'<mtablecolumnalign=',                    r'<mtable columnalign='),
        (r'<math(display=)',                        r'<math \1'),
        (r'(display="block")(xmlns=)',              r'\1 \2'),
        (r'<mfenced(close="[^"]*")(open="[^"]*")', r'<mfenced \1 \2'),
        # MathType 有时省略标签名与属性间的空格，如 <mstyledisplaystyle=...> <moveraccent=...>
        # 用已知标签集合精确匹配，避免误拆合法标签名（如 <msubsup> 不应被拆）
        # 匹配模式：<已知标签名 + 紧跟的属性名= → 插入空格
        # 此规则在单引号→双引号之前应用，但在列表中定义，实际在循环后单独调用
        # （见下方 TAG_SPACE_PAT 单独处理）
        # 将残余的单引号属性值统一转为双引号，如 displaystyle='true'
        (r"(\s[a-zA-Z]+)='([^']*)'",               r'\1="\2"'),
    ]
    for pat, repl in fixes:
        raw_ml = re.sub(pat, repl, raw_ml)
    # 修复标签名与属性名之间缺空格（需在单引号→双引号规则之后，避免二次干扰）
    raw_ml = _TAG_SPACE_PAT.sub(r'<\1 \2', raw_ml)
    raw_ml = re.sub(r'<\?xml[^?]*\?>', '', raw_ml)
    raw_ml = re.sub(r'<!--.*?-->', '', raw_ml, flags=re.DOTALL)
    # 修复裸 &（行拼接处产生的非实体 &），避免 XML 解析报 invalid token
    raw_ml = re.sub(r'&(?!amp;|lt;|gt;|quot;|apos;|#\d+;|#x[0-9a-fA-F]+;)', '&amp;', raw_ml)
    return raw_ml.strip()


def _extract_mathml(filepath):
    """从 EPS 文件提取并修复 MathML 字符串"""
    with open(filepath, "rb") as f:
        raw = f.read().decode("latin-1")
    start = raw.find('%MathType!MathML')
    if start == -1:
        raise ValueError("未找到 MathML 块，请确认该 EPS 由 MathType 导出")
    end = raw.find('\n/MT', start)
    block = raw[start:end]
    lines = block.splitlines()
    ml = "".join(l[1:] for l in lines if l.startswith('%') and not l.startswith('%%'))
    ml = re.sub(r'^MathType!MathML!1!1!\+-', '', ml)
    ml = re.sub(r'<!--MathType@End.*$', '', ml).rstrip('!')
    return _fix_mathml(ml)


def _node_to_latex(node):
    """
    递归将 MathML 节点转为 LaTeX 字符串。

    关键修复（v13）：MathType 有时将括号内容平铺在 <msup>/<msub> 下，
    而不是用 <mrow> 包裹。例如：
        <msup><mo>(</mo><mi>c</mi><mo>·</mo><msub>...</msub><mo>)</mo><mn>2</mn></msup>
    标准 MathML 应为 2 个子节点（base + exp），
    异常情况为 n 个子节点（前 n-1 个合并为 base，最后一个为 exp）。
    """
    tag = node.tag.replace(f'{{{MML_NS}}}', '')
    text = (node.text or '').strip()
    ch = list(node)

    if tag in ('math', 'mtd', 'mrow', 'mstyle', 'mpadded', 'mphantom'):
        # Bug2修复：相邻 <mi> 中，希腊字母命令（\rho等）后紧跟普通字母时加空格
        # 否则 \rho + c → \rhoc，LaTeX 会把它当作未知命令
        parts = []
        for i, c in enumerate(ch):
            part = _node_to_latex(c)
            if i + 1 < len(ch):
                ctag = c.tag.replace(f'{{{MML_NS}}}', '')
                ntag = ch[i+1].tag.replace(f'{{{MML_NS}}}', '')
                ctext = (c.text or '').strip()
                ntext = (ch[i+1].text or '').strip()
                c_is_greek = ctag == 'mi' and ctext in GREEK
                n_is_plain  = ntag == 'mi' and ntext not in GREEK
                # 只在希腊字母后跟普通字母时补空格
                if c_is_greek and n_is_plain:
                    part = part + ' '
            parts.append(part)
        return ''.join(parts)
    if tag == 'mtr':
        return ''.join(_node_to_latex(c) for c in ch)
    if tag == 'mtable':
        rows = [''.join(_node_to_latex(c) for c in mtr)
                for mtr in ch if mtr.tag.replace(f'{{{MML_NS}}}', '') == 'mtr']
        rows = [r for r in rows if r.strip()]
        return ' \\\\\n'.join(rows)
    if tag == 'mfenced':
        open_ch  = node.get('open',  '(')
        close_ch = node.get('close', ')')
        inner = ''.join(_node_to_latex(c) for c in ch)
        if open_ch == '{':
            return (r'\left\{' + '\n'
                    + r'\begin{matrix}' + '\n'
                    + inner + '\n'
                    + r'\end{matrix}' + '\n'
                    + r'\right.')
        ld = '\\left'  + ('\\' + open_ch  if open_ch  in '{}' else open_ch)
        rd = '\\right' + ('\\' + close_ch if close_ch in '{}' else close_ch)
        return f'{ld}{inner}{rd}'

    if tag == 'msup':
        if len(ch) == 2:
            base = _node_to_latex(ch[0])
            exp  = _node_to_latex(ch[1])
        else:
            # MathType 异常：多子节点平铺，前 n-1 个为 base，最后一个为 exp
            base = ''.join(_node_to_latex(c) for c in ch[:-1])
            exp  = _node_to_latex(ch[-1])
        base_str = f'{{{base}}}' if len(base) > 1 else base
        return f'{base_str}^{{{exp}}}'

    if tag == 'msub':
        if len(ch) == 2:
            base = _node_to_latex(ch[0])
            sub  = _node_to_latex(ch[1])
        else:
            base = ''.join(_node_to_latex(c) for c in ch[:-1])
            sub  = _node_to_latex(ch[-1])
        base_str = f'{{{base}}}' if len(base) > 1 else base
        return f'{base_str}_{{{sub}}}'

    if tag == 'msubsup':
        base = _node_to_latex(ch[0])
        sub  = _node_to_latex(ch[1])
        sup  = _node_to_latex(ch[2])
        return f'{base}_{{{sub}}}^{{{sup}}}'
    if tag == 'mfrac':
        return f'\\frac{{{_node_to_latex(ch[0])}}}{{{_node_to_latex(ch[1])}}}'
    if tag == 'msqrt':
        return f'\\sqrt{{{" ".join(_node_to_latex(c) for c in ch)}}}'
    if tag == 'mroot':
        return f'\\sqrt[{_node_to_latex(ch[1])}]{{{_node_to_latex(ch[0])}}}'
    if tag == 'munderover':
        # Bug1修复：munderover 有三个子节点：base、下限、上限
        base  = _node_to_latex(ch[0])
        under = _node_to_latex(ch[1])
        over  = _node_to_latex(ch[2])
        # 积分号特殊处理为 \int_{下}^{上}
        if base == '\\int' or (ch[0].text or '').strip() == '\u222b':
            return f'\\int_{{{under}}}^{{{over}}}'
        return f'\\overset{{{over}}}{{\\underset{{{under}}}{{{base}}}}}'

    if tag == 'mover':
        acc = _node_to_latex(ch[1])
        cmd = ACC_MAP.get(acc, f'\\overset{{{acc}}}')
        return f'{cmd}{{{_node_to_latex(ch[0])}}}'
    if tag == 'munder':
        return f'\\underset{{{_node_to_latex(ch[1])}}}{{{_node_to_latex(ch[0])}}}'
    if tag == 'mspace':
        return ' '
    if tag == 'mi':
        if text in GREEK:
            return GREEK[text]
        if text and all('\u4e00' <= c <= '\u9fff' or c in '，。：；！？、：' for c in text):
            return f'\\text{{{text}}}'
        # 多字母 mi（如 cos sin arcsin ln）→ 加反斜杠变为 LaTeX 命令
        if len(text) > 1 and text.isalpha():
            return f'\\{text}'
        return text
    if tag == 'mn':
        return text
    if tag == 'mo':
        if (text or '').strip() == '\u222b':
            return '\\int'
        return OP_MAP.get(text, text)
    return ''.join(_node_to_latex(c) for c in ch) or text


def eps_to_md_content(filepath):
    """将单个 EPS 文件转换为 Markdown 字符串"""
    ml = _extract_mathml(filepath)
    ET.register_namespace('', MML_NS)
    root = ET.fromstring(ml)

    mtable = root.find(f'{{{MML_NS}}}mtable')
    if mtable is None:
        mtable = root

    paragraphs = []
    for mtr in mtable:
        if mtr.tag.replace(f'{{{MML_NS}}}', '') != 'mtr':
            continue
        mtd_list = list(mtr)
        if not mtd_list:
            continue
        latex = _node_to_latex(mtd_list[0]).strip()
        if not latex:
            continue
        plain = re.sub(r'\\text\{([^}]*)\}', r'\1', latex)
        is_text = all(
            '\u4e00' <= c <= '\u9fff'
            or c in '，。：；！？、：:（）() '
            for c in plain
        )
        if is_text:
            paragraphs.append(plain.strip())
        else:
            paragraphs.append(f'$$\n{latex}\n$$')

    return '\n\n'.join(p for p in paragraphs if p.strip())


def batch_convert_eps(folder):
    """批量处理文件夹下所有 .eps 文件，输出同名 .md"""
    folder = Path(folder)
    eps_files = sorted(folder.glob("*.eps"))
    if not eps_files:
        print(f"[!] 未找到 .eps 文件：{folder}")
        return
    print(f"[EPS 批量转换] 找到 {len(eps_files)} 个文件，开始处理...\n")
    ok, fail = 0, 0
    for eps in eps_files:
        md_path = eps.with_suffix('.md')
        try:
            content = eps_to_md_content(eps)
            md_path.write_text(content, encoding='utf-8')
            print(f"  ✓  {eps.name}  →  {md_path.name}")
            ok += 1
        except Exception as e:
            print(f"  ✗  {eps.name}  失败：{e}")
            fail += 1
    print(f"\n完成：{ok} 成功，{fail} 失败。")


# ──────────────────────────────────────────────────────────────────────────────
#  入口
# ──────────────────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(description='MathFlow v13')
    parser.add_argument('--eps', nargs='?', const='.', metavar='FOLDER',
                        help='批量转换文件夹下的 .eps 文件为 .md（默认当前目录）')
    args = parser.parse_args()

    if args.eps is not None:
        batch_convert_eps(args.eps)
    else:
        converter = MathFlowConverter()
        print("========================================")
        print("   MathFlow v13 (clipboard + EPS->MD)  ")
        print("========================================")
        print("状态: 监听中 (Ctrl + Alt + V)")
        print("提示: 批量转换 EPS 请用 --eps 参数运行")
        keyboard.add_hotkey('ctrl+alt+v', converter.run)
        try:
            keyboard.wait()
        except KeyboardInterrupt:
            sys.exit(0)


if __name__ == "__main__":
    main()
