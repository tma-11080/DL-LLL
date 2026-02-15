import streamlit as st
import requests
import yt_dlp
from io import BytesIO
import time

# --- ページ設定 & CSS (青・紫・黒のネオン・サイバーパンク) ---
st.set_page_config(page_title="NEON CORE - VIDEO EXTRACTOR", layout="wide")

st.markdown("""
<style>
    /* 全体背景：黒から深い紫へのグラデーション */
    .stApp {
        background: radial-gradient(circle at top, #1a0033 0%, #000000 100%);
        color: #e0e0e0;
        font-family: 'Courier New', Courier, monospace;
    }
    
    /* ヘッダー：光る青と紫 */
    .header-container {
        text-align: center;
        padding: 50px;
        background: rgba(0, 0, 0, 0.5);
        border-bottom: 2px solid #8a2be2;
        box-shadow: 0 10px 30px #0000ff88;
        margin-bottom: 40px;
    }

    .neon-title {
        font-size: clamp(2rem, 8vw, 5rem);
        font-weight: 900;
        color: #fff;
        text-transform: uppercase;
        letter-spacing: 5px;
        text-shadow: 0 0 5px #fff, 0 0 10px #fff, 0 0 20px #0000ff, 0 0 40px #0000ff, 0 0 80px #8a2be2;
        animation: glow 2s ease-in-out infinite alternate;
    }

    @keyframes glow {
        from { text-shadow: 0 0 10px #0000ff, 0 0 20px #0000ff; }
        to { text-shadow: 0 0 20px #8a2be2, 0 0 40px #8a2be2, 0 0 60px #0000ff; }
    }

    /* 入力エリア：青の縁取り */
    .stTextInput > div > div > input {
        background-color: #0d0d0d !important;
        border: 2px solid #00f2ff !important;
        color: #00f2ff !important;
        box-shadow: 0 0 15px #00f2ff33;
        font-size: 1.2rem;
    }

    /* ボタン：紫のグラデーション発光 */
    div.stButton > button {
        background: linear-gradient(90deg, #0000ff, #8a2be2) !important;
        border: none !important;
        color: white !important;
        font-weight: bold !important;
        height: 3em !important;
        box-shadow: 0 0 20px #8a2be2 !important;
        transition: 0.5s !important;
    }
    div.stButton > button:hover {
        box-shadow: 0 0 40px #00f2ff !important;
        transform: scale(1.05);
    }

    /* 情報カード */
    .info-card {
        background: rgba(138, 43, 226, 0.1);
        border: 1px solid #8a2be2;
        padding: 25px;
        border-radius: 15px;
        box-shadow: inset 0 0 20px #8a2be222;
    }
</style>
""", unsafe_allow_html=True)

# --- メインコンテンツ ---
st.markdown('<div class="header-container"><h1 class="neon-title">NEON EXTRACTOR</h1></div>', unsafe_allow_html=True)

col1, col2, col3 = st.columns([1, 8, 1])

with col2:
    target_url = st.text_input("🔗 PASTE TARGET URL HERE", placeholder="https://...")
    
    if target_url:
        st.markdown('<div class="info-card">', unsafe_allow_html=True)
        
        with st.spinner("⚡ ANALYZING CORE DATA..."):
            try:
                # 汎用的な動画取得設定
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                    'Referer': 'https://f2-movie.po-kaki-to.com/' # 特定サイト対策のバイパス
                }

                # 1. 直接リンク系（po-kaki-to等）かチェック
                if ".mp4" in target_url:
                    video_data = requests.get(target_url, headers=headers).content
                    video_name = target_url.split('/')[-1]
                    video_url = target_url
                else:
                    # 2. yt-dlpでの解析
                    with yt_dlp.YoutubeDL({'format': 'best', 'quiet': True}) as ydl:
                        info = ydl.extract_info(target_url, download=False)
                        video_url = info.get('url')
                        video_name = f"{info.get('title', 'video')}.mp4"
                        video_data = requests.get(video_url, headers=headers).content

                # UI表示
                st.subheader(f"💎 TARGET: {video_name}")
                
                # プレビュー
                st.video(video_url)
                
                # ダウンロードボタン
                st.download_button(
                    label="💾 DOWNLOAD COMPLETE FILE",
                    data=video_data,
                    file_name=video_name,
                    mime="video/mp4",
                    use_container_width=True
                )
                
                st.success("ACCESS GRANTED. FILE READY FOR DOWNLOAD.")

            except Exception as e:
                st.error(f"⚠️ ACCESS DENIED: {str(e)}")
                st.info("ヒント: 直リンクの場合はURLの末尾が.mp4であることを確認してください。")
        
        st.markdown('</div>', unsafe_allow_html=True)

# フッター
st.markdown("<br><br><br>", unsafe_allow_html=True)
st.caption("SYSTEM STATUS: STABLE | CORE: PYTHON 3.10 | UI: NEON-V3")
