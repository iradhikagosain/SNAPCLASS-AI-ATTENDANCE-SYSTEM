import streamlit as st
import base64
from pathlib import Path

# Path to the assets folder at the project root (2 levels up from this file:
# src/components/header.py -> src -> project root -> assets)
ASSETS_DIR = Path(__file__).resolve().parents[2] / "assets"


def _load_logo_as_data_uri() -> str | None:
    """
    A local file path like 'E:\\SNAPCLASS\\logo.png' can NEVER be rendered by
    <img src="..."> in the browser -- the browser has no access to your disk.
    The fix is to read the file and embed it directly as a base64 data URI.
    """
    logo_path = ASSETS_DIR / "logo.svg"
    if not logo_path.exists():
        return None
    encoded = base64.b64encode(logo_path.read_bytes()).decode()
    return f"data:image/svg+xml;base64,{encoded}"


def header_home():
    logo_uri = _load_logo_as_data_uri()
    logo_html = (
        f'<img src="{logo_uri}" alt="SnapClass logo" style="height:90px;" />'
        if logo_uri
        else ""
    )

    st.markdown(
        f"""
        <div style="
            display:flex;
            align-items:center;
            justify-content:center;
            flex-direction:column;
            margin-top:20px;
            margin-bottom:10px;
        ">
            {logo_html}
            <h1 style="text-align:center;color:#FFFFFF;margin-top:12px;">
                SnapClass
            </h1>
            <p style="text-align:center;color:#E4E6FF;font-size:1.15rem;font-weight:500;margin-top:-2px;">
                Smart classrooms, made simple.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )
