from pathlib import Path

import cv2
import os

def extract_frames_from_movie(movie_file, output_dir):
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # Open the video file
    vidcap = cv2.VideoCapture(movie_file)

    success, image = vidcap.read()
    count = 0
    while success:
        # Save frame as JPEG file
        cv2.imwrite(os.path.join(output_dir, f"frame{count}.jpg"), image)
        success, image = vidcap.read()
        print(f'Read a new frame: {success}')
        count += 1

movie_file = Path(__file__).parent / 'input.mp4'
output_directory = Path(__file__).parent / 'input_imgs2'

extract_frames_from_movie(movie_file, output_directory)