---
name: pdf-doc-convert
description: Convert PDF files to DOC/DOCX and vice versa
trigger: /pdf-convert
author: claude-code
version: 1.0.0
---

# PDF/DOC 文件转换工具

这个 skill 用于将 PDF 文件转换为 DOC/DOCX 格式，以及将 DOC/DOCX 文件转换为 PDF 格式。

## 触发命令

`/pdf-convert`

## 支持的转换方向

- PDF → DOCX
- PDF → DOC
- DOCX → PDF
- DOC → PDF
1.
2.
3.
4.


## 使用方法

告诉 Claude 你要执行什么转换，例如：
- "将 current_folder 中的 report.pdf 转换为 docx"
- "将 documents 文件夹里的所有 docx 文件转换为 pdf"

## 技术实现

使用 Python 库实现：
- **PDF → DOCX**: PyMuPDF (提取文本) + python-docx (创建文档)
- **DOCX → PDF**: docx2pdf (使用 Word 引擎)

## 依赖要求

```bash
pip install python-docx pymupdf docx2pdf
```

## 示例代码

```python
import os
from docx import Document
import fitz  # PyMuPDF

def pdf_to_docx(pdf_path, docx_path):
    """Convert PDF to DOCX"""
    doc = fitz.open(pdf_path)
    docx_doc = Document()
    docx_doc.add_heading(os.path.basename(pdf_path), 0)

    for page in doc:
        text = page.get_text()
        if text.strip():
            docx_doc.add_paragraph(text)

    doc.close()
    docx_doc.save(docx_path)
    return True

def docx_to_pdf(docx_path, pdf_path):
    """Convert DOCX to PDF"""
    from docx2pdf import convert
    convert(docx_path, pdf_path)
    return True
```






