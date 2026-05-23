"""
main.py
Streamlit app entry point for Receipt OCR App.

Run with:
    streamlit run app/main.py
"""

import sys
import os

# Ensure app/ directory is in path so relative imports work
sys.path.insert(0, os.path.dirname(__file__))

import streamlit as st
from PIL import Image
import pandas as pd
import io

# from app.preprocess import preprocess, to_pil, to_bytes
# from app.ocr import get_vision_client, run_ocr, run_ocr_mock, save_raw_json
# from app.parser import parse_receipt
# from app.database import init_db, save_receipt, get_all_receipts, get_receipt_by_id, get_summary_stats
# from app.utils import (
#     save_uploaded_file, save_raw_ocr_json,
#     receipt_to_dataframe, receipts_to_dataframe, export_to_excel,
#     format_rupiah, truncate_text, is_valid_image
# )

from preprocess import preprocess, to_pil, to_bytes
from ocr import get_vision_client, run_ocr, run_ocr_mock, save_raw_json
from parser import parse_receipt
from database import init_db, save_receipt, get_all_receipts, get_receipt_by_id, get_summary_stats
from utils import (
    save_uploaded_file, save_raw_ocr_json,
    receipt_to_dataframe, receipts_to_dataframe, export_to_excel,
    format_rupiah, truncate_text, is_valid_image
)

# ── Page config ───────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="Receipt OCR",
    page_icon="🧾",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ── Session state defaults ────────────────────────────────────────────────────

