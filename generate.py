import numpy as np
import matplotlib.image as mpimg
import matplotlib.pyplot as plt
from skimage.draw import line_aa, ellipse_perimeter
from math import atan2
from skimage.transform import resize
from time import time
import pathlib
import os


# Directorios de entrada y salida
input_dir = pathlib.Path('sections-export')
output_dir = pathlib.Path('string-sections')
instructions_file = 'instructions.txt'


def rgb2gray(rgb):
    return np.dot(rgb[...,:3], [0.2989, 0.5870, 0.1140])

def largest_square(image: np.ndarray) -> np.ndarray:
    short_edge = np.argmin(image.shape[:2])  # 0 = vertical <= horizontal; 1 = otherwise
    short_edge_half = image.shape[short_edge] // 2
    long_edge_center = image.shape[1 - short_edge] // 2
    if short_edge == 0:
        return image[:, long_edge_center - short_edge_half:long_edge_center + short_edge_half]
    if short_edge == 1:
        return image[long_edge_center - short_edge_half:long_edge_center + short_edge_half, :]

def create_rectangle_nail_positions(shape, nail_step=2):
    height, width = shape

    nails_top = [(0, i) for i in range(0, width, nail_step)]
    nails_bot = [(height-1, i) for i in range(0, width, nail_step)]
    nails_right = [(i, width-1) for i in range(1, height-1, nail_step)]
    nails_left = [(i, 0) for i in range(1, height-1, nail_step)]
    nails = nails_top + nails_right + nails_bot + nails_left

    return np.array(nails)

