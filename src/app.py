import streamlit as st
from line_extremities import process_video
import json

def main():
    st.title("Soccer Player Position Calculation")

    checkpoint = "./train_59.pt"
    resolution_width = 455
    resolution_height = 256
    pp_radius = 4
    pp_maxdists = 30
    num_points_lines = 2

    with open('coordinates.json', 'r') as f:
        coordinates_data = json.load(f)

    video_file = st.file_uploader("Upload a video file", type=["mp4", "avi", "mov"])
    if video_file is not None:
        st.write("Processing video...")
        video_bytes = video_file.read()
        result = process_video(video_bytes, checkpoint, resolution_width, resolution_height, pp_radius, pp_maxdists, num_points_lines, coordinates_data)
        st.write("Processing complete. Check the output directory for results.")
        st.json(result)



if __name__ == "__main__":
    main()