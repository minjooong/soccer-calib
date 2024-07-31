import streamlit as st
import requests
import time

# Streamlit 페이지 설정
st.title("유튜브 링크 제출 페이지")
st.write("\n주소 복사 ↓↓↓↓")
st.write("https://youtu.be/O9KANVeDafE")
FASTAPI_URL = st.text_input("Server 주소를 입력하세요:")

# 유튜브 링크 입력
youtube_link = st.text_input("Youtube 링크를 입력하세요:")

# 제출 버튼 클릭 시
if st.button("제출"):
    if youtube_link:
        # FastAPI 서버에 요청 전송
        with st.spinner("동영상 처리 중..."):
            response = requests.post(f"{FASTAPI_URL}/submit_link", json={"link": youtube_link})
        
        if response.status_code == 202:  # 202 Accepted: Task started
            result = response.json()
            task_id = result.get("task_id")

            st.success("링크가 성공적으로 전송되었습니다.")
            st.write("작업 ID:", task_id)

            # 상태 확인
            status = None
            while status != "completed":
                status_response = requests.get(f"{FASTAPI_URL}/task_status/{task_id}")
                if status_response.status_code == 200:
                    status_result = status_response.json()
                    status = status_result.get("status")
                    if status == "completed":
                        st.success("비디오 처리가 완료되었습니다.")
                        st.json(status_result)  # 결과를 표시할 수 있음
                    else:
                        st.write("처리 중... 상태:", status)
                        time.sleep(10)  # 10초 간격으로 상태 확인
                else:
                    st.error("상태 조회 실패")
                    break
        else:
            st.error("링크 전송에 실패했습니다.")
    else:
        st.error("링크를 입력해주세요.")
