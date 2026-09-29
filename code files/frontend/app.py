import os
from datetime import date
from pathlib import Path
import sys
import requests
import streamlit as st
from dotenv import load_dotenv

ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT_DIR))
load_dotenv()
BACKEND_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8001").rstrip("/")
ASSETS_DIR = Path(__file__).resolve().parents[1] / "assets"

st.set_page_config(page_title="LegalEase", page_icon="⚖️", layout="wide")
st.markdown("""
<style>
.block-container {max-width: 1150px; padding-top: 2rem;}
.hero {padding: 1.2rem 1.4rem; border-radius: 14px; background: #111827; color: white;}
.legal-preview {background: #0f172a; color: #e5e7eb; padding: 1.3rem; border-radius: 12px;
max-height: 650px; overflow-y: auto; font-family: Georgia, serif; line-height: 1.65;}
.notice {font-size: .85rem; color: #6b7280;}
</style>
""", unsafe_allow_html=True)


st.markdown(
    """
    <div style="
        text-align: center;
        width: 100%;
        margin: 10px 0 25px 0;
        white-space: nowrap;
    ">
        <span style="
            font-size: 30px;
            font-weight: 800;
        ">⚖ LegalEase</span>
    </div>
    """,
    unsafe_allow_html=True
)
st.caption("Create an editable draft from your facts and terms. LegalEase does not replace advice from a qualified lawyer.")

if "document" not in st.session_state: st.session_state.document = ""
if "editing" not in st.session_state: st.session_state.editing = False

with st.form("document_form"):
    col1, col2 = st.columns(2)
    with col1:
        document_type = st.selectbox("Document type", [
            "Employment Contract", "Non-Disclosure Agreement", "Lease Agreement",
            "Freelance Work Contract", "Service Agreement", "General Agreement", "Custom Legal Document"
        ])
        parties = st.text_area("Parties involved", placeholder="Jane Doe (Service Provider); TechNova Inc. (Client)", height=120)
    with col2:
        effective_date = st.date_input("Effective date", value=date.today())
        terms = st.text_area("Terms & conditions", placeholder="Payment within 30 days; confidentiality must be maintained; either party may terminate with 15 days notice", height=120)
    submitted = st.form_submit_button("Generate Document", type="primary", use_container_width=True)

if submitted:
    if not parties.strip() or not terms.strip():
        st.error("Please enter parties and terms.")
    else:
        try:
            with st.spinner("Generating your draft..."):
                response = requests.post(f"{BACKEND_URL}/generate", json={
                    "document_type": document_type, "parties": parties, "terms": terms,
                    "effective_date": effective_date.isoformat()
                }, timeout=120)
            if response.ok:
                st.session_state.document = response.json()["document_text"]
                st.session_state.editing = False
                st.success("Document generated.")
            else:
                try: detail = response.json().get("detail", response.text)
                except Exception: detail = response.text
                st.error(f"Backend error ({response.status_code}): {detail}")
        except requests.RequestException as exc:
            st.error(f"Could not connect to FastAPI at {BACKEND_URL}. Start the backend first. Details: {exc}")

if st.session_state.document:
    st.divider(); st.subheader("Document Preview")
    if st.button("Click to Edit Document"):
        st.session_state.editing = not st.session_state.editing

    from backend.services.document_formatter import format_html_preview, format_docx, format_pdf, sanitize_text
    if st.session_state.editing:
        st.session_state.document = st.text_area("Editable document", value=st.session_state.document, height=620)
    else:
        st.markdown(format_html_preview(st.session_state.document), unsafe_allow_html=True)

    clean_text = sanitize_text(st.session_state.document)
    docx_bytes = format_docx(clean_text, document_type)
    pdf_bytes = format_pdf(clean_text, document_type)

    st.subheader("Download")
    c1, c2, c3 = st.columns(3)
    with c1:
        st.download_button("Download TXT", clean_text.encode("utf-8"), "legalease_document.txt", "text/plain", use_container_width=True)
    with c2:
        st.download_button("Download DOCX", docx_bytes, "legalease_document.docx", "application/vnd.openxmlformats-officedocument.wordprocessingml.document", use_container_width=True)
    with c3:
        st.download_button("Download PDF", pdf_bytes, "legalease_document.pdf", "application/pdf", use_container_width=True)

    st.markdown('<p class="notice">Important: AI-generated legal drafts may contain errors or omissions. Review material documents with a qualified lawyer before use.</p>', unsafe_allow_html=True)
