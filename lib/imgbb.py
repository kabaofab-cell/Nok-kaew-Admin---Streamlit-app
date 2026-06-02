"""ImgBB image upload helper."""

import base64
import requests
import streamlit as st


def upload_to_imgbb(file_bytes: bytes) -> str:
    """Upload image bytes to ImgBB and return the direct image URL."""
    api_key = st.secrets.get("imgbb_api_key", "")
    if not api_key:
        raise ValueError("ไม่พบ imgbb_api_key ใน Streamlit secrets")

    encoded = base64.b64encode(file_bytes).decode("utf-8")
    resp = requests.post(
        "https://api.imgbb.com/1/upload",
        data={"key": api_key, "image": encoded},
        timeout=30,
    )
    resp.raise_for_status()
    result = resp.json()
    if result.get("success"):
        return result["data"]["url"]
    msg = result.get("error", {}).get("message", "Unknown error")
    raise ValueError(f"ImgBB upload failed: {msg}")
