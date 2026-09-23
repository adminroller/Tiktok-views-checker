"""
TikTok Influencer Checker - Web App (Barber Daily styled)
-----------------------------------------------------------
A shareable website version of the TikTok stats checker, styled with a
soft brown gradient hero section similar to the reference design.

HOW TO RUN LOCALLY (to test before sharing):
    pip install streamlit yt-dlp pandas
    streamlit run streamlit_app.py

HOW TO DEPLOY SO YOUR CO-WORKER CAN ACCESS IT (free):
    1. Upload this file + requirements.txt to your GitHub repo (replace
       the old streamlit_app.py).
    2. Streamlit Cloud auto-redeploys within a minute.

TO ADD YOUR OWN HERO PICTURE:
    Find the line below that says  HERO_IMAGE_URL = ""
    Paste an image link between the quotes, e.g.:
        HERO_IMAGE_URL = "https://your-image-link-here.jpg"
    (Upload your image to somewhere like imgur.com or your GitHub repo
    to get a link, then paste it there.) Leave it blank for no image.
"""

import streamlit as st
import pandas as pd
import yt_dlp

# ---- PASTE YOUR OWN IMAGE LINK HERE (optional) ----
HERO_IMAGE_URL = ""
# -----------------------------------------------------

st.set_page_config(page_title="Barber Daily TikTok Checker", layout="wide")

# ---------------- Custom brown-gradient styling ----------------
# NOTE: instead of manually opening/closing a <div> across separate
# st.markdown() calls (which breaks in Streamlit - each call renders
# independently, so a div opened in one call can't be closed in another),
# we style Streamlit's own main content container directly. This makes
# the whole page content sit inside one clean rounded "card" automatically.
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600&display=swap');

    html, body, [class*="css"]  {
        font-family: 'Poppins', sans-serif;
    }

    .stApp {
        background: radial-gradient(circle at 20% 20%, #E8CBA8 0%, #C9A579 35%, #8C5B33 100%);
    }

    /* Style Streamlit's real content container as the rounded card */
    div[data-testid="stAppViewContainer"] > div:first-child .block-container {
        background: rgba(255, 250, 244, 0.94);
        border-radius: 28px;
        padding: 48px 56px 40px 56px;
        margin: 24px auto;
        max-width: 1100px;
        box-shadow: 0 20px 60px rgba(60, 36, 18, 0.25);
    }

    .hero-nav {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 30px;
    }

    .hero-logo {
        font-size: 22px;
        font-weight: 600;
        color: #4A2C1D;
    }

    .hero-title {
        font-size: 40px;
        font-weight: 600;
        text-align: center;
        color: #3B2417;
        line-height: 1.2;
        margin-bottom: 12px;
    }

    .hero-subtitle {
        text-align: center;
        color: #6B4226;
        font-size: 16px;
        max-width: 650px;
        margin: 0 auto 28px auto;
    }

    div.stButton {
        text-align: center;
    }
    div.stButton > button {
        background-color: #6B4226;
        color: #FFF8F0;
        border-radius: 999px;
        padding: 10px 28px;
        border: none;
        font-weight: 500;
    }
    div.stButton > button:hover {
        background-color: #4A2C1D;
        color: #FFF8F0;
    }

    .result-card {
        background: #FFF8F0;
        border: 1px solid #E8D5BC;
        border-radius: 18px;
        padding: 18px 20px;
        margin-bottom: 14px;
        box-shadow: 0 4px 14px rgba(60, 36, 18, 0.08);
    }
    .result-card h4 {
        margin: 0 0 6px 0;
        color: #4A2C1D;
    }
    .result-stats {
        color: #6B4226;
        font-size: 14px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------- Hero section ----------------
st.markdown(
    """
    <div class="hero-nav">
        <div class="hero-logo">🧴 Barber Daily</div>
        <div style="color:#6B4226; font-size:14px;">Affiliate & Influencer Tracker</div>
    </div>
    """,
    unsafe_allow_html=True,
)

if HERO_IMAGE_URL:
    st.image(HERO_IMAGE_URL, use_container_width=True)

st.markdown('<div class="hero-title">Check your influencers.<br>All in one place.</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="hero-subtitle">Paste TikTok video links below and instantly see views, likes, '
    'comments, and shares for each one — no manual checking needed.</div>',
    unsafe_allow_html=True,
)

urls_input = st.text_area(
    "TikTok video links",
    height=180,
    placeholder="https://www.tiktok.com/@username/video/1234567890123456789\nhttps://www.tiktok.com/@username2/video/9876543210987654321",
    label_visibility="collapsed",
)

check_button = st.button("Check Stats", type="primary")


def get_video_stats(url: str) -> dict:
    ydl_opts = {"quiet": True, "no_warnings": True, "skip_download": True}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
    return {
        "Username": info.get("uploader") or info.get("creator") or "",
        "Video Title": (info.get("title") or "")[:80],
        "URL": url,
        "Views": info.get("view_count", ""),
        "Likes": info.get("like_count", ""),
        "Comments": info.get("comment_count", ""),
        "Shares": info.get("repost_count", ""),
        "Upload Date": info.get("upload_date", ""),
        "Status": "OK",
    }


if check_button:
    urls = [u.strip() for u in urls_input.splitlines() if u.strip()]

    if not urls:
        st.warning("Paste at least one TikTok link first.")
    else:
        results = []
        progress = st.progress(0, text="Starting...")

        for i, url in enumerate(urls, start=1):
            progress.progress(i / len(urls), text=f"Checking {i}/{len(urls)}: {url}")
            try:
                results.append(get_video_stats(url))
            except Exception as e:
                results.append({
                    "Username": "", "Video Title": "", "URL": url,
                    "Views": "", "Likes": "", "Comments": "", "Shares": "",
                    "Upload Date": "", "Status": f"FAILED - {str(e)[:60]}",
                })

        progress.empty()

        df = pd.DataFrame(results)
        # Convert to numbers so sorting works even when some links failed
        # (failed links leave blank values, which would otherwise crash the sort)
        for col in ["Views", "Likes", "Comments", "Shares"]:
            df[col] = pd.to_numeric(df[col], errors="coerce")
        df = df.sort_values(by="Views", ascending=False, na_position="last")

        st.markdown(f'<div class="hero-title" style="font-size:26px; margin-top:36px;">Results ({len(urls)} checked)</div>', unsafe_allow_html=True)

        def fmt(val):
            # Show a clean number, or N/A for failed/missing links
            if pd.isna(val):
                return "N/A"
            return f"{int(val):,}"

        cols = st.columns(3)
        for idx, row in enumerate(df.to_dict("records")):
            with cols[idx % 3]:
                status_note = "" if row["Status"] == "OK" else f'<br><span style="color:#B23B3B;">{row["Status"]}</span>'
                st.markdown(
                    f"""
                    <div class="result-card">
                        <h4>@{row['Username'] or 'unknown'}</h4>
                        <div class="result-stats">
                            views: {fmt(row['Views'])}<br>
                            likes: {fmt(row['Likes'])}<br>
                            comments: {fmt(row['Comments'])}<br>
                            shares: {fmt(row['Shares'])}
                            {status_note}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

        st.dataframe(df, use_container_width=True)

        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button(
            "⬇️ Download as CSV",
            data=csv,
            file_name="tiktok_report.csv",
            mime="text/csv",
        )
