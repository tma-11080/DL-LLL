import streamlit as st
import yt_dlp
import requests
import time
import os
import re
import random
import json
import datetime
import urllib.parse
from io import BytesIO
from concurrent.futures import ThreadPoolExecutor

# ==========================================
# 1. SYSTEM CORE CONFIG
# ==========================================
SYSTEM_VERSION = "4.0.0-BATCH-CORE"
MAX_WORKERS = 3  # 並列処理数

# ==========================================
# 2. NEON UI ENGINE (IMMUTABLE)
# ==========================================
st.set_page_config(page_title="NEON BATCH DOWNLOADER", layout="wide", page_icon="⚡")

st.markdown("""
<style>
    /* CORE THEME */
    .stApp {
        background-color: #000000;
        color: #e0e0e0;
        font-family: 'Courier New', Courier, monospace;
    }
    
    /* NEON HEADER */
    .neon-text {
        font-size: clamp(30px, 5vw, 60px);
        font-weight: 900;
        color: #fff;
        text-align: center;
        text-transform: uppercase;
        text-shadow: 0 0 10px #0000ff, 0 0 20px #8a2be2;
        margin-bottom: 30px;
        border-bottom: 2px solid #8a2be2;
        padding-bottom: 20px;
        animation: pulse 3s infinite;
    }
    @keyframes pulse {
        0% { text-shadow: 0 0 10px #0000ff; }
        50% { text-shadow: 0 0 30px #8a2be2, 0 0 50px #0000ff; }
        100% { text-shadow: 0 0 10px #0000ff; }
    }

    /* TEXT AREA (MULTI-URL) */
    .stTextArea textarea {
        background-color: #0a0a0a !important;
        color: #00f2ff !important;
        border: 2px solid #8a2be2 !important;
        box-shadow: 0 0 15px rgba(138, 43, 226, 0.2);
        border-radius: 8px;
        font-family: monospace;
    }
    .stTextArea textarea:focus {
        box-shadow: 0 0 25px rgba(0, 242, 255, 0.5);
        border-color: #00f2ff !important;
    }

    /* BUTTONS */
    div.stButton > button {
        background: linear-gradient(90deg, #0000ff, #8a2be2);
        color: white; border: none; padding: 10px 20px;
        border-radius: 5px; font-weight: bold;
        box-shadow: 0 0 15px #0000ff; transition: 0.3s;
        width: 100%;
    }
    div.stButton > button:hover {
        box-shadow: 0 0 30px #8a2be2; transform: scale(1.02);
    }

    /* VIDEO CARD */
    .batch-card {
        border: 1px solid #00f2ff;
        padding: 15px;
        border-radius: 10px;
        background: rgba(10, 10, 30, 0.8);
        margin-bottom: 15px;
        border-left: 5px solid #8a2be2;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 3. ADVANCED LOGIC KERNEL
# ==========================================

class NetworkCore:
    def __init__(self):
        self.session = requests.Session()
        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15"
        ]

    def generate_headers(self, url):
        # po-kaki-to 用の強力なリファラ偽装
        domain = urllib.parse.urlparse(url).netloc
        return {
            'User-Agent': random.choice(self.user_agents),
            'Referer': f'https://{domain}/',
            'Origin': f'https://{domain}',
            'Accept': '*/*',
            'Connection': 'keep-alive'
        }

    def fetch_stream(self, url):
        """ストリームデータをバッファリング"""
        try:
            headers = self.generate_headers(url)
            with self.session.get(url, headers=headers, stream=True, timeout=30) as r:
                r.raise_for_status()
                return BytesIO(r.content)
        except Exception as e:
            return None

class URLProcessor:
    @staticmethod
    def extract_filename(url):
        """URLから適切なファイル名を抽出 (query param対応)"""
        # po-kaki-to の ?name=XXXXX.mp4 パターンに対応
        try:
            parsed = urllib.parse.urlparse(url)
            query_params = urllib.parse.parse_qs(parsed.query)
            
            if 'name' in query_params:
                # nameパラメータがある場合 (例: 28651-1.mp4)
                return query_params['name'][0]
            
            path_name = os.path.basename(parsed.path)
            if path_name and '.' in path_name:
                return path_name
                
            return f"video_{int(time.time())}.mp4"
        except:
            return "downloaded_video.mp4"

# ==========================================
# 4. MAIN APPLICATION
# ==========================================

def main():
    st.markdown('<div class="neon-text">NEON BATCH SYSTEM</div>', unsafe_allow_html=True)

    # ステータス管理
    if 'queue' not in st.session_state:
        st.session_state.queue = []
    
    col1, col2, col3 = st.columns([1, 8, 1])
    
    with col2:
        st.markdown("### 📥 MULTI-LINK INJECTION")
        # 複数行入力に対応
        raw_urls = st.text_area(
            "PASTE LINKS (ONE PER LINE)", 
            placeholder="https://f2-movie.po-kaki-to.com/movie.php?name=28651-1.mp4\nhttps://f2-movie.po-kaki-to.com/movie.php?name=28651-2.mp4",
            height=150
        )
        
        process_btn = st.button("⚡ ANALYZE & PROCESS QUEUE")

        if process_btn and raw_urls:
            # URLリストの正規化
            urls = [u.strip() for u in raw_urls.split('\n') if u.strip()]
            st.session_state.queue = urls
            st.success(f"QUEUE LOADED: {len(urls)} TARGETS")

        # キュー処理画面
        if st.session_state.queue:
            st.markdown("---")
            st.markdown(f"### ⚙️ PROCESSING QUEUE ({len(st.session_state.queue)} FILES)")
            
            net = NetworkCore()
            
            for i, target_url in enumerate(st.session_state.queue):
                # UIカード生成
                st.markdown(f'<div class="batch-card">', unsafe_allow_html=True)
                
                fname = URLProcessor.extract_filename(target_url)
                
                c1, c2, c3 = st.columns([6, 2, 2])
                with c1:
                    st.markdown(f"**TARGET {i+1}:** `{fname}`")
                    st.caption(f"SOURCE: {target_url[:40]}...")
                
                with c2:
                    # プレビューボタン（動作確認用）
                    if st.checkbox(f"Show Preview #{i+1}", key=f"prev_{i}"):
                        st.video(target_url)

                with c3:
                    # 個別ダウンロードロジック
                    # Streamlitの制限上、ループ内で直接DLボタンを大量生成すると重くなるため
                    # 「Load Data」→「Download」の2ステップ方式を採用
                    load_key = f"load_{i}"
                    
                    if st.button(f"📥 FETCH DATA #{i+1}", key=load_key):
                        with st.spinner("Downloading..."):
                            data_stream = net.fetch_stream(target_url)
                            
                            if data_stream:
                                st.session_state[f"data_{i}"] = data_stream
                                st.success("READY")
                            else:
                                st.error("FAILED")

                    if f"data_{i}" in st.session_state:
                        st.download_button(
                            label="💾 SAVE FILE",
                            data=st.session_state[f"data_{i}"],
                            file_name=fname,
                            mime="video/mp4",
                            key=f"dl_{i}"
                        )

                st.markdown('</div>', unsafe_allow_html=True)

    # Footer
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.caption(f"NEON BATCH CORE v{SYSTEM_VERSION} | THREADS: {MAX_WORKERS}")

if __name__ == "__main__":
    main()
