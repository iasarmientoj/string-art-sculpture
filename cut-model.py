import trimesh
import numpy as np
import matplotlib.pyplot as plt
import os

# model statue
mesh = trimesh.load('model/model-statue.stl') # Carga el modelo
num_sections = 42 + 2
rotation_angle = 45 # Ángulo de rotación en grados alrededor del eje Z (vertical)
z_min, z_max = mesh.bounds[0][2], mesh.bounds[1][2] #eje z
directionParam = [0, 0, 1]
x_limits = (-800, 500)
y_limits = (-650, 650)

# model ballet
mesh = trimesh.load('model/model-ballet.stl') # Carga el modelo
num_sections = 30 + 2
rotation_angle = 90 # Ángulo de rotación en grados alrededor del eje Z (vertical)
z_min, z_max = mesh.bounds[0][1], mesh.bounds[1][1] #eje z
directionParam = [1, 0, 0]
x_limits = (-1, 1)
y_limits = (-1, 1)

# model octopus
mesh = trimesh.load('model/model-octopus.stl') # Carga el modelo
num_sections = 15 + 2
rotation_angle = -90 # Ángulo de rotación en grados alrededor del eje Z (vertical)
z_min, z_max = mesh.bounds[0][2], mesh.bounds[1][2] #eje z
directionParam = [0, 0, 1]
x_limits = (-12-5, 12-5)
y_limits = (-12+3, 12+3)

# model deer
mesh = trimesh.load('model/model-deer.stl') # Carga el modelo
num_sections = 30 + 2
rotation_angle = -90 # Ángulo de rotación en grados alrededor del eje Z (vertical)
z_min, z_max = mesh.bounds[0][2], mesh.bounds[1][2] #eje z
directionParam = [0, 0, 1]
x_limits = (-12+0, 12+0)
y_limits = (-12-5, 12-5)

# model apple
mesh = trimesh.load('model/model-apple.stl') # Carga el modelo
num_sections = 20 + 2
rotation_angle = 0 # Ángulo de rotación en grados alrededor del eje Z (vertical)
z_min, z_max = mesh.bounds[0][2], mesh.bounds[1][2] #eje z
directionParam = [0, 0, 1]
x_limits = (-400+0, 400+0)
y_limits = (-400-0, 400-0)

# Parámetros
line_width = 10.0    # Ancho del contorno en píxeles (ajusta según necesidad)
z_positions = np.linspace(z_min, z_max, num_sections)

# Aplica rotación al modelo en el eje Z
rotation_matrix = trimesh.transformations.rotation_matrix(
    angle=np.deg2rad(rotation_angle),  # Convierte a radianes
    direction=directionParam,              # Rotación en eje Z
    point=[0, 0, 0]                   # Rota alrededor del origen (0, 0, 0)
)
mesh.apply_transform(rotation_matrix)

# Configura el tamaño de la imagen y los límites de los ejes
plt.rcParams['figure.figsize'] = [15.36,15.36]  # Proporción cuadrada para 512x512 píxeles

# Crea el directorio sections-export si no existe
output_dir = 'sections-export'
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# Genera secciones transversales
for i, z in enumerate(z_positions):
    # Define el plano de corte en el sistema de coordenadas global
    section = mesh.section(plane_origin=[0, 0, z], plane_normal=[0, 0, 1])
    if section:
        # Extrae los vértices y entidades de la sección
        vertices_3d = section.vertices
        entities = section.entities
        # Proyecta manualmente al plano XY (ignora Z)
        vertices_2d = vertices_3d[:, :2]  # Toma solo X e Y
        # Dibuja la sección
        plt.figure()
        for entity in entities:
            # Obtiene los índices de los vértices para esta entidad
            points_idx = entity.points
            # Dibuja las líneas conectando los vértices
            for j in range(len(points_idx)):
                start_idx = points_idx[j]
                end_idx = points_idx[(j + 1) % len(points_idx)]  # Cierra el bucle
                start_point = vertices_2d[start_idx]
                end_point = vertices_2d[end_idx]
                plt.plot([start_point[0], end_point[0]], [start_point[1], end_point[1]], 'k-', linewidth=line_width)
        plt.axis('equal')
        plt.xlim(x_limits)
        plt.ylim(y_limits)
        plt.gca().set_aspect('equal', adjustable='box')
        plt.axis('off')  # Oculta los ejes y el recuadro
        plt.savefig(f'{output_dir}/seccion_{i:03d}.png', dpi=100, bbox_inches='tight', pad_inches=0)  # 512x512 píxeles
        plt.close()