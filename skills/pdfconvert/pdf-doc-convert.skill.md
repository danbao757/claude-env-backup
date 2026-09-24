---
name: pdf-doc-convert
description: Convert PDF files to DOC/DOCX and vice versa
trigger: /pdf-convert
author: claude-code
version: 1.0.0
---

# PDF/DOC 文件转换工具

## 触发命令

`/pdf-convert`

## 支持的转换方向

- PDF → DOCX
- PDF → DOC
- DOCX → PDF
- DOC → PDF

## 使用方法

用户说 `/pdf-convert` 后，等待用户提供：
1. 源文件路径（完整路径或文件名）
2. 目标格式（DOC 或 DOCX）

## 执行步骤

当用户提供文件路径后，执行以下操作：

### PDF → DOC/DOCX 转换

1. 检查文件是否存在
2. 使用 PyMuPDF 读取 PDF 内容
3. 使用 python-docx 创建 DOCX 文档
4. 保存到目标路径

### DOC/DOCX → PDF 转换

1. 检查文件是否存在
2. 使用 docx2pdf 转换
3. 保存到目标路径

## 依赖检查

如果依赖未安装，执行：
```bash
pip install python-docx pymupdf docx2pdf
```

## 错误处理

- 文件不存在：提示用户检查路径
- 转换失败：报告具体错误信息
- 缺少依赖：自动安装或提示用户安装

## 示例对话

```
用户: /pdf-convert
助手: 请提供要转换的文件路径和目标格式（DOC 或 DOCX）。
用户: C:\Users\Desktop\report.pdf，转换为 docx
助手: (执行转换)
```

## 技术细节

```python
# PDF → DOCX
import fitz
from docx import Document

def pdf_to_docx(pdf_path, docx_path):
    doc = fitz.open(pdf_path)
    docx_doc = Document()
    docx_doc.add_heading(os.path.basename(pdf_path).replace('.pdf', ''), 0)
    for page in doc:
        text = page.get_text()
        if text.strip():
            docx_doc.add_paragraph(text)
    doc.close()
    docx_doc.save(docx_path)
```

## 输出确认

转换完成后：
- 确认文件已创建
- 报告文件大小
- 询问用户是否需要调整