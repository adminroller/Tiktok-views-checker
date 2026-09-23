"""
TikTok Influencer Checker - Web App
-------------------------------------
A shareable website version of the TikTok stats checker. Paste links in
the browser, click a button, get a table of views/likes/comments/shares,
and download it as CSV. Your co-worker just opens the link - no install
needed on their end.

HOW TO RUN LOCALLY (to test before sharing):
    pip install streamlit yt-dlp
    streamlit run streamlit_app.py

HOW TO DEPLOY SO YOUR CO-WORKER CAN ACCESS IT (free, ~5 minutes):
    1. Create a free GitHub account (github.com) if you don't have one.
    2. Create a new repository and upload this file (streamlit_app.py)
       plus a file named "requirements.txt" containing:
           streamlit
           yt-dlp
    3. Go to https://share.streamlit.io , sign in with GitHub.
    4. Click "New app", pick your repository and this file.
    5. Click Deploy. You'll get a link like:
           https://yourname-tiktok-checker.streamlit.app
    6. Send that link to your co-worker - they just open it in a browser.
"""

import streamlit as st
import pandas as pd
import yt_dlp

st.set_page_config(page_title="Barber Daily TikTok Checker", layout="wide")

st.title("🧴 Barber Daily TikTok Checker")
st.write(
    "Paste TikTok video links below (one per line), then click **Check Stats**. "
    "Works on public videos only."
)

urls_input = st.text_area(
    "TikTok video links",
    height=200,
    placeholder="https://www.tiktok.com/@username/video/1234567890123456789\nhttps://www.tiktok.com/@username2/video/9876543210987654321",
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
        df = df.sort_values(by="Views", ascending=False, na_position="last")

        st.success(f"Checked {len(urls)} video(s).")
        st.dataframe(df, use_container_width=True)

        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button(
            "⬇️ Download as CSV",
            data=csv,
            file_name="tiktok_report.csv",
            mime="text/csv",
        )
