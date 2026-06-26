"""Вспомогательные построители тестовых файлов."""
import io
import zipfile

PDF_BYTES = b"%PDF-1.4\n%real pdf content"


def make_docx_bytes() -> bytes:
    """Собрать минимальный валидный DOCX (zip с word/document.xml)."""
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as z:
        z.writestr("[Content_Types].xml", "<Types/>")
        z.writestr("word/document.xml", "<w:document/>")
    return buf.getvalue()


def make_zip_without_word() -> bytes:
    """Валидный zip, но без word/document.xml — имитация .xlsx/.zip под видом .docx."""
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as z:
        z.writestr("xl/workbook.xml", "<workbook/>")
    return buf.getvalue()
