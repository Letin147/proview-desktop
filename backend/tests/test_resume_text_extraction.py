import unittest
from pathlib import Path
import sys
import uuid
import zipfile
from unittest.mock import patch

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))
TEST_FILES_ROOT = BACKEND_ROOT / "tests"

from services import resume_text_extraction as extraction_service
from services.resume_text_extraction import (
    ResumeExtractionError,
    ResumeOcrUnavailableError,
    UnsupportedResumeFormatError,
    ensure_supported_resume_extension,
    extract_resume_content,
    unwrap_resume_text,
)


class ResumeTextExtractionTests(unittest.TestCase):
    def _write_minimal_docx(self, docx_path: Path) -> None:
        content_types = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="xml" ContentType="application/xml"/>
  <Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
</Types>"""
        rels = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>
</Relationships>"""
        document_xml = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:body>
    <w:p><w:r><w:t>李四</w:t></w:r></w:p>
    <w:tbl>
      <w:tr>
        <w:tc><w:p><w:r><w:t>技能</w:t></w:r></w:p></w:tc>
        <w:tc><w:p><w:r><w:t>Go</w:t></w:r></w:p></w:tc>
      </w:tr>
    </w:tbl>
  </w:body>
</w:document>"""

        with zipfile.ZipFile(docx_path, "w") as archive:
            archive.writestr("[Content_Types].xml", content_types)
            archive.writestr("_rels/.rels", rels)
            archive.writestr("word/document.xml", document_xml)

    def _write_header_only_docx(self, docx_path: Path) -> None:
        document_xml = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:body>
    <w:p/>
  </w:body>
</w:document>"""
        header_xml = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:hdr xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:p><w:r><w:t>王五</w:t></w:r></w:p>
  <w:p><w:r><w:t>Python 工程师</w:t></w:r></w:p>
</w:hdr>"""

        with zipfile.ZipFile(docx_path, "w") as archive:
            archive.writestr("word/document.xml", document_xml)
            archive.writestr("word/header1.xml", header_xml)

    def test_markdown_is_extracted_without_ocr(self):
        md_path = TEST_FILES_ROOT / f"__resume_text_test_{uuid.uuid4().hex}.md"
        try:
            md_path.write_text("# 张三\n\n- Python\n- Vue\n\n[作品集](https://example.com)\n", encoding="utf-8")

            result = extract_resume_content(
                str(md_path),
                include_images=False,
                ocr_available=False,
            )

            self.assertTrue(result["success"])
            self.assertEqual(result["mode"], "direct_text")
            self.assertIn("张三", result["text"])
            self.assertIn("- Python", result["text"])
            self.assertIn("作品集", result["text"])
            self.assertNotIn("https://example.com", result["text"])
            self.assertIn("无需 OCR", result["reusable_text"])
        finally:
            md_path.unlink(missing_ok=True)

    def test_docx_is_extracted_without_python_docx(self):
        docx_path = TEST_FILES_ROOT / f"__resume_text_test_{uuid.uuid4().hex}.docx"
        try:
            self._write_minimal_docx(docx_path)

            with patch.object(extraction_service, "Document", None):
                result = extract_resume_content(
                    str(docx_path),
                    include_images=False,
                    ocr_available=False,
                )

            self.assertTrue(result["success"])
            self.assertEqual(result["mode"], "direct_text")
            self.assertIn("李四", result["text"])
            self.assertIn("技能 | Go", result["text"])
        finally:
            docx_path.unlink(missing_ok=True)

    def test_docx_falls_back_to_zip_parts_when_python_docx_returns_empty(self):
        docx_path = TEST_FILES_ROOT / f"__resume_text_test_{uuid.uuid4().hex}.docx"
        try:
            self._write_header_only_docx(docx_path)

            class EmptyDocument:
                paragraphs = []
                tables = []

            with patch.object(extraction_service, "Document", lambda _path: EmptyDocument()):
                result = extract_resume_content(
                    str(docx_path),
                    include_images=False,
                    ocr_available=False,
                )

            self.assertTrue(result["success"])
            self.assertEqual(result["mode"], "direct_text")
            self.assertIn("王五", result["text"])
            self.assertIn("Python 工程师", result["text"])
        finally:
            docx_path.unlink(missing_ok=True)

    def test_invalid_docx_is_reported_as_resume_extraction_error(self):
        docx_path = TEST_FILES_ROOT / f"__resume_text_test_{uuid.uuid4().hex}.docx"
        try:
            docx_path.write_text("this is not a real docx archive", encoding="utf-8")

            with self.assertRaisesRegex(ResumeExtractionError, "不是有效的 .docx 文件"):
                extract_resume_content(
                    str(docx_path),
                    include_images=False,
                    ocr_available=False,
                )
        finally:
            docx_path.unlink(missing_ok=True)

    def test_legacy_doc_is_rejected_before_parsing(self):
        with self.assertRaisesRegex(UnsupportedResumeFormatError, "暂不支持旧版 .doc"):
            ensure_supported_resume_extension("legacy_resume.doc")

    def test_unwrap_resume_text_removes_wrapper(self):
        wrapped_text = (
            "【解析成功】已直接提取 Markdown 文档 内容（无需 OCR）\n\n"
            "以下是提取的内容:\n\n"
            "# 张三\n\n"
            "- React\n\n"
            "[博客](https://example.com)"
        )

        clean_text = unwrap_resume_text(wrapped_text, ext=".md")

        self.assertIn("张三", clean_text)
        self.assertIn("- React", clean_text)
        self.assertNotIn("以下是提取的内容", clean_text)
        self.assertNotIn("https://example.com", clean_text)

    def test_pdf_requires_ocr(self):
        pdf_path = TEST_FILES_ROOT / f"__resume_text_test_{uuid.uuid4().hex}.pdf"
        try:
            pdf_path.write_bytes(b"%PDF-1.4")

            with self.assertRaises(ResumeOcrUnavailableError):
                extract_resume_content(
                    str(pdf_path),
                    include_images=False,
                    ocr_available=False,
                )
        finally:
            pdf_path.unlink(missing_ok=True)


if __name__ == "__main__":
    unittest.main()