def init_session():
    defaults = {
        "mock_mode": False,
        "credentials_path": "credentials/google_credentials.json",
        "ocr_result": None,
        "parsed_receipt": None,
        "current_receipt_id": None,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


init_session()
init_db()


# ── Sidebar ───────────────────────────────────────────────────────────────────

with st.sidebar:
    st.title("🧾 Receipt OCR")
    st.divider()

    page = st.radio(
        "Navigation",
        ["📤 Scan Receipt", "📋 History", "📊 Stats"],
        label_visibility="collapsed",
    )

    st.divider()
    st.subheader("⚙️ Settings")

    st.session_state.mock_mode = st.toggle(
        "Mock Mode (no API key)",
        value=st.session_state.mock_mode,
        help="Use fake OCR output. Great for testing parser without Google Vision API.",
    )

    if not st.session_state.mock_mode:
        creds_path = st.text_input(
            "Credentials JSON path",
            value=st.session_state.credentials_path,
            help="Path to your Google service account JSON file.",
        )
        st.session_state.credentials_path = creds_path

    st.divider()
    st.caption("Built with OpenCV + Google Vision + Streamlit")


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: SCAN RECEIPT
# ══════════════════════════════════════════════════════════════════════════════

if page == "📤 Scan Receipt":
    st.header("📤 Scan a Receipt")

    if st.session_state.mock_mode:
        st.info("🔧 **Mock Mode active** — using fake OCR data. Toggle off in sidebar to use real Vision API.")

    uploaded_file = st.file_uploader(
        "Upload a receipt image",
        type=["jpg", "jpeg", "png", "webp", "bmp"],
        help="Clear, well-lit photos work best.",
    )

    if uploaded_file:
        image_bytes = uploaded_file.read()

        st.subheader("1️⃣ Image Preview")
        col_orig, col_proc = st.columns(2)

        with st.spinner("Preprocessing image..."):
            try:
                original_cv, processed_cv = preprocess(image_bytes, source="bytes")
                original_pil = to_pil(original_cv)
                processed_pil = to_pil(processed_cv)
            except Exception as e:
                st.error(f"Preprocessing failed: {e}")
                st.stop()

        with col_orig:
            st.image(original_pil, caption="Original", use_container_width=True)
        with col_proc:
            st.image(processed_pil, caption="Preprocessed (sent to OCR)", use_container_width=True)

        # ── OCR ───────────────────────────────────────────────────────────────
        st.subheader("2️⃣ OCR")

        run_btn = st.button("🔍 Run OCR", type="primary", use_container_width=True)

        if run_btn:
            with st.spinner("Running OCR..."):
                try:
                    if st.session_state.mock_mode:
                        ocr_result = run_ocr_mock()
                    else:
                        client = get_vision_client(st.session_state.credentials_path)
                        processed_bytes = to_bytes(processed_cv)
                        ocr_result = run_ocr(processed_bytes, client)

                    st.session_state.ocr_result = ocr_result

                    # Save files
                    image_path = save_uploaded_file(image_bytes)
                    json_path = save_raw_ocr_json(ocr_result, image_path)

                    # Parse
                    parsed = parse_receipt(ocr_result["full_text"])
                    st.session_state.parsed_receipt = parsed

                    # Save to DB
                    receipt_id = save_receipt(
                        parsed,
                        image_path=image_path,
                        raw_json_path=json_path,
                    )
                    st.session_state.current_receipt_id = receipt_id

                    st.success(f"✅ OCR complete! Saved as Receipt #{receipt_id}")

                except FileNotFoundError as e:
                    st.error(f"Credentials error: {e}")
                except Exception as e:
                    st.error(f"OCR failed: {e}")
                    st.exception(e)

        # ── Results ───────────────────────────────────────────────────────────
        if st.session_state.ocr_result and st.session_state.parsed_receipt:
            ocr_result = st.session_state.ocr_result
            parsed = st.session_state.parsed_receipt

            st.subheader("3️⃣ Raw OCR Text")
            with st.expander("Show raw OCR output", expanded=False):
                st.code(ocr_result["full_text"], language=None)

            st.subheader("4️⃣ Parsed Receipt")

            # Receipt header
            meta_col1, meta_col2, meta_col3 = st.columns(3)
            meta_col1.metric("🏪 Store", parsed.store_name or "—")
            meta_col2.metric("📅 Date", parsed.date or "—")
            meta_col3.metric("💳 Total", format_rupiah(parsed.total) if parsed.total else "—")

            if parsed.discount:
                st.caption(f"Discount: {format_rupiah(parsed.discount)}")

            # Warnings
            if parsed.parse_warnings:
                for w in parsed.parse_warnings:
                    st.warning(f"⚠️ {w}")

            # Items table
            if parsed.items:
                df = receipt_to_dataframe(
                    {"items": [vars(i) for i in parsed.items]}
                )
                st.dataframe(df, use_container_width=True, hide_index=True)

                # Export
                export_path = "data/export.xlsx"
                export_to_excel(df, export_path)
                with open(export_path, "rb") as f:
                    st.download_button(
                        "⬇️ Download as Excel",
                        data=f.read(),
                        file_name="receipt_items.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    )
            else:
                st.info("No items were parsed. Try adjusting the image or reviewing raw OCR text above.")


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: HISTORY
# ══════════════════════════════════════════════════════════════════════════════

elif page == "📋 History":
    st.header("📋 Scan History")

    receipts = get_all_receipts()

    if not receipts:
        st.info("No receipts scanned yet. Go to **Scan Receipt** to get started.")
    else:
        # Summary row
        cols = st.columns(3)
        cols[0].metric("Total Receipts", len(receipts))
        cols[1].metric("Total Spend", format_rupiah(sum(r["total"] for r in receipts)))
        cols[2].metric("Total Items", sum(r["item_count"] for r in receipts))

        st.divider()

        for r in receipts:
            with st.expander(
                f"#{r['id']} — {r['store_name']} | {r['receipt_date'] or 'unknown date'} | {format_rupiah(r['total'])}",
                expanded=False,
            ):
                receipt_detail = get_receipt_by_id(r["id"])
                if receipt_detail and receipt_detail.get("items"):
                    df = receipt_to_dataframe(receipt_detail)
                    st.dataframe(df, use_container_width=True, hide_index=True)

                    if receipt_detail["warnings"]:
                        for w in receipt_detail["warnings"]:
                            st.caption(f"⚠️ {w}")
                else:
                    st.caption("No items found for this receipt.")


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: STATS
# ══════════════════════════════════════════════════════════════════════════════

elif page == "📊 Stats":
    st.header("📊 Statistics")

    stats = get_summary_stats()

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("🧾 Receipts Scanned", stats["total_receipts"])
    col2.metric("🛒 Items Parsed", stats["total_items"])
    col3.metric("💰 Total Spend", format_rupiah(stats["total_spend"]))
    col4.metric("🏪 Top Store", stats["top_store"])

    st.divider()

    # All items as searchable table
    receipts = get_all_receipts()
    if receipts:
        all_data = []
        for r in receipts:
            detail = get_receipt_by_id(r["id"])
            if detail:
                all_data.append(detail)

        df = receipts_to_dataframe(all_data)

        if not df.empty:
            st.subheader("All Items")
            search = st.text_input("🔎 Search item name", "")
            if search:
                df = df[df["Item"].str.upper().str.contains(search.upper(), na=False)]

            st.dataframe(df, use_container_width=True, hide_index=True)

            if not df.empty:
                export_path = "data/all_items_export.xlsx"
                export_to_excel(df, export_path)
                with open(export_path, "rb") as f:
                    st.download_button(
                        "⬇️ Export All to Excel",
                        data=f.read(),
                        file_name="all_receipt_items.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    )
    else:
        st.info("No data yet.")
