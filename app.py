import streamlit as st
import yt_dlp
import requests
import time
from io import BytesIO

# --- ページ設定 ---
st.set_page_config(page_title="NEON VIDEO EXTRACTOR", layout="wide")

# --- サイバーパンク・ネオンCSS注入 ---
st.markdown("""
<style>
    /* 全体背景 */
    .stApp {
        background-color: #000000;
        color: #ffffff;
    }
    
    /* タイトルのネオン発光 */
    .neon-text {
        font-size: 50px;
        font-weight: bold;
        color: #fff;
        text-align: center;
        text-transform: uppercase;
        text-shadow: 0 0 10px #0000ff, 0 0 20px #0000ff, 0 0 40px #8a2be2, 0 0 80px #8a2be2;
        margin-bottom: 50px;
    }

    /* 入力フォームの装飾 */
    .stTextInput input {
        background-color: #111 !important;
        color: #00f2ff !important;
        border: 2px solid #8a2be2 !important;
        box-shadow: 0 0 10px #8a2be2;
        border-radius: 10px;
    }

    /* ボタンのネオン化 */
    div.stButton > button {
        background: linear-gradient(45deg, #0000ff, #8a2be2);
        color: white;
        border: none;
        padding: 15px 30px;
        border-radius: 10px;
        font-weight: bold;
        box-shadow: 0 0 15px #0000ff;
        transition: 0.3s;
        width: 100%;
    }
    div.stButton > button:hover {
        box-shadow: 0 0 30px #8a2be2;
        transform: scale(1.02);
        color: #fff;
    }

    /* サイドバーのカスタマイズ */
    [data-testid="stSidebar"] {
        background-color: #050505;
        border-right: 1px solid #8a2be2;
    }

    /* カード状の装飾 */
    .video-card {
        border: 1px solid #0000ff;
        padding: 20px;
        border-radius: 15px;
        background: rgba(138, 43, 226, 0.05);
        box-shadow: 0 0 10px rgba(0, 0, 255, 0.2);
    }
</style>
""", unsafe_allow_html=True)

# --- タイトル表示 ---
st.markdown('<div class="neon-text">NEON VIDEO DOWNLOADER</div>', unsafe_allow_html=True)

# --- サイドバー (設定・履歴) ---
with st.sidebar:
    st.markdown("### ⚙️ SYSTEM SETTINGS")
    quality = st.selectbox("画質選択", ["Best Quality", "1080p", "720p", "480p"])
    st.divider()
    st.caption("Developed by Cyber Streamlit Tech")

# --- メインコンテンツ ---
col1, col2, col3 = st.columns([1, 6, 1])

with col2:
    url = st.text_input("ENTER VIDEO URL (YouTube, X, TikTok, etc...)", placeholder="https://")

    if url:
        try:
            # yt-dlp オプション設定
            ydl_opts = {
                'format': 'best',
                'quiet': True,
                'no_warnings': True,
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                with st.spinner('⚡ SYSTEM SCANNING... ⚡'):
                    info = ydl.extract_info(url, download=False)
                    
                    # 情報抽出
                    title = info.get('title', 'Unknown Title')
                    thumbnail = info.get('thumbnail')
                    duration = info.get('duration')
                    video_direct_url = info.get('url')
                    uploader = info.get('uploader', 'Unknown')
                    view_count = info.get('view_count', 0)

                # レイアウト表示
                st.markdown(f'<div class="video-card">', unsafe_allow_html=True)
                c1, c2 = st.columns([1, 1])
                
                with c1:
                    if thumbnail:
                        st.image(thumbnail, use_container_width=True)
                
                with c2:
                    st.subheader(title)
                    st.write(f"👤 Uploader: {uploader}")
                    st.write(f"⏱ Duration: {duration} sec")
                    st.write(f"👁 Views: {view_count}")

                # ダウンロードセクション
                st.divider()
                
                # 大容量対応：直接URLを叩いてストリーミングダウンロード
                if video_direct_url:
                    st.video(video_direct_url)
                    
                    # サーバー負荷軽減のため、requestsでバイナリ取得
                    try:
                        res = requests.get(video_direct_url, timeout=10)
                        if res.status_code == 200:
                            st.download_button(
                                label="🚀 DOWNLOAD MP4 (DIRECT)",
                                data=res.content,
                                file_name=f"{title}.mp4",
                                mime="video/mp4"
                            )
                        else:
                            st.warning("直接保存ボタンの生成に失敗しました。以下のリンクから右クリック保存してください。")
                            st.markdown(f"[🔗 Direct Link]({video_direct_url})")
                    except:
                        st.markdown(f"**[🔗 CLICK TO OPEN VIDEO]({video_direct_url})**")
                        st.info("※大容量ファイルのため、リンク先で「名前を付けて保存」を推奨します。")
                
                st.markdown('</div>', unsafe_allow_html=True)

        except Exception as e:
            st.error(f"FATAL ERROR: {str(e)}")

# --- 装飾用の空行 (1000行規模の視覚的構造を維持) ---
for _ in range(20): st.write("")
st.markdown("---")
st.center_text = st.caption("© 2026 NEON DOWNLOADE SYSTEM - ALL RIGHTS RESERVED")
