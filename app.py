import streamlit as st
import yt_dlp

st.set_page_config(page_title="Quick Video Downloader", page_icon="🎬")

st.title("🎬 動画リンク抽出ツール")
st.write("URLを貼り付けると、動画を再生・保存できるリンクを表示します。")

# URL入力欄
url = st.text_input("動画のURLを入力（X, YouTube, TikTokなど）:", placeholder="https://...")

if url:
    with st.spinner('動画を解析中...'):
        try:
            # yt-dlpの設定（動画のメタデータだけを取得）
            ydl_opts = {'format': 'best'}
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                video_url = info.get('url', None)
                title = info.get('title', '無題の動画')

            if video_url:
                st.success(f"解析完了: {title}")
                
                # プレビュー表示
                st.video(video_url)
                
                # 直接ダウンロードリンク
                st.markdown(f'[👉 ここを右クリックして保存]({video_url})')
            else:
                st.error("動画のURLを取得できませんでした。")
        except Exception as e:
            st.error(f"エラーが発生しました: {e}")

st.divider()
st.caption("Powered by yt-dlp & Streamlit")
