import re
import html
import subprocess
import os

md_path = r"e:\IIIT G\SEM_5\CS353-LC3C\LAB12\Submission_Lab12_QoS\Lab12_QoS_Written_Report.md"
html_path = r"e:\IIIT G\SEM_5\CS353-LC3C\LAB12\Submission_Lab12_QoS\Lab12_QoS_Written_Report.html"
pdf_path = r"e:\IIIT G\SEM_5\CS353-LC3C\LAB12\Submission_Lab12_QoS\Lab12_QoS_Written_Report.pdf"

with open(md_path, "r", encoding="utf-8") as f:
    lines = f.readlines()

def clean_math(expr):
    # 1. Strip LaTeX sizing directives
    expr = re.sub(r'\\left\b', '', expr)
    expr = re.sub(r'\\right\b', '', expr)
    
    # 2. Fractions and text/bold blocks (handle nested up to 3 deep)
    for _ in range(3):
        expr = re.sub(r'\\frac\{([^{}]+)\}\{([^{}]+)\}', r'(\1 / \2)', expr)
        expr = re.sub(r'\\mathbf\{([^{}]+)\}', r'<b>\1</b>', expr)
        expr = re.sub(r'\\text\{([^{}]+)\}', r'\1', expr)
        
    # 3. Mathematical symbols with word boundaries so \le never matches \left
    expr = re.sub(r'\\ge\b', '≥', expr)
    expr = re.sub(r'\\le\b', '≤', expr)
    expr = re.sub(r'\\in\b', '∈', expr)
    expr = re.sub(r'\\to\b', '⟶', expr)
    expr = re.sub(r'\\sum\b', 'Σ', expr)
    expr = expr.replace(r'\Sigma W', 'ΣW')
    expr = expr.replace(r'\sum_{i=1}^4 R_i', 'Σ Rᵢ')
    expr = expr.replace(r'\cdot', '·')
    expr = expr.replace(r'\times', '×')
    expr = expr.replace(r'\implies', '⟹')
    expr = expr.replace(r'\longrightarrow', '⟶')
    expr = expr.replace(r'\;\longrightarrow\;', ' ⟶ ')
    expr = expr.replace(r'\;', ' ')
    expr = expr.replace(r'\Delta', 'Δ')
    expr = expr.replace(r'\max', 'max')
    expr = expr.replace(r'\_', '_')
    expr = expr.replace(r'\quad', ' &nbsp; ')
    
    # 4. Clean Subscripts and Superscripts
    # Special fix for Rate_{f_4} -> Rate<sub>f4</sub>
    expr = re.sub(r'_\{([^{}]+)\}', lambda m: f"<sub>{m.group(1).replace('_', '')}</sub>", expr)
    expr = re.sub(r'_([a-zA-Z0-9])', r'<sub>\1</sub>', expr)
    expr = re.sub(r'\^\{([^{}]+)\}', r'<sup>\1</sup>', expr)
    
    # 5. Clean up redundant brackets and stray backslashes
    expr = expr.replace('((', '(').replace('))', ')')
    expr = re.sub(r'\\mathbf\b', '', expr)
    expr = expr.replace('{', '').replace('}', '')
    
    return expr.strip()

html_content = []
html_content.append("""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>CS353 Lab 12 QoS Written Report</title>
<style>
  @page {
    size: A4;
    margin: 14mm 15mm 14mm 15mm;
  }
  body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
    font-size: 10pt;
    line-height: 1.45;
    color: #1f2328;
    background-color: #fff;
    padding: 0;
    margin: 0;
  }
  h1 {
    font-size: 17pt;
    border-bottom: 2px solid #0969da;
    padding-bottom: 4px;
    margin: 0 0 10px 0;
    color: #0d1117;
  }
  h2 {
    font-size: 12.5pt;
    border-bottom: 1px solid #d0d7de;
    padding-bottom: 3px;
    margin-top: 15px;
    margin-bottom: 8px;
    color: #0969da;
    page-break-after: avoid;
  }
  h3 {
    font-size: 10.5pt;
    margin-top: 11px;
    margin-bottom: 6px;
    color: #24292f;
    page-break-after: avoid;
  }
  table {
    border-collapse: collapse;
    width: 100%;
    margin: 9px 0;
    page-break-inside: avoid;
    font-size: 9pt;
  }
  th, td {
    border: 1px solid #d0d7de;
    padding: 5px 8px;
    text-align: left;
  }
  th {
    background-color: #f6f8fa;
    font-weight: 600;
  }
  tr:nth-child(even) {
    background-color: #fafbfc;
  }
  code {
    font-family: "SFMono-Regular", Consolas, "Liberation Mono", Menlo, Courier, monospace;
    font-size: 9pt;
    background-color: #f6f8fa;
    padding: 1px 4px;
    border-radius: 3px;
    border: 1px solid #e1e4e8;
  }
  p {
    margin: 4px 0;
  }
  ul, ol {
    margin: 4px 0 8px 18px;
    padding: 0;
  }
  li {
    margin-bottom: 3px;
  }
  hr {
    border: 0;
    height: 1px;
    background: #d0d7de;
    margin: 14px 0;
  }
  .math-block {
    text-align: center;
    margin: 8px 0;
    font-family: "Cambria Math", "Latin Modern Math", "Times New Roman", serif;
    font-size: 11pt;
    background-color: #f6f8fa;
    padding: 5px;
    border-radius: 4px;
    border: 1px solid #eaecef;
    page-break-inside: avoid;
  }
  sub, sup {
    font-size: 75%;
    line-height: 0;
    position: relative;
    vertical-align: baseline;
  }
  sub {
    bottom: -0.25em;
  }
  sup {
    top: -0.5em;
  }
</style>
</head>
<body>
""")