def create_circle_nail_positions(shape, nail_step=2, r1_multip=1, r2_multip=1):
    height = shape[0]
    width = shape[1]

    centre = (height // 2, width // 2)
    radius = min(height, width) // 2 - 1
    rr, cc = ellipse_perimeter(centre[0], centre[1], int(radius*r1_multip), int(radius*r2_multip))
    nails = list(set([(rr[i], cc[i]) for i in range(len(cc))]))
    nails.sort(key=lambda c: atan2(c[0] - centre[0], c[1] - centre[1]))
    nails = nails[::nail_step]

    return np.asarray(nails)

def init_canvas(shape, black=False):
    if black:
        return np.zeros(shape)
    else:
        return np.ones(shape)

def get_aa_line(from_pos, to_pos, str_strength, picture):
    rr, cc, val = line_aa(from_pos[0], from_pos[1], to_pos[0], to_pos[1])
    line = picture[rr, cc] + str_strength * val
    line = np.clip(line, a_min=0, a_max=1)

    return line, rr, cc

def find_best_nail_position(current_idx, nails, str_pic, orig_pic, str_strength, random_nails=None):
    best_cumulative_improvement = -99999
    best_nail_position = None
    best_nail_idx = None
    best_start_idx = None
    
    # Determinar las puntillas adyacentes (idx-1 e idx+1), manejando los bordes
    adjacent_indices = []
    if current_idx > 0:
        adjacent_indices.append(current_idx - 1)  # Adyacente izquierdo
    if current_idx < len(nails) - 1:
        adjacent_indices.append(current_idx + 1)  # Adyacente derecho
    
    # Evaluar cada puntilla adyacente como punto de partida
    for start_idx in adjacent_indices:
        start_position = nails[start_idx]
        
        # Seleccionar puntillas destino (excluyendo la misma y sus adyacentes)
        if random_nails is not None:
            nail_ids = np.random.choice(range(len(nails)), size=random_nails, replace=False)
            nail_ids = [i for i in nail_ids if i not in [start_idx, start_idx-1, start_idx+1]]
            nails_and_ids = list(zip(nail_ids, nails[nail_ids]))
        else:
            nails_and_ids = [(i, nail) for i, nail in enumerate(nails) 
                            if i not in [start_idx, start_idx-1, start_idx+1]]

        for nail_idx, nail_position in nails_and_ids:
            overlayed_line, rr, cc = get_aa_line(start_position, nail_position, str_strength, str_pic)

            before_overlayed_line_diff = np.abs(str_pic[rr, cc] - orig_pic[rr, cc])**2
            after_overlayed_line_diff = np.abs(overlayed_line - orig_pic[rr, cc])**2

            cumulative_improvement = np.sum(before_overlayed_line_diff - after_overlayed_line_diff)

            if cumulative_improvement >= best_cumulative_improvement:
                best_cumulative_improvement = cumulative_improvement
                best_nail_position = nail_position
                best_nail_idx = nail_idx
                best_start_idx = start_idx

    return best_start_idx, best_nail_idx, best_nail_position, best_cumulative_improvement

def create_art(nails, orig_pic, str_pic, str_strength, i_limit=None, last_nail_idx=0):
    start = time()
    iter_times = []

    # Elegir la ranura inicial como una adyacente a last_nail_idx
    adjacent_indices = []
    if last_nail_idx > 0:
        adjacent_indices.append(last_nail_idx - 1)
    if last_nail_idx < len(nails) - 1:
        adjacent_indices.append(last_nail_idx + 1)
    
    # Evaluar cuál adyacente es mejor como punto de partida para el primer hilo
    best_start_idx = adjacent_indices[0]  # Por defecto, el primero disponible
    best_initial_improvement = -99999
    best_first_nail_idx = None
    best_first_nail_position = None
    
    for start_idx in adjacent_indices:
        start_position = nails[start_idx]
        # Evaluar el mejor destino para el primer hilo
        _, temp_nail_idx, temp_nail_position, temp_improvement = find_best_nail_position(
            start_idx, nails, str_pic, orig_pic, str_strength)
        if temp_improvement > best_initial_improvement:
            best_initial_improvement = temp_improvement
            best_start_idx = start_idx
            best_first_nail_idx = temp_nail_idx
            best_first_nail_position = temp_nail_position

    # Iniciar el pull_order con la ranura inicial y el primer destino
    current_idx = best_start_idx
    pull_order = [best_start_idx]
    
    # Dibujar el primer hilo desde best_start_idx a best_first_nail_idx
    if best_first_nail_idx is not None:
        best_overlayed_line, rr, cc = get_aa_line(
            nails[best_start_idx], best_first_nail_position, str_strength, str_pic)
        str_pic[rr, cc] = best_overlayed_line
        pull_order.append(best_first_nail_idx)
        current_idx = best_first_nail_idx

    i = 0
    fails = 0
    while True:
        start_iter = time()

        i += 1
        
        if i % 500 == 0:
            print(f"Iteration {i}")
        
        if i_limit is None:
            if fails >= 3:
                break
        else:
            if i > i_limit:
                break

        start_idx, best_nail_idx, best_nail_position, best_cumulative_improvement = find_best_nail_position(
            current_idx, nails, str_pic, orig_pic, str_strength)

        if best_cumulative_improvement <= 0:
            fails += 1
            continue

        pull_order.append(start_idx)
        pull_order.append(best_nail_idx)
        
        best_overlayed_line, rr, cc = get_aa_line(nails[start_idx], best_nail_position, str_strength, str_pic)
        str_pic[rr, cc] = best_overlayed_line

        current_idx = best_nail_idx
        iter_times.append(time() - start_iter)

    print(f"Time: {time() - start}")
    print(f"Avg iteration time: {np.mean(iter_times)}")
    return pull_order

def scale_nails(x_ratio, y_ratio, nails):
    return [(int(y_ratio*nail[0]), int(x_ratio*nail[1])) for nail in nails]

def pull_order_to_array_bw(order, canvas, nails, strength):
    for pull_start, pull_end in zip(order, order[1:]):
        rr, cc, val = line_aa(nails[pull_start][0], nails[pull_start][1],
                              nails[pull_end][0], nails[pull_end][1])
        canvas[rr, cc] += val * strength

    return np.clip(canvas, a_min=0, a_max=1)

def pull_order_to_array_rgb(orders, canvas, nails, colors, strength):
    color_order_iterators = [iter(zip(order, order[1:])) for order in orders]
    for _ in range(len(orders[0]) - 1):
        for color_idx, iterator in enumerate(color_order_iterators):
            pull_start, pull_end = next(iterator)
            rr_aa, cc_aa, val_aa = line_aa(
                nails[pull_start][0], nails[pull_start][1],
                nails[pull_end][0], nails[pull_end][1]
            )

            val_aa_colored = np.zeros((val_aa.shape[0], len(colors)))
            for idx in range(len(val_aa)):
                val_aa_colored[idx] = np.full(len(colors), val_aa[idx])

            canvas[rr_aa, cc_aa] += colors[color_idx] * val_aa_colored * strength

    return np.clip(canvas, a_min=0, a_max=1)

if __name__ == '__main__':
    # Parámetros fijos
    LONG_SIDE = 300
    SIDE_LEN = 800
    NAIL_STEP = 10
    EXPORT_STRENGTH = 0.18
    RECT = True
    WB = False
    RGB = False
    PULL_AMOUNT = None
    RANDOM_NAILS = None
    RADIUS1_MULTIPLIER = 1.0
    RADIUS2_MULTIPLIER = 1.0

    # Crear la carpeta de salida si no existe
    output_dir.mkdir(exist_ok=True)

    # Inicializar la última ranura como 0 para la primera imagen
    last_nail_idx = 0

    # Abrir el archivo de instrucciones
    with open(instructions_file,'a') as f:
        f.write("Instructions:\n\n")


        # Procesar todas las imágenes en la carpeta sections-export
        for input_file in sorted(input_dir.glob('seccion_*.png')):
            print(f"Processing {input_file.name}...")
            f.write(f"{input_file.name}\n")
            
            # Ruta de salida (mismo nombre en string-sections)
            output_file = output_dir / input_file.name
	    
            # Leer la imagen
            img = mpimg.imread(str(input_file))
            
            if np.any(img > 100):
                img = img / 255
            
            if RADIUS1_MULTIPLIER == 1 and RADIUS2_MULTIPLIER == 1:
                img = largest_square(img)
                img = resize(img, (LONG_SIDE, LONG_SIDE))
	    
            shape = (len(img), len(img[0]))
	    
            if RECT:
                nails = create_rectangle_nail_positions(shape, NAIL_STEP)
            else:
                nails = create_circle_nail_positions(shape, NAIL_STEP, RADIUS1_MULTIPLIER, RADIUS2_MULTIPLIER)
	    
            print(f"Nails amount: {len(nails)}")
            
            if RGB:
                iteration_strength = 0.1 if WB else -0.1
	    
                r = img[:,:,0]
                g = img[:,:,1]
                b = img[:,:,2]
                
                str_pic_r = init_canvas(shape, black=WB)
                pull_orders_r = create_art(nails, r, str_pic_r, iteration_strength, i_limit=PULL_AMOUNT, last_nail_idx=last_nail_idx)
	    
                str_pic_g = init_canvas(shape, black=WB)
                pull_orders_g = create_art(nails, g, str_pic_g, iteration_strength, i_limit=PULL_AMOUNT, last_nail_idx=last_nail_idx)
	    
                str_pic_b = init_canvas(shape, black=WB)
                pull_orders_b = create_art(nails, b, str_pic_b, iteration_strength, i_limit=PULL_AMOUNT, last_nail_idx=last_nail_idx)
	    
                max_pulls = np.max([len(pull_orders_r), len(pull_orders_g), len(pull_orders_b)])
                pull_orders_r = pull_orders_r + [pull_orders_r[-1]] * (max_pulls - len(pull_orders_r))
                pull_orders_g = pull_orders_g + [pull_orders_g[-1]] * (max_pulls - len(pull_orders_g))
                pull_orders_b = pull_orders_b + [pull_orders_b[-1]] * (max_pulls - len(pull_orders_b))
	    
                pull_orders = [pull_orders_r, pull_orders_g, pull_orders_b]
	    
                color_image_dimens = int(SIDE_LEN * RADIUS1_MULTIPLIER), int(SIDE_LEN * RADIUS2_MULTIPLIER), 3
                print(color_image_dimens)
                blank = init_canvas(color_image_dimens, black=WB)
	    
                scaled_nails = scale_nails(
                    color_image_dimens[1] / shape[1],
                    color_image_dimens[0] / shape[0],
                    nails
                )
	    
                result = pull_order_to_array_rgb(
                    pull_orders,
                    blank,
                    scaled_nails,
                    (np.array((1., 0., 0.,)), np.array((0., 1., 0.,)), np.array((0., 0., 1.,))),
                    EXPORT_STRENGTH if WB else -EXPORT_STRENGTH
                )
                mpimg.imsave(str(output_file), result, cmap=plt.get_cmap("gray"), vmin=0.0, vmax=1.0)
	    
            else:
                orig_pic = rgb2gray(img) * 0.9
                
                image_dimens = int(SIDE_LEN * RADIUS1_MULTIPLIER), int(SIDE_LEN * RADIUS2_MULTIPLIER)
                if WB:
                    str_pic = init_canvas(shape, black=True)
                    pull_order = create_art(nails, orig_pic, str_pic, 0.05, i_limit=PULL_AMOUNT, last_nail_idx=last_nail_idx)
                    blank = init_canvas(image_dimens, black=True)
                else:
                    str_pic = init_canvas(shape, black=False)
                    pull_order = create_art(nails, orig_pic, str_pic, -0.05, i_limit=PULL_AMOUNT, last_nail_idx=last_nail_idx)
                    blank = init_canvas(image_dimens, black=False)
	    
                scaled_nails = scale_nails(
                    image_dimens[1] / shape[1],
                    image_dimens[0] / shape[0],
                    nails
                )
	    
                result = pull_order_to_array_bw(
                    pull_order,
                    blank,
                    scaled_nails,
                    EXPORT_STRENGTH if WB else -EXPORT_STRENGTH
                )
                mpimg.imsave(str(output_file), result, cmap=plt.get_cmap("gray"), vmin=0.0, vmax=1.0)
	    
                print(f"Thread pull order by nail index for {input_file.name}:\n{'-'.join([str(idx) for idx in pull_order])}")
            # Escribir en instructions.txt
            f.write(f"{'-'.join([str(idx) for idx in pull_order])}\n\n")
            
            # Actualizar last_nail_idx con la última ranura de la sección actual
            last_nail_idx = pull_order[-1]
            print(f"Saved to {output_file}")