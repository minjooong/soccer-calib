import streamlit as st
import io
import yt_dlp as youtube_dl

st.markdown("<h1 style='text-align: center; color: white;'>유튜브 동영상 다운로드</h1>", unsafe_allow_html=True)

youtube_url = st.text_input("유튜브 링크를 입력하세요")

if st.button("동영상 찾기"):
    if youtube_url:
        with st.spinner("동영상 찾는 중..."):
            try:
                # Download the YouTube video using yt-dlp
                ydl_opts = {
                    'format': 'best',
                    'outtmpl': 'video.mp4',
                    'noplaylist': True,
                }

                with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                    info_dict = ydl.extract_info(youtube_url, download=False)
                    video_title = info_dict.get('title', None) or "downloaded_video"
                    ydl.download([youtube_url])

                # Load the downloaded video into a BytesIO object
                video_bytes = io.BytesIO()
                with open(f"video.mp4", 'rb') as f:
                    video_bytes.write(f.read())
                video_bytes.seek(0)
                
                # Add a download button for the video
                st.download_button(
                    label="동영상 다운로드",
                    data=video_bytes,
                    file_name=f"{video_title}.mp4",
                    mime='video/mp4'
                )

                st.video(youtube_url)

            except Exception as e:
                st.error(f"유튜브 링크를 처리하는 중 오류가 발생했습니다: {e}")
