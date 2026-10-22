import os
import re
import subprocess
from markdown_it import MarkdownIt

def format_math(text: str) -> str:
    # Convert display math $$...$$
    def replace_display(match):
        content = match.group(1).strip()
        content = re.sub(r'\\text\{([^}]*)\}', r'\1', content)
        content = content.replace(r"|E_{tree}|", "|<i>E</i><sub>tree</sub>|")
        content = content.replace(r"|E_{\text{tree}}|", "|<i>E</i><sub>tree</sub>|")
        content = content.replace(r"\to", "→")
        content = content.replace(r"\dots", "…")
        return f'<div class="math-display">{content}</div>'

    text = re.sub(r'\$\$(.*?)\$\$', replace_display, text, flags=re.DOTALL)

    # Convert inline math $...$
    def replace_inline(match):
        content = match.group(1).strip()
        content = content.replace(r"\to", "→")
        content = content.replace(r"\neq", "≠")
        content = content.replace(r"\dots", "…")
        content = content.replace(r"\implies", "⟹")
        return f'<span class="math-inline">{content}</span>'

    text = re.sub(r'\$(.*?)\$', replace_inline, text)
    return text

def build_pdf():
    with open('Part_D_Answers.md', 'r', encoding='utf-8') as f:
        md_text = f.read()

    # Pre-process math
    clean_md = format_math(md_text)

    md = MarkdownIt().enable('table')
    html_content = md.render(clean_md)

    diagram_html = '''
    <div style="page-break-inside: avoid; text-align: center; margin: 20px 0 25px 0;">
        <h3 style="color: #1e3a8a; margin-bottom: 8px; font-size: 13.5px;">Network Topology, Sink Trees, and Rerouting Visualization</h3>
        <img src="topology_and_sink_trees.png" style="max-width: 100%; border: 1px solid #cbd5e1; border-radius: 6px;" />
        <p style="font-size: 10.5px; color: #64748b; margin-top: 5px;">
            Figure 1: (1) Base Undirected Topology; (2) Vector 1 Sink Tree (Sink F); (3) Vector 2 Sink Tree (Sink A); (4) Vector 3 Rerouted Sink Tree (Sink F, Link D-F=9). Green arrows denote new paths; red dashed denote broken links.
        </p>
    </div>
    '''

    # Insert diagram before Section 3
    if "<h2>3. Part D: Properties and Rerouting Analysis</h2>" in html_content:
        html_content = html_content.replace(
            "<h2>3. Part D: Properties and Rerouting Analysis</h2>",
            diagram_html + "<h2>3. Part D: Properties and Rerouting Analysis</h2>"
        )
    else:
        html_content += diagram_html

    html_template = """<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>Lab 8: Computing the Sink Tree with Dijkstra's Algorithm</title>
<style>
@page {
    size: A4;
    margin: 14mm 16mm 14mm 16mm;
}
body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    line-height: 1.48;
    color: #1e293b;
    font-size: 12.5px;
    margin: 0;
    padding: 0;
}
h1 {
    font-size: 18.5px;
    color: #0f172a;
    border-bottom: 2px solid #3b82f6;
    padding-bottom: 5px;
    margin-top: 0;
    margin-bottom: 8px;
}
h2 {
    font-size: 14.5px;
    color: #1e3a8a;
    border-bottom: 1px solid #cbd5e1;
    padding-bottom: 3px;
    margin-top: 16px;
    margin-bottom: 8px;
    page-break-after: avoid;
}
h3 {
    font-size: 13px;
    color: #0f172a;
    margin-top: 12px;
    margin-bottom: 6px;
    page-break-after: avoid;
}
h4 {
    font-size: 12.5px;
    color: #334155;
    margin-top: 10px;
    margin-bottom: 4px;
    page-break-after: avoid;
}
table {
    border-collapse: collapse;
    width: 100%;
    margin: 10px 0;
    font-size: 11.5px;
    page-break-inside: avoid;
}
th, td {
    border: 1px solid #cbd5e1;
    padding: 4.5px 9px;
    text-align: left;
}
th {
    background-color: #f1f5f9;
    font-weight: 600;
    color: #0f172a;
}
tr:nth-child(even) {
    background-color: #f8fafc;
}
blockquote {
    border-left: 4px solid #3b82f6;
    margin: 8px 0;
    padding: 6px 12px;
    background-color: #eff6ff;
    color: #1e40af;
    font-style: italic;
    page-break-inside: avoid;
}
code {
    background-color: #f1f5f9;
    padding: 2px 4px;
    border-radius: 3px;
    font-family: Consolas, "Courier New", monospace;
    font-size: 11px;
    color: #0f172a;
}
.math-display {
    text-align: center;
    margin: 8px 0;
    padding: 6px 10px;
    background-color: #f8fafc;
    border-radius: 4px;
    font-family: "Cambria Math", "Times New Roman", serif;
    font-size: 13px;
    color: #0f172a;
}
.math-inline {
    font-family: "Cambria Math", "Times New Roman", serif;
    font-style: italic;
}
hr {
    border: none;
    border-top: 1px solid #e2e8f0;
    margin: 12px 0;
}
ul, ol {
    padding-left: 18px;
    margin: 5px 0;
}
li {
    margin-bottom: 3px;
}
p {
    margin: 5px 0;
}
</style>
</head>
<body>
""" + html_content + """
</body>
</html>"""

    with open("temp_report.html", "w", encoding="utf-8") as f:
        f.write(html_template)

    chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
    edge_path = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
    browser = chrome_path if os.path.exists(chrome_path) else edge_path

    html_abs = os.path.abspath("temp_report.html")
    pdf_abs = os.path.abspath("Part_D_Answers.pdf")

    cmd = [
        browser,
        "--headless",
        "--disable-gpu",
        "--no-pdf-header-footer",
        f"--print-to-pdf={pdf_abs}",
        html_abs
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    if os.path.exists(pdf_abs) and os.path.getsize(pdf_abs) > 0:
        print(f"Successfully generated {pdf_abs} ({os.path.getsize(pdf_abs)} bytes)")
    else:
        print("PDF generation failed:", res.stderr)

    if os.path.exists("temp_report.html"):
        os.remove("temp_report.html")

if __name__ == "__main__":
    build_pdf()