in_table = False

def format_inline(text):
    text = re.sub(r'\$\$(.*?)\$\$', lambda m: f'<div class="math-block">{clean_math(m.group(1))}</div>', text)
    text = re.sub(r'\$(.*?)\$', lambda m: f'<i>{clean_math(m.group(1))}</i>', text)
    text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', text)
    text = re.sub(r'`(.*?)`', r'<code>\1</code>', text)
    return text

i = 0
while i < len(lines):
    line = lines[i].rstrip('\r\n')
    
    if line.startswith("# "):
        if in_table:
            html_content.append("</tbody></table>")
            in_table = False
        html_content.append(f"<h1>{format_inline(line[2:])}</h1>")
    elif line.startswith("## "):
        if in_table:
            html_content.append("</tbody></table>")
            in_table = False
        html_content.append(f"<h2>{format_inline(line[3:])}</h2>")
    elif line.startswith("### "):
        if in_table:
            html_content.append("</tbody></table>")
            in_table = False
        html_content.append(f"<h3>{format_inline(line[4:])}</h3>")
    elif line.startswith("---"):
        if in_table:
            html_content.append("</tbody></table>")
            in_table = False
        html_content.append("<hr>")
    elif line.startswith("|"):
        cells = [c.strip() for c in line.split("|")[1:-1]]
        if not in_table:
            in_table = True
            html_content.append("<table>")
            html_content.append("<thead><tr>")
            for c in cells:
                html_content.append(f"<th>{format_inline(c)}</th>")
            html_content.append("</tr></thead><tbody>")
        elif all(set(c).issubset({'-', ':', ' '}) for c in cells):
            pass
        else:
            html_content.append("<tr>")
            for c in cells:
                html_content.append(f"<td>{format_inline(c)}</td>")
            html_content.append("</tr>")
    elif line.startswith("$$"):
        if in_table:
            html_content.append("</tbody></table>")
            in_table = False
        math_lines = [line]
        if not line.endswith("$$") or line == "$$":
            i += 1
            while i < len(lines) and not lines[i].strip().endswith("$$"):
                math_lines.append(lines[i].strip())
                i += 1
            if i < len(lines):
                math_lines.append(lines[i].strip())
        full_math = " ".join(math_lines).replace("$$", "").strip()
        html_content.append(f'<div class="math-block">{clean_math(full_math)}</div>')
    elif line.strip() == "":
        if in_table:
            html_content.append("</tbody></table>")
            in_table = False
    elif line.startswith("- ") or line.startswith("* "):
        if in_table:
            html_content.append("</tbody></table>")
            in_table = False
        html_content.append(f"<li>{format_inline(line[2:])}</li>")
    elif re.match(r'^\d+\.\s', line):
        if in_table:
            html_content.append("</tbody></table>")
            in_table = False
        content = re.sub(r'^\d+\.\s', '', line)
        html_content.append(f"<p style='margin: 3px 0;'><b>{line.split('.')[0]}.</b> {format_inline(content)}</p>")
    else:
        if in_table:
            html_content.append("</tbody></table>")
            in_table = False
        html_content.append(f"<p style='margin: 4px 0;'>{format_inline(line)}</p>")
    i += 1

if in_table:
    html_content.append("</tbody></table>")

html_content.append("""
</body>
</html>
""")

with open(html_path, "w", encoding="utf-8") as f:
    f.write("\n".join(html_content))

print(f"HTML regenerated with fixed math formulas at {html_path}")
