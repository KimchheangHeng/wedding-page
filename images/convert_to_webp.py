import os
from PIL import Image

# Define the folder paths
input_folder = "qrcode"
output_folder = "qrcode_webp"

# Create output folder if it doesn't exist
os.makedirs(output_folder, exist_ok=True)

# Loop through the images in the input folder
for filename in os.listdir(input_folder):
    if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
        input_path = os.path.join(input_folder, filename)
        output_path = os.path.join(output_folder, os.path.splitext(filename)[0] + ".webp")
        
        # Open image and save as WebP with lossy compression (quality 80)
        with Image.open(input_path) as img:
            img.save(output_path, "WEBP", quality=80)  # Adjust quality as needed
        print(f"Converted {filename} to WebP with lossy compression")
print("Conversion completed!")