import concurrent.futures
import os
from pathlib import Path

import imageio
from PIL import Image
from rembg import remove


def remove_background(input_path, output_path) -> bool:
    try:
        # Open the image and remove its background
        original_image = Image.open(input_path)
        image_without_bg = remove(original_image)

        # Save the new image with a.png extension
        image_without_bg.save(output_path)
        print(f"Background removed successfully for {os.path.basename(input_path)}")
    except Exception as e:
        print(f"An error occurred processing {os.path.basename(input_path)}: {e}")
        return False
    return True


def process_image(paths) -> bool:
    return remove_background(*paths)


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
        print("All images were processed successfully.")
    else:
        print("Some images were not processed successfully.")


def create_gif(input_dir, output_file, duration):
    # Get all image files in the input directory
    images = sorted(
        [os.path.join(input_dir, file) for file in os.listdir(input_dir) if file.endswith(('.png', '.jpg', '.jpeg'))])

    # Read images into memory
    images_data = [imageio.imread(image) for image in images]

    # Write images to gif
    imageio.mimsave(output_file, images_data, duration=duration)


if __name__ == '__main__':
    input_directory = Path(__file__).parent / 'input_imgs'
    output_directory = Path(__file__).parent / 'output_imgs'
    output_file = Path(__file__).parent / 'output.gif'

    remove_background_from_images(input_directory, output_directory)
    # create_gif(output_directory, output_file, duration=0.1)
