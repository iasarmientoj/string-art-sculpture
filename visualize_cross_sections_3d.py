import platform as py_platform
import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import os
import numpy as np

# Parameters
folder_name = "string-sections-statue"  # Default folder name
# folder_name = "sections-export"  # Default folder name

z_separation = 0.5  # Separation between sections on the Z-axis
x_limits = (-650, 650)  # X-axis limits (will be scaled)
y_limits = (-650, 650)  # Y-axis limits (will be scaled)
scale_factor = 100.0  # Scale down the model size
alpha = 0.9  # Overall opacity of images (1.0 since transparency is handled per pixel)
white_threshold = 200  # Threshold for pixels to be considered white (stricter to avoid affecting hilos)

# Initialize Pygame and OpenGL
pygame.init()
display = (800, 600)
pygame.display.set_mode(display, DOUBLEBUF | OPENGL)
gluPerspective(45, (display[0] / display[1]), 0.1, 500.0)
glTranslatef(0.0, 0.0, -20.0)  # Initial camera position

# Configure OpenGL
glEnable(GL_TEXTURE_2D)
glEnable(GL_BLEND)
glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
glClearColor(1.0, 1.0, 1.0, 1.0)  # Set background to white
glDisable(GL_CULL_FACE)  # Disable back-face culling to render both sides of quads

# Count the number of PNG files in the folder and load textures
textures = []
if os.path.exists(folder_name):
    # Get list of PNG files in the folder
    image_files = [f for f in os.listdir(folder_name) if f.endswith('.png')]
    num_sections = len(image_files)
    for i, img_file in enumerate(sorted(image_files), 1):  # Sort to ensure consistent order
        img_path = os.path.join(folder_name, img_file)
        try:
            surface = pygame.image.load(img_path)
            # Convert surface to RGBA array
            img_data = pygame.surfarray.array3d(surface)
            alpha_data = np.ones((img_data.shape[0], img_data.shape[1]), dtype=np.uint8) * 255
            # Set alpha to 0 for nearly white pixels (stricter threshold)
            white_mask = (img_data[:, :, 0] >= white_threshold) & (img_data[:, :, 1] >= white_threshold) & (img_data[:, :, 2] >= white_threshold)
            alpha_data[white_mask] = 0
            # Combine RGB and alpha into RGBA
            rgba_data = np.dstack((img_data, alpha_data))
            # Convert back to raw data for OpenGL
            data = rgba_data.tobytes()
            width, height = surface.get_size()
            
            texture_id = glGenTextures(1)
            glBindTexture(GL_TEXTURE_2D, texture_id)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
            glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, width, height, 0, GL_RGBA, GL_UNSIGNED_BYTE, data)
            textures.append((texture_id, width, height, i * z_separation))  # Store z-position
        except Exception as e:
            print(f"Error loading {img_path}: {e}")
    else:
        textures.append(None)
else:
    print(f"Folder {folder_name} does not exist.")
    num_sections = 0

# Variables for interaction
angle_x, angle_y = -90, 0  # Initial rotation to align Z with screen Y
trans_x, trans_y, trans_z = 0, -10, -20.0  # Adjusted camera translation
last_pos_left = None  # For rotation (left mouse button)
last_pos_right = None  # For translation (right mouse button)

def update_loop():
    global angle_x, angle_y, trans_x, trans_y, trans_z, last_pos_left, last_pos_right
    
    for event in pygame.event.get():
        if event.type == QUIT:
            return False  # Signal to exit the loop
        elif event.type == MOUSEBUTTONDOWN:
            if event.button == 1:  # Left button for rotation
                last_pos_left = pygame.mouse.get_pos()
            elif event.button == 3:  # Right button for translation
                last_pos_right = pygame.mouse.get_pos()
        elif event.type == MOUSEBUTTONUP:
            if event.button == 1:
                last_pos_left = None
            elif event.button == 3:
                last_pos_right = None
        elif event.type == MOUSEMOTION:
            x, y = pygame.mouse.get_pos()
            if last_pos_left:  # Rotate
                dx, dy = x - last_pos_left[0], y - last_pos_left[1]
                angle_x += dy * 0.5
                angle_y += dx * 0.5
                last_pos_left = (x, y)
            if last_pos_right:  # Translate
                dx, dy = x - last_pos_right[0], y - last_pos_right[1]
                trans_x += dx * 0.01
                trans_y -= dy * 0.01  # Invert Y for intuitive movement
                last_pos_right = (x, y)
        elif event.type == MOUSEWHEEL:  # Zoom
            trans_z += event.y * 0.5  # Positive for zoom in, negative for zoom out
            trans_z = max(-100.0, min(-1.0, trans_z))  # Limit zoom range
    
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glPushMatrix()
    glTranslatef(trans_x, trans_y, trans_z)
    glRotatef(angle_x, 1, 0, 0)
    glRotatef(angle_y, 0, 0, 1)
    
    # Sort textures by z-position (nearest to farthest for correct transparency)
    valid_textures = [(t[3], t) for t in textures if t is not None]
    valid_textures.sort(reverse=False)  # Nearest to farthest (last to first)
    
    # Render quads with transparency handling
    glDisable(GL_DEPTH_TEST)  # Disable depth test to prevent occlusion of transparent layers
    for z, texture_info in valid_textures:
        texture_id, width, height, _ = texture_info
        
        glBindTexture(GL_TEXTURE_2D, texture_id)
        glBegin(GL_QUADS)
        glColor4f(1.0, 1.0, 1.0, alpha)
        # Define vertices in clockwise order to ensure front face is upward
        glTexCoord2f(0, 0); glVertex3f(x_limits[0]/scale_factor, y_limits[0]/scale_factor, z)
        glTexCoord2f(0, 1); glVertex3f(x_limits[0]/scale_factor, y_limits[1]/scale_factor, z)
        glTexCoord2f(1, 1); glVertex3f(x_limits[1]/scale_factor, y_limits[1]/scale_factor, z)
        glTexCoord2f(1, 0); glVertex3f(x_limits[1]/scale_factor, y_limits[0]/scale_factor, z)
        glEnd()
    
    glPopMatrix()
    pygame.display.flip()
    return True  # Continue the loop

def main():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    
    if py_platform.system() == "Emscripten":
        # Code for Pyodide (keep asyncio)
        import asyncio
        async def pyodide_main():
            while True:
                if not update_loop():
                    break
                await asyncio.sleep(1.0 / 60)
        asyncio.ensure_future(pyodide_main())
    else:
        # Synchronous loop for desktop environments
        running = True
        while running:
            running = update_loop()
            pygame.time.Clock().tick(60)  # Limit to 60 FPS

if __name__ == "__main__":
    main()
    pygame.quit()