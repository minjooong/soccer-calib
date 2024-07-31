import streamlit as st
import requests
import io

# FastAPI 서버 URL (ngrok URL)
FASTAPI_URL = "https://f188-35-230-102-96.ngrok-free.app"

st.title("동영상 업로드 페이지")

uploaded_file = st.file_uploader("동영상 파일을 선택하세요", type=["mp4", "avi", "mov"])

if uploaded_file is not None:
    st.video(uploaded_file)
    
    if st.button("처리 시작"):
        video_bytes = uploaded_file.getvalue()
        
        files = {"video": ("video.mp4", io.BytesIO(video_bytes), "video/mp4")}
        
        with st.spinner("동영상 처리 중..."):
            response = requests.post(f"{FASTAPI_URL}/upload_video/", files=files)
        
        if response.status_code == 200:
            result = response.json()
            st.success("동영상 처리 완료!")
            st.json(result)
        else:
            st.error(f"오류 발생: {response.status_code} - {response.text}")