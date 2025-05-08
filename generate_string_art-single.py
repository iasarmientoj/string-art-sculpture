import numpy as np
from PIL import Image, ImageDraw
import time
import math

# Parameters
idImage=10
input_image = f"sections-export/seccion_{idImage}.png"  # Input cross-sectional image
output_image = f"sections-export/seccion_{idImage}_string_art.png"  # Output string art image
output_sequence = f"sections-export/seccion_{idImage}_string_art.txt"  # Output sequence file
points_per_side = 25  # Number of points per side (400 total)
num_jumps = 400  # Increased number of thread jumps for better detail
subtract_intensity = 100  # Increased intensity to subtract per thread pass
min_distance = 50  # Minimum distance (pixels) between points for jumps
line_width = 1  # Width of lines in output image
image_size = 1182  # Image dimensions (512x512 pixels)

# Generate equidistant points along the square border
def generate_points(points_per_side, image_size):
    points = []
    step = image_size / points_per_side  # Distance between points
    
    # Top side (x varies, y = 0)
    for i in range(points_per_side):
        points.append((i * step, 0))
    # Right side (x = image_size, y varies)
    for i in range(points_per_side):
        points.append((image_size - 1, i * step))
    # Bottom side (x varies, y = image_size)
    # for i in range(points_per_side):
        # points.append(((points_per_side - 1 - i) * step, image_size - 1))
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

# Main string art algorithm
def generate_string_art():
    # Load and process the input image
    img = Image.open(input_image).convert("L")  # Convert to grayscale
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
            print(f"Parando en salto {jump}: no se encontraron puntos válidos.")
            break
        
        # Draw the line on the output image (invert Y-axis for PIL)
        p1 = points[current_point]
        p2 = points[best_point]
        draw.line((p1[0], p1[1], p2[0], p2[1]), fill=0, width=line_width)
        
        # Subtract intensity from the image array
        subtract_line(img_array, best_pixels)
        
        # Update the current point and sequence
        current_point = best_point
        sequence.append(current_point + 1)  # 1-based index
    
    # Save the output image
    output_img.save(output_image)
    
    # Save the sequence of points
    with open(output_sequence, "w") as f:
        f.write("Secuencia de puntos (1-based):\n")
        f.write(" -> ".join(map(str, sequence)))
    
    # Print statistics
    print(f"Completado {len(sequence)-1} saltos en {time.time() - start_time:.2f} segundos.")
    print(f"Imagen guardada en: {output_image}")
    print(f"Secuencia guardada en: {output_sequence}")

if __name__ == "__main__":
    generate_string_art()