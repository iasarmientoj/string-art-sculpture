import trimesh
import numpy as np
import matplotlib.pyplot as plt

# Carga el modelo
mesh = trimesh.load('model/model.stl')

# Parámetros
num_sections = 100
rotation_angle = 45  # Ángulo de rotación en grados alrededor del eje Z (vertical)
z_min, z_max = mesh.bounds[0][2], mesh.bounds[1][2]
z_positions = np.linspace(z_min, z_max, num_sections)

# Aplica rotación al modelo en el eje Z
rotation_matrix = trimesh.transformations.rotation_matrix(
    angle=np.deg2rad(rotation_angle),  # Convierte a radianes
    direction=[0, 0, 1],              # Rotación en eje Z
    point=[0, 0, 0]                   # Rota alrededor del origen (0, 0, 0)
)
mesh.apply_transform(rotation_matrix)

# Configura el tamaño de la imagen y los límites de los ejes
plt.rcParams['figure.figsize'] = [15.36,15.36]  # Proporción cuadrada para 512x512 píxeles
x_limits = (-800, 500)
y_limits = (-650, 650)

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
            # Extrae los vértices del polígono
            polygon = vertices_2d[points_idx]
            # Rellena el polígono
            plt.fill(polygon[:, 0], polygon[:, 1], 'k')  # 'k' para negro
        plt.axis('equal')
        plt.xlim(x_limits)
        plt.ylim(y_limits)
        plt.gca().set_aspect('equal', adjustable='box')
        plt.axis('off')  # Oculta los ejes y el recuadro
        plt.savefig(f'sections-export/seccion_{i}.png', dpi=100, bbox_inches='tight', pad_inches=0)  # 512x512 píxeles
        plt.close()