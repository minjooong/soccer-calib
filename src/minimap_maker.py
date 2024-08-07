import json
import os
import cv2
import numpy as np
from scipy.signal import savgol_filter
from yt_dlp.networking.impersonate import dataclass

def create_smooth_video(data, label_path, field_img_path, output_video_path):
    #########################

    file_names = os.listdir(label_path)

    #########################

    # Load transformation data
    data_json_tmp = json.dumps(data)
    data_json = json.loads(data_json_tmp)
    transformation_data = data_json["frames"]


    # Parse and transform player data
    transformed_data = {}
    for i in range(len(file_names)):
        # try:
            # Retrieve the corresponding transformation matrix for the frame
            transform_matrix = np.array(transformation_data[i]['matrix_data'])

            # Read label content
            #########################

            filename = f"video_120_{i+1}.txt"
            file_path = os.path.join(label_path, filename)
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
            # content = label[i]

            #########################
            data_list = [list(map(float, row.split())) for row in content.split('\n') if row]
            data_array = np.array(data_list)
            
            player_points = []
            player_indices = []
            for row in data_array:
                player_x = row[1]
                player_y = row[2]
                player_height = row[4]
                player_idx = row[5]
                player_point = [int(player_x * 1920), int((player_y + (player_height / 2)) * 1080)]
                player_points.append(player_point)
                player_indices.append(player_idx)

            player_points = np.array(player_points, dtype=np.float32).reshape(-1, 1, 2)
            transformed_player_points = cv2.perspectiveTransform(player_points, transform_matrix)
            transformed_player_points = transformed_player_points.reshape(-1, 2)

            frame_data = []
            for idx, point in zip(player_indices, transformed_player_points):
                frame_data.append({
                    'id': int(idx),
                    'x': float(round(point[0], 2)),
                    'y': float(round(point[1], 2))
                })
            
            transformed_data[f"Frame_{i+1}"] = frame_data

        # except Exception as e:
        #     print(f"Error processing file {filename}: {e}")

    # Smooth the player positions
    player_positions = {}
    player_start_frames = {}

    for frame_idx, (frame, positions) in enumerate(transformed_data.items()):
        for player in positions:
            if player['id'] not in player_positions:
                player_positions[player['id']] = {'x': [], 'y': []}
                player_start_frames[player['id']] = frame_idx  # Record the starting frame for each player
            player_positions[player['id']]['x'].append(player['x'])
            player_positions[player['id']]['y'].append(player['y'])

    # Apply Savitzky-Golay filter to smooth the positions
    window_length = 11  # Use a larger window length for more smoothing
    polyorder = 1      # Use a higher polynomial order for smoother results

    smoothed_positions = {}
    for player_id, coords in player_positions.items():
        if len(coords['x']) >= window_length:
            smoothed_x = savgol_filter(coords['x'], window_length, polyorder)
            smoothed_y = savgol_filter(coords['y'], window_length, polyorder)
            smoothed_positions[player_id] = {
                'x': smoothed_x,
                'y': smoothed_y,
                'start_frame': player_start_frames[player_id]
            }

    # Prepare data for animation
    frames = {}
    num_frames = len(transformed_data)

    for frame_idx in range(num_frames):
        frame_data = []
        for player_id, coords in smoothed_positions.items():
            start_frame = coords['start_frame']
            if start_frame <= frame_idx < start_frame + len(coords['x']):
                relative_idx = frame_idx - start_frame
                frame_data.append({
                    'id': player_id,
                    'x': coords['x'][relative_idx],
                    'y': coords['y'][relative_idx]
                })
        frames[f"Frame_{frame_idx+1}"] = frame_data

    # Load the field image
    field = cv2.imread(field_img_path)
    output_size = (1050, 680)
    fps = 30
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')

    out = cv2.VideoWriter(output_video_path, fourcc, fps, output_size)

    # Create the video
    for frame in frames:
        background = field.copy()
        players = frames[frame]
        for player in players:
            player_point = (int(player['x']), int(player['y']))
            radius = 5
            color = (255, 255, 255)
            thickness = -1  # Fill the circle
            cv2.circle(background, player_point, radius, color, thickness)
        out.write(background)

    out.release()
    #print(f"Video saved at {output_video_path}")