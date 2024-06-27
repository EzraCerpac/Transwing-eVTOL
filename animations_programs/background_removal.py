import concurrent.futures
import os
import subprocess
from pathlib import Path

import cv2
import imageio
from PIL import Image
from rembg import remove


def remove_background(input_path, output_path) -> bool:
    try:
        # Open the image with OpenCV and remove its background
        original_image = cv2.imread(input_path)
        image_without_bg = remove(original_image)

        # Save the new image with a.png extension
        cv2.imwrite(output_path, image_without_bg)
        print(f"Background removed successfully for {os.path.basename(input_path)}")
    except Exception as e:
        print(f"An error occurred processing {os.path.basename(input_path)}: {e}")
        return False
    return True

def remove_background_with_imagemagick(input_path: str, output_path: str, fuzz: str = '30%') -> bool:
    try:
        # Run the ImageMagick command
        command = ['convert', input_path, '-fuzz', fuzz, '-fill', 'magenta', '-draw', 'color 0,0 floodfill', '-transparent', 'magenta', output_path]
        subprocess.run(command, check=True)
        print(f"Background removed successfully for {os.path.basename(input_path)}")
    except subprocess.CalledProcessError as e:
        print(f"An error occurred processing {os.path.basename(input_path)}: {e}")
        return False
    return True

def process_image(paths) -> bool:
    # return remove_background(*paths)
    return remove_background_with_imagemagick(*paths)


def remove_background_from_images(input_dir, output_dir):
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # Create a list of tuples, each containing the full input and output file paths
    paths = [(os.path.join(input_dir, filename), os.path.join(output_dir, filename.rsplit('.', 1)[0] + '.png'))
             for filename in os.listdir(input_dir) if filename.endswith(('.png', '.jpg', '.jpeg'))]

    # Use a ProcessPoolExecutor to process the images in parallel
    with concurrent.futures.ProcessPoolExecutor() as executor:
        results = list(executor.map(process_image, paths))

    # Check if all images were processed successfully
    if all(results):
        print(f"All images were processed successfully, and saved in {output_dir}")
    else:
        print("Some images were not processed successfully.")



if __name__ == '__main__':
    input_directory = Path(__file__).parent / 'input_imgs'
    output_directory = Path(__file__).parent / 'output_imgs'
    output_file = Path(__file__).parent / 'output.gif'

    remove_background_from_images(input_directory, output_directory)
    # create_gif(output_directory, output_file, duration=0.1)
