import os
import subprocess
import cv2
import numpy as np
import random

# Set your variables here
segment_count = 10  # Number of segments
segment_duration = 3  # Duration of each segment in seconds

def generate_video():
    path_to_video = "video.mp4"
    path_to_tmp_playlist = "playlist.txt"
    tmp_playlist = []

    for i in range(segment_count):
        filename = f"segment-{i}.mp4"
        create_segment_video(filename, segment_duration)

        tmp_playlist.append(f"file '{filename}'")

    create_segment_playlist(path_to_tmp_playlist, tmp_playlist)
    create_final_video(path_to_video, path_to_tmp_playlist)

    print(f"Created video in {path_to_video}")

def create_segment_video(filename, segment_duration):
    height, width = 720, 1280  # You can specify your own dimensions
    color_image = np.zeros((height, width, 3), np.uint8)

    # Generate a random color
    color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

    color_image[:] = color  # (B, G, R)
    tmp_color_image = "tmp_color.png"
    cv2.imwrite(tmp_color_image, color_image)

    cmd = f'ffmpeg -y -loop 1 -i {tmp_color_image} ' \
          f'-c:v libx264 -pix_fmt yuv420p ' \
          f'-b:v 7M -minrate 7M -maxrate 10M -bufsize 14M ' \
          f'-t {segment_duration} -r 25 {filename}'

    subprocess.call(cmd, shell=True)

    if os.path.exists(tmp_color_image):
        os.remove(tmp_color_image)

def create_final_video(path_to_video, path_to_tmp_playlist):
    cmd = f'ffmpeg -y -f concat -i {path_to_tmp_playlist} -f lavfi ' \
          f'-i anullsrc=channel_layout=stereo:sample_rate=44100 ' \
          f'-c:v copy -shortest -c:a aac {path_to_video}'

    subprocess.call(cmd, shell=True)

def create_segment_playlist(path_to_tmp_playlist, tmp_playlist):
    with open(path_to_tmp_playlist, 'w') as f:
        f.write("\n".join(tmp_playlist))

if __name__ == "__main__":
    generate_video()