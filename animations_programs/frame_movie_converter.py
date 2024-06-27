import os
from pathlib import Path

import cv2
import imageio


def extract_frames_from_movie(movie_file, output_dir, nth_frame=1):
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # Open the video file
    vidcap = cv2.VideoCapture(movie_file)

    success, image = vidcap.read()
    count = 0
    frame_number = 0
    while success:
        # Save frame as JPEG file if it's the nth frame
        if frame_number % nth_frame == 0:
            cv2.imwrite(os.path.join(output_dir, f"frame{count}.jpg"), image)
            count += 1
        success, image = vidcap.read()
        print(f'Read a new frame: {success}')
        frame_number += 1


def create_gif(input_dir, output_file, duration, nth_frame=1):
    # Get all image files in the input directory
    images = sorted(
        [os.path.join(input_dir, file) for file in os.listdir(input_dir) if file.endswith(('.png', '.jpg', '.jpeg'))])

    # Read images into memory
    images_data = [imageio.imread(image) for image in images[::nth_frame]]

    # Write images to gif
    imageio.mimsave(output_file, images_data, duration=duration)
    print(f'Gif created at {output_file}')


if __name__ == '__main__':
    movie_file = Path(__file__).parent / 'input.mp4'
    output_directory = Path(__file__).parent / 'input_imgs'

    extract_frames_from_movie(movie_file, output_directory)

    # create_gif(output_directory, 'output.gif', duration=1e-4, nth_frame=4)

