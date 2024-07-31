import streamlit as st
import requests
import io
import yt_dlp as youtube_dl

# FastAPI 서버 URL (ngrok URL)
# FASTAPI_URL = "https://21eb-34-143-197-196.ngrok-free.app"

st.title("유튜브 다운로드 페이지")

youtube_url = st.text_input("유튜브 링크를 입력하세요")

if youtube_url:
    try:
        # Download the YouTube video using yt-dlp
        ydl_opts = {
            'format': 'best',
            'outtmpl': 'video.mp4',
            'noplaylist': True,
        }
        
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(youtube_url, download=False)
            video_title = info_dict.get('title', None)
            video_bytes = io.BytesIO()
            ydl.download([youtube_url])
            with open('video.mp4', 'rb') as f:
                video_bytes.write(f.read())
            video_bytes.seek(0)

        # st.video(youtube_url)
        
        # if st.button("처리 시작"):
        #     with st.spinner("동영상 처리 중..."):
        #         # Check the size and type of video_bytes before sending
        #         video_size = len(video_bytes.getvalue())
        #         st.write(f"Downloaded video size: {video_size} bytes")

        #         # Send the video bytes to the FastAPI server
        #         files = {"video": ("video.mp4", video_bytes, "video/mp4")}
        #         headers = {
        #             "Content-Type": "multipart/form-data"
        #         }
                
        #         # Disable SSL verification (not recommended for production)
        #         response = requests.post(f"{FASTAPI_URL}/upload_video/", files=files, headers=headers, verify=False)
                
        #         if response.status_code == 200:
        #             result = response.json()
        #             st.success("동영상 처리 완료!")
        #             st.json(result)
        #         else:
        #             st.error(f"오류 발생: {response.status_code} - {response.text}")
        #             st.write("Response content:", response.content)
    except Exception as e:
        st.error(f"유튜브 링크를 처리하는 중 오류가 발생했습니다: {e}")
