import streamlit as st
from line_extremities import process_video
import json

def main():
    st.title("Video Processing for Soccer Line Detection")

    checkpoint = "./train_59.pt"
    output_dir = "./outputs"
    resolution_width = 455
    resolution_height = 256
    pp_radius = 4
    pp_maxdists = 30
    num_points_lines = 2
    # masks = False

    with open('coordinates.json', 'r') as f:
        coordinates_data = json.load(f)

    video_file = st.file_uploader("Upload a video file", type=["mp4", "avi", "mov"])
    if video_file is not None:
        st.write("Processing video...")
        video_bytes = video_file.read()
        process_video(video_bytes, checkpoint, output_dir, resolution_width, resolution_height, pp_radius, pp_maxdists, num_points_lines, coordinates_data)
        st.write("Processing complete. Check the output directory for results.")

if __name__ == "__main__":
    main()
