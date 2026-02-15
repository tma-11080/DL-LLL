import streamlit as st
import yt_dlp
import requests
import time
import os
import re
import random
import json
import base64
import hashlib
import datetime
import urllib.parse
from io import BytesIO
from typing import Optional, Dict, Any, List

# ==========================================
# 1. SYSTEM CONFIGURATION & CONSTANTS
# ==========================================
SYSTEM_VERSION = "3.0.0-MAXIMUS"
MAX_CHUNK_SIZE = 1024 * 1024 * 5  # 5MB chunks
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
]

# ==========================================
# 2. UI / GUI ENGINE (NEON STYLE - FIXED)
# ==========================================
st.set_page_config(page_title="NEON VIDEO EXTRACTOR", layout="wide", page_icon="⚡")

st.markdown("""
<style>
    /* CORE THEME: BLACK & NEON */
    .stApp {
        background-color: #000000;
        color: #e0e0e0;
        font-family: 'Courier New', Courier, monospace;
    }
    
    /* HEADER NEON ANIMATION */
    @keyframes neon-pulse {
        0% { text-shadow: 0 0 10px #0000ff, 0 0 20px #0000ff; }
        50% { text-shadow: 0 0 20px #8a2be2, 0 0 40px #8a2be2, 0 0 60px #0000ff; }
        100% { text-shadow: 0 0 10px #0000ff, 0 0 20px #0000ff; }
    }
    
    .neon-text {
        font-size: clamp(30px, 5vw, 60px);
        font-weight: 900;
        color: #fff;
        text-align: center;
        text-transform: uppercase;
        animation: neon-pulse 3s infinite alternate;
        margin-bottom: 40px;
        letter-spacing: 4px;
        border-bottom: 2px solid #8a2be2;
        padding-bottom: 20px;
    }

    /* INPUT FIELD STYLING */
    .stTextInput input {
        background-color: #0a0a0a !important;
        color: #00f2ff !important;
        border: 2px solid #8a2be2 !important;
        box-shadow: 0 0 15px rgba(138, 43, 226, 0.3);
        border-radius: 8px;
        padding: 15px;
        font-size: 1.1rem;
    }
    .stTextInput input:focus {
        box-shadow: 0 0 25px rgba(0, 242, 255, 0.6);
        border-color: #00f2ff !important;
    }

    /* BUTTON STYLING */
    div.stButton > button {
        background: linear-gradient(90deg, #0000ff, #8a2be2);
        color: white;
        border: none;
        padding: 15px 25px;
        border-radius: 8px;
        font-weight: bold;
        text-transform: uppercase;
        letter-spacing: 2px;
        box-shadow: 0 0 20px rgba(0, 0, 255, 0.4);
        transition: all 0.3s ease;
        width: 100%;
    }
    div.stButton > button:hover {
        box-shadow: 0 0 40px rgba(138, 43, 226, 0.8);
        transform: scale(1.02);
        background: linear-gradient(90deg, #8a2be2, #0000ff);
    }

    /* CARD COMPONENT */
    .video-card {
        border: 1px solid #00f2ff;
        padding: 25px;
        border-radius: 12px;
        background: linear-gradient(135deg, rgba(0,0,0,0.9), rgba(20,0,40,0.9));
        box-shadow: inset 0 0 30px rgba(0, 0, 255, 0.1);
        margin-top: 20px;
    }
    
    /* LOG CONSOLE */
    .console-log {
        background: #050505;
        border-left: 3px solid #8a2be2;
        padding: 10px;
        font-family: monospace;
        font-size: 0.8rem;
        color: #00ff00;
        margin-bottom: 5px;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 3. ADVANCED LOGIC MODULES
# ==========================================

class NeonLogger:
    """システムログ管理クラス"""
    def __init__(self):
        if "logs" not in st.session_state:
            st.session_state.logs = []
    
    def info(self, message):
        ts = datetime.datetime.now().strftime("%H:%M:%S")
        st.session_state.logs.append(f"[{ts}] [INFO] {message}")
        
    def error(self, message):
        ts = datetime.datetime.now().strftime("%H:%M:%S")
        st.session_state.logs.append(f"[{ts}] [ERROR] {message}")
        
    def get_logs(self):
        return st.session_state.logs[-20:] # 最新20件

logger = NeonLogger()

class NetworkHandler:
    """高度なネットワークリクエスト処理クラス"""
    def __init__(self):
        self.session = requests.Session()
        
    def get_headers(self, url):
        parsed = urllib.parse.urlparse(url)
        domain = f"{parsed.scheme}://{parsed.netloc}/"
        return {
            'User-Agent': random.choice(USER_AGENTS),
            'Referer': domain, # リファラ偽装（po-kaki-to対策）
            'Accept-Language': 'en-US,en;q=0.9,ja;q=0.8',
        }

    def validate_stream(self, url):
        """動画ストリームの存在確認"""
        try:
            h = self.session.head(url, headers=self.get_headers(url), timeout=5, allow_redirects=True)
            content_type = h.headers.get('Content-Type', '').lower()
            size = int(h.headers.get('Content-Length', 0))
            return 'video' in content_type or 'application/octet-stream' in content_type, size
        except:
            return False, 0

    def download_chunk(self, url):
        """メモリ効率を考慮したバイナリ取得"""
        try:
            resp = self.session.get(url, headers=self.get_headers(url), stream=True, timeout=20)
            resp.raise_for_status()
            return resp.content
        except Exception as e:
            logger.error(f"Download failed: {e}")
            return None

class VideoExtractor:
    """動画抽出エンジン"""
    def __init__(self):
        self.net = NetworkHandler()
        
    def extract(self, url):
        logger.info(f"Analyzing target: {url}")
        
        # 1. 直リンク (.mp4) 判定
        if ".mp4" in url or ".m3u8" in url:
            valid, size = self.net.validate_stream(url)
            if valid:
                logger.info("Direct stream detected.")
                return {
                    'type': 'direct',
                    'title': url.split('/')[-1].split('?')[0],
                    'url': url,
                    'size': size,
                    'thumbnail': None
                }
        
        # 2. yt-dlp による解析
        try:
            ydl_opts = {
                'format': 'best',
                'quiet': True,
                'no_warnings': True,
                'extract_flat': 'in_playlist',
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                logger.info("Metadata extraction successful.")
                return {
                    'type': 'platform',
                    'title': info.get('title', 'Unknown Video'),
                    'url': info.get('url'),
                    'thumbnail': info.get('thumbnail'),
                    'duration': info.get('duration'),
                    'uploader': info.get('uploader')
                }
        except Exception as e:
            logger.error(f"Extraction Error: {e}")
            return None

# ==========================================
# 4. MAIN APPLICATION LOGIC
# ==========================================

def main():
    # Header
    st.markdown('<div class="neon-text">NEON CORE SYSTEM</div>', unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.markdown("### 📡 SYSTEM MONITOR")
        st.write("STATUS: **ONLINE**")
        st.progress(100)
        
        st.markdown("---")
        st.markdown("### 📝 EVENT LOGS")
        log_container = st.empty()
        
        # ログ表示ループ
        logs = logger.get_logs()
        log_html = ""
        for log in reversed(logs):
            color = "#ff0055" if "[ERROR]" in log else "#00ff00"
            log_html += f'<div class="console-log" style="color:{color};">{log}</div>'
        log_container.markdown(log_html, unsafe_allow_html=True)

    # Main Area
    col1, col2, col3 = st.columns([1, 8, 1])
    
    with col2:
        # URL Input
        target_url = st.text_input("ENTER TARGET URL", placeholder="https://example.com/video...")
        
        if target_url:
            extractor = VideoExtractor()
            net_handler = NetworkHandler()
            
            with st.spinner("⚡ DECRYPTING VIDEO STREAM..."):
                data = extractor.extract(target_url)
                
                if data:
                    # Success UI
                    st.markdown(f'<div class="video-card">', unsafe_allow_html=True)
                    
                    c1, c2 = st.columns([1, 1])
                    with c1:
                        if data.get('thumbnail'):
                            st.image(data['thumbnail'], use_container_width=True)
                        else:
                            st.markdown("### 🎬 [NO SIGNAL]")
                            
                    with c2:
                        st.markdown(f"## {data['title']}")
                        st.markdown(f"**TYPE:** `{data['type'].upper()}`")
                        if data.get('size'):
                            size_mb = data['size'] / (1024*1024)
                            st.markdown(f"**SIZE:** `{size_mb:.2f} MB`")
                        st.markdown(f"**SOURCE:** `{target_url[:30]}...`")
                    
                    st.divider()
                    
                    # Video Player
                    if data.get('url'):
                        st.video(data['url'])
                        
                        # Download Logic
                        st.markdown("### 💾 DOWNLOAD OPS")
                        
                        # ボタンの状態管理
                        if 'dl_data' not in st.session_state:
                            st.session_state.dl_data = None

                        if st.button("🚀 INITIATE DOWNLOAD SEQUENCE"):
                            with st.spinner("Downloading to server buffer..."):
                                binary_data = net_handler.download_chunk(data['url'])
                                if binary_data:
                                    st.session_state.dl_data = binary_data
                                    logger.info("Download buffer complete.")
                                    st.success("BUFFER COMPLETE. READY TO SAVE.")
                        
                        if st.session_state.dl_data:
                            st.download_button(
                                label="📥 SAVE MP4 FILE",
                                data=st.session_state.dl_data,
                                file_name=f"{data['title']}.mp4",
                                mime="video/mp4",
                                use_container_width=True
                            )
                    
                    st.markdown('</div>', unsafe_allow_html=True)
                else:
                    st.error("SYSTEM FAILURE: Target Unreachable.")

    # Footer Filler (Functional)
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    st.caption(f"NEON CORE v{SYSTEM_VERSION} | SECURE CONNECTION ESTABLISHED")

if __name__ == "__main__":
    main()
