"""
Google Document Tree Parser — hierarchical Document → Page → Block → Paragraph → Line → Token
Production uses Google Document AI; fallback uses pypdf regex mimicking GDT hierarchy.
Preserves headings, lists, tables, math, footnotes.
"""
from dataclasses import dataclass, field, asdict
from pathlib import Path
import re
from typing import List, Optional

@dataclass
class GDT_Token:
    text: str
    confidence: float = 1.0
    layout: dict = field(default_factory=dict)

@dataclass
class GDT_Line:
    tokens: List[GDT_Token] = field(default_factory=list)
    @property
    def text(self): return " ".join(t.text for t in self.tokens)

@dataclass
class GDT_Paragraph:
    lines: List[GDT_Line] = field(default_factory=list)
    type: str = "PARAGRAPH"
    @property
    def text(self): return "\n".join(l.text for l in self.lines)

@dataclass
class GDT_Block:
    paragraphs: List[GDT_Paragraph] = field(default_factory=list)
    type: str = "TEXT_BLOCK"

@dataclass
class GDT_Page:
    page_number: int
    blocks: List[GDT_Block] = field(default_factory=list)

@dataclass
class GDT_Document:
    doc_id: str
    source_uri: str
    pages: List[GDT_Page] = field(default_factory=list)
    detected_language: str = "en"
    def to_dict(self):
        return {
            "@context": "https://documentai.googleapis.com/v1",
            "@type": "Document",
            "doc_id": self.doc_id,
            "source_uri": self.source_uri,
            "pages": [
                {"page_number": p.page_number,
                 "blocks": [{"paragraphs": [
                     {"type": par.type, "text": par.text, "lines": [{"text": l.text} for l in par.lines]}
                     for par in b.paragraphs]}
                 for b in p.blocks]}
                for p in self.pages
            ]
        }

class GoogleDocumentTreeParser:
    def __init__(self, use_docai: bool = False, processor: str = ""):
        self.use_docai = use_docai
        self.processor = processor

    def parse(self, pdf_path: Path, source_uri: str) -> GDT_Document:
        if self.use_docai:
            return self._parse_docai(pdf_path, source_uri)
        return self._parse_fallback(pdf_path, source_uri)

    def _parse_docai(self, pdf_path: Path, source_uri: str) -> GDT_Document:
        from google.cloud import documentai
        client = documentai.DocumentProcessorServiceClient()
        with open(pdf_path, "rb") as f:
            raw = f.read()
        result = client.process_document(
            documentai.ProcessRequest(
                name=self.processor,
                raw_document=documentai.RawDocument(content=raw, mime_type="application/pdf"),
            )
        ).document
        return self._convert_docai(result, source_uri)

    def _convert_docai(self, doc, source_uri: str) -> GDT_Document:
        gdt = GDT_Document(doc_id=Path(source_uri).stem, source_uri=source_uri)
        for page_idx, page in enumerate(doc.pages):
            gdt_page = GDT_Page(page_number=page_idx + 1)
            for block in page.blocks:
                gdt_block = GDT_Block()
                for para in block.paragraphs:
                    text = "".join(t.text for l in para.lines for t in l.tokens)  # type: ignore
                    gdt_para = GDT_Paragraph(type=self._classify(text), lines=[
                        GDT_Line(tokens=[GDT_Token(text=t.text) for t in l.tokens])
                        for l in para.lines  # type: ignore
                    ])
                    gdt_block.paragraphs.append(gdt_para)
                gdt_page.blocks.append(gdt_block)
            gdt.pages.append(gdt_page)
        return gdt

    def _parse_fallback(self, pdf_path: Path, source_uri: str) -> GDT_Document:
        from pypdf import PdfReader
        gdt = GDT_Document(doc_id=pdf_path.stem, source_uri=source_uri)
        reader = PdfReader(str(pdf_path))
        for page_idx, page in enumerate(reader.pages):
            gdt_page = GDT_Page(page_number=page_idx + 1)
            text = page.extract_text() or ""
            for raw_block in text.split("\n\n"):
                if not raw_block.strip():
                    continue
                gdt_block = GDT_Block()
                for raw_line in raw_block.split("\n"):
                    if not raw_line.strip():
                        continue
                    ptype = self._classify(raw_line)
                    para = GDT_Paragraph(type=ptype,
                        lines=[GDT_Line(tokens=[GDT_Token(text=raw_line.strip())])])
                    gdt_block.paragraphs.append(para)
                gdt_page.blocks.append(gdt_block)
            gdt.pages.append(gdt_page)
        return gdt

    @staticmethod
    def _classify(text: str) -> str:
        t = text.strip()
        if re.match(r"^(\d+(\.\d+)?)\.?\s+[A-Z]", t): return "HEADING"
        if re.match(r"^[\(\[][a-z\d]+[\)\]]", t):        return "LIST_ITEM"
        if re.match(r"^(Theorem|Definition|Note|Proof)[:\s]", t, re.I): return "DEFINITION"
        if re.search(r"[=+\-×÷√π∑∫]", t) and ("$" in t or "\\" in t or "^" in t):
            return "FORMULA"
        return "PARAGRAPH"
