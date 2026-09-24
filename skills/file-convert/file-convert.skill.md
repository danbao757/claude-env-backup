---
name: file-convert
description: Convert PDF files to DOC/DOCX and vice versa
trigger: /file-convert
author: claude-code
version: 1.0.0
---

# 文件格式转换工具

这个 skill 用于将 PDF 文件转换为 DOC/DOCX 格式，以及将 DOC/DOCX 文件转换为 PDF 格式。

## 触发命令

`/file-convert`

## 支持的转换方向

- PDF → DOCX
- PDF → DOC
- DOCX → PDF
- DOC → PDF

## 使用方法

使用 slash command 后，告诉 Claude 你要执行什么转换，例如：
- "将 current_folder 中的 report.pdf 转换为 docx"
- "将 documents 文件夹里的所有 docx 文件转换为 pdf"
- "将 ./合同.doc 转换为 pdf"

## 技术实现

使用 Python 库实现：
- **PDF → DOCX/DOC**: PyMuPDF (提取文本) + python-docx (创建文档)
- **DOCX/DOC → PDF**: docx2pdf (使用 Word 引擎)

## 依赖要求

已安装的包：python-docx, pymupdf, docx2pdf

## 转换函数

### PDF 转 DOCX
```python
import os
from docx import Document
import fitz

def pdf_to_docx(pdf_path, docx_path=None):
    if docx_path is None:
        docx_path = os.path.splitext(pdf_path)[0] + '.docx'

    doc = fitz.open(pdf_path)
    docx_doc = Document()
    docx_doc.add_heading(os.path.basename(pdf_path), 0)

    for page in doc:
        text = page.get_text()
        if text.strip():
            docx_doc.add_paragraph(text)

    doc.close()
    docx_doc.save(docx_path)
    return docx_path
```

### PDF 转 DOC
```python
def pdf_to_doc(pdf_path, doc_path=None):
    if doc_path is None:
        doc_path = os.path.splitext(pdf_path)[0] + '.doc'

    docx_path = pdf_to_docx(pdf_path)
    # 重命名为 .doc
    import shutil
    shutil.move(docx_path, doc_path)
    return doc_path
```

### DOCX/DOC 转 PDF
```python
from docx2pdf import convert

def docx_to_pdf(docx_path, pdf_path=None):
    if pdf_path is None:
        pdf_path = os.path.splitext(docx_path)[0] + '.pdf'

    convert(docx_path, pdf_path)
    return pdf_path

def doc_to_pdf(doc_path, pdf_path=None):
    if pdf_path is None:
        pdf_path = os.path.splitext(doc_path)[0] + '.pdf'

    convert(doc_path, pdf_path)
    return pdf_path
```

### 批量转换
```python
import glob

def batch_convert(pattern, output_ext):
    """批量转换文件

    Args:
        pattern: 文件匹配模式，如 "*.pdf" 或 "./docs/*.docx"
        output_ext: 目标扩展名，如 ".docx" 或 ".pdf"
    """
    files = glob.glob(pattern)
    results = []

    for file in files:
        try:
            if output_ext in ['.docx', '.doc']:
                result = pdf_to_docx(file) if file.lower().endswith('.pdf') else docx_to_pdf(file)
            else:
                result = docx_to_pdf(file) if file.lower().endswith(('.docx', '.doc')) else pdf_to_docx(file)
            results.append((file, result, 'success'))
        except Exception as e:
            results.append((file, None, str(e)))

    return results
```

## 执行流程

1. 解析用户请求，提取源文件路径和目标格式
2. 验证源文件存在
3. 执行转换
4. 返回转换结果（成功/失败）
5. 告知用户输出文件位置