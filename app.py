import streamlit as st
import yt_dlp
import requests
from io import BytesIO

st.set_page_config(page_title="Direct Video Downloader", page_icon="💾")

st.title("💾 直接保存ツール")

url = st.text_input("動画URLを入力:", placeholder="https://...")

if url:
    with st.spinner('解析中...（少し時間がかかります）'):
        try:
            # 動画の直URLを取得
            ydl_opts = {'format': 'best', 'quiet': True}
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                video_direct_url = info.get('url')
                title = info.get('title', 'video').replace("/", "_") # ファイル名エラー防止

            if video_direct_url:
                # 動画データをメモリに読み込む
                response = requests.get(video_direct_url, stream=True)
                video_bytes = BytesIO(response.content)

                # プレビュー表示
                st.video(video_bytes)

                # ★ここが重要！直接ダウンロードさせるボタン
                st.download_button(
                    label="📥 動画ファイルを保存する",
                    data=video_bytes,
                    file_name=f"{title}.mp4",
                    mime="video/mp4"
                )
                st.success("準備完了！上のボタンを押して保存してね。")
        
        except Exception as e:
            st.error(f"エラー: {e}")
