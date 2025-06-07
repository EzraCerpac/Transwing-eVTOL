import concurrent.futures
import os
import subprocess
from pathlib import Path

import cv2
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
        command = ['convert', input_path, '-fuzz', fuzz, '-fill', 'magenta', '-draw', 'color 0,0 floodfill',
                   '-transparent', 'magenta', output_path]
        subprocess.Popen(command)
        print(f"Background removal started for {os.path.basename(input_path)}")
    except subprocess.CalledProcessError as e:
        print(f"An error occurred processing {os.path.basename(input_path)}: {e}")
        return False
    return True


def process_image(paths) -> bool:
    return remove_background(*paths)
    # return remove_background_with_imagemagick(*paths)


def remove_background_from_images(input_dir, output_dir, crop=False):
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

    if crop:
        crop_images(output_dir, output_dir)


def crop_images(input_dir, output_dir):
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    for filename in os.listdir(input_dir):
        if filename.endswith('.png'):
            # Read the image
            image = cv2.imread(os.path.join(input_dir, filename), -1)

            pre_crop = 100
            h, w = image.shape[:2]
            image = image[pre_crop:h-pre_crop, pre_crop:w-pre_crop]

            # Convert the image to grayscale
            grey = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

            # Apply a threshold to get a binary image
            _, binary = cv2.threshold(grey, 20, 255, cv2.THRESH_BINARY)

            # Find contours
            contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            # Calculate the bounding rectangle of all contours
            x_min = min([cv2.boundingRect(contour)[0] for contour in contours])
            y_min = min([cv2.boundingRect(contour)[1] for contour in contours])
            x_max = max([cv2.boundingRect(contour)[0] + cv2.boundingRect(contour)[2] for contour in contours])
            y_max = max([cv2.boundingRect(contour)[1] + cv2.boundingRect(contour)[3] for contour in contours])

            # Crop the image using the bounding rectangle
            cropped_image = image[y_min:y_max, x_min:x_max]

            # Save the cropped image with the alpha channel
            cv2.imwrite(os.path.join(output_dir, filename), cropped_image, [cv2.IMWRITE_PNG_COMPRESSION, 9])
            print(f"Image {filename} cropped successfully")


if __name__ == '__main__':
    input_directory = Path(__file__).parent / 'input_imgs'
    output_directory = Path(__file__).parent / 'output_imgs'
    output_file = Path(__file__).parent / 'output.gif'

    # input_directory = "/Users/ezracerpac/PycharmProjects/Transwing-eVTOL/data/flight_data/ac_jpgs"
    # output_directory = "/Users/ezracerpac/PycharmProjects/Transwing-eVTOL/data/flight_data/ac_pngs"
    # output2_directory = "/Users/ezracerpac/PycharmProjects/Transwing-eVTOL/data/flight_data/ac_pngs2"

    input_directory = Path(__file__).parent / 'tims_renders'
    output_directory = Path(__file__).parent / 'tims_renders_output'

    remove_background_from_images(input_directory, output_directory, crop=False)
    # crop_images(output_directory, output2_directory)
    # create_gif(output_directory, output_file, duration=0.1)
