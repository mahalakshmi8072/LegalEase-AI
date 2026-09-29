uvicorn backend.main:app --reload --port 8000from backend.services.document_formatter import format_docx, format_html_preview, format_pdf, sanitize_text

def test_sanitize_text():
    assert sanitize_text("Hello — “world”") == 'Hello - "world"'

def test_html_preview_escapes_html():
    output = format_html_preview("<script>alert(1)</script>")
    assert "<script>" not in output
    assert "&lt;script&gt;" in output

def test_docx_and_pdf_generate():
    text = "DRAFT AGREEMENT\n\n1. Payment within 30 days."
    docx = format_docx(text, "Agreement")
    pdf = format_pdf(text, "Agreement")
    assert docx[:2] == b"PK"
    assert pdf.startswith(b"%PDF")
