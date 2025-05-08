import numpy as np
from PIL import Image, ImageDraw
import time
import math
import os
import re

# Parameters
input_dir = "sections-export/"  # Input directory for cross-sectional images
output_dir = "string-sections/"  # Output directory for string art images
output_sequence = "string_art_sequences.txt"  # Consolidated sequence file
points_per_side = 25  # Number of points per side (150 total, excluding bottom)
num_jumps = 400  # Number of thread jumps
subtract_intensity = 100  # Intensity to subtract per thread pass
min_distance = 50  # Minimum distance (pixels) between points for jumps
line_width = 1  # Width of lines in output image
image_size = 1182  # Image dimensions (1182x1182 pixels)

# Generate equidistant points along the square border (excluding bottom side)
def generate_points(points_per_side, image_size):
    points = []
    step = image_size / points_per_side  # Distance between points
    
    # Top side (x varies, y = 0)
    for i in range(points_per_side):
        points.append((i * step, 0))
    # Right side (x = image_size, y varies)
    for i in range(points_per_side):
        points.append((image_size - 1, i * step))
    # Left side (x = 0, y varies)
    for i in range(points_per_side):
        points.append((0, (points_per_side - 1 - i) * step))
    
    return np.array(points)

# Calculate distance between two points
def point_distance(p1, p2):
    return math.sqrt((p2[0] - p1[0])**2 + (p2[1] - p1[1])**2)

# Calculate the "score" of a line by summing the darkness of pixels it covers
def line_score(img_array, p1, p2):
    # Bresenham's line algorithm to get pixels along the line
    x1, y1 = int(p1[0]), int(p1[1])
    x2, y2 = int(p2[0]), int(p2[1])
    dx = abs(x2 - x1)
    dy = abs(y2 - y1)
    sx = 1 if x1 < x2 else -1
    sy = 1 if y1 < y2 else -1
    err = dx - dy
    pixels = []
    
    while True:
        if 0 <= x1 < img_array.shape[1] and 0 <= y1 < img_array.shape[0]:
            pixels.append((x1, y1))
        if x1 == x2 and y1 == y2:
            break
        e2 = 2 * err
        if e2 > -dy:
            err -= dy
            x1 += sx
        if e2 < dx:
            err += dx
            y1 += sy
    
    # Sum the darkness (255 - pixel value, since black=0 is max darkness)
    score = sum(255 - img_array[y, x] for x, y in pixels if 0 <= x < img_array.shape[1] and 0 <= y < img_array.shape[0])
    # Normalize by line length to avoid bias toward short lines
    length = max(1, point_distance(p1, p2))
    normalized_score = score / length
    return normalized_score, pixels

# Subtract intensity from pixels along a line
def subtract_line(img_array, pixels):
    for x, y in pixels:
        if 0 <= x < img_array.shape[1] and 0 <= y < img_array.shape[0]:
            img_array[y, x] = min(255, img_array[y, x] + subtract_intensity)

# Main string art algorithm for a single image
def generate_string_art_for_image(input_image_path, output_image_path, sequence_file, section_name):
    # Load and process the input image
    img = Image.open(input_image_path).convert("L")  # Convert to grayscale
    img_array = np.array(img)  # 0 = black, 255 = white
    points = generate_points(points_per_side, image_size)
    num_points = len(points)
    
    # Initialize variables
    current_point = 0  # Start at point 1 (index 0)
    sequence = [current_point + 1]  # Store 1-based point indices
    output_img = Image.new("L", (image_size, image_size), 255)  # White background
    draw = ImageDraw.Draw(output_img)
    
    start_time = time.time()
    
    # Perform the specified number of jumps
    for jump in range(num_jumps):
        best_score = -1
        best_point = None
        best_pixels = None
        
        # Evaluate all possible jumps from the current point
        for i in range(num_points):
            if i == current_point:
                continue
            # Skip points too close to the current point
            if point_distance(points[current_point], points[i]) < min_distance:
                continue
            score, pixels = line_score(img_array, points[current_point], points[i])
            if score > best_score:
                best_score = score
                best_point = i
                best_pixels = pixels
        
        if best_point is None:
            print(f"Parando en salto {jump} para Sección {section_name}: no se encontraron puntos válidos.")
            break
        
        # Draw the line on the output image
        p1 = points[current_point]
        p2 = points[best_point]
        draw.line((p1[0], p1[1], p2[0], p2[1]), fill=0, width=line_width)
        
        # Subtract intensity from the image array
        subtract_line(img_array, best_pixels)
        
        # Update the current point and sequence
        current_point = best_point
        sequence.append(current_point + 1)  # 1-based index
    
    # Save the output image
    output_img.save(output_image_path)
    
    # Append the sequence to the consolidated sequence file
    with open(sequence_file, "a") as f:
        f.write(f"Sección {section_name}:\n")
        f.write(" -> ".join(map(str, sequence)) + "\n\n")
    
    # Print statistics
    print(f"Completado {len(sequence)-1} saltos para Sección {section_name} en {time.time() - start_time:.2f} segundos.")
    print(f"Imagen guardada en: {output_image_path}")

# Main function to process all images
def generate_string_art():
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Initialize the sequence file
    with open(output_sequence, "w") as f:
        f.write("")  # Clear the file
    
    # Get all PNG files in the input directory
    image_files = [f for f in os.listdir(input_dir) if f.endswith(".png") and f.startswith("seccion_")]
    
    # Sort files numerically by section number
    def get_section_number(filename):
        match = re.search(r'seccion_(\d+)\.png', filename)
        return int(match.group(1)) if match else float('inf')
    
    image_files.sort(key=get_section_number)
    
    for image_file in image_files:
        # Extract section number from filename (e.g., seccion_1.png -> 1)
        try:
            section_name = re.search(r'seccion_(\d+)\.png', image_file).group(1)
        except AttributeError:
            print(f"Nombre de archivo inválido: {image_file}. Saltando...")
            continue
        
        input_image_path = os.path.join(input_dir, image_file)
        output_image_path = os.path.join(output_dir, f"seccion_{section_name}_string_art.png")
        
        print(f"Procesando {image_file}...")
        generate_string_art_for_image(input_image_path, output_image_path, output_sequence, section_name)

if __name__ == "__main__":
    generate_string_art()