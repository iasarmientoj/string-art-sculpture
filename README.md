# String Art Sculpture

![Example](/assets/example.png "Example")

## Descripción
**String Art Sculpture** es un proyecto basado en Python para procesar modelos 3D en formato STL y generar secciones transversales que sirvan como guía para crear esculturas en *string art*. El proyecto incluye scripts para cortar un modelo 3D en imágenes 2D, rellenar los contornos para simular los hilos del *string art*, y visualizar las secciones en un entorno 3D interactivo. Este proyecto es ideal para artistas, diseñadores y entusiastas del *string art* que deseen planificar esculturas tridimensionales basadas en modelos digitales.

## Estructura de Carpetas
El proyecto está organizado de la siguiente manera:
```
main/
├── model/
│   └── model.stl           # Modelo 3D en formato STL
├── sections-export/
│   └── seccion_1.png       # Imágenes de secciones generadas y consumidas
│   └── seccion_2.png
│   └── ...
│   └── seccion_98.png
├── cut-model.py            # Script para generar imágenes de secciones
├── cut-model-fill.py       # Script para rellenar contornos de secciones
└── visualize_cross_sections_3d.py  # Script para visualizar secciones en 3D
```

- **`main/`**: Directorio raíz que contiene los scripts y subcarpetas.
- **`model/`**: Almacena el modelo STL de entrada (`model.stl`).
- **`sections-export/`**: Contiene las imágenes de secciones transversales (`seccion_1.png` a `seccion_98.png`) generadas por `cut-model.py` y `cut-model-fill.py`, y consumidas por `visualize_cross_sections_3d.py`.

## Documentación de Scripts

### 1. `cut-model.py`
**Propósito**: Corta un modelo 3D STL en imágenes 2D de secciones transversales para *string art*.

**Funcionalidad**:
- Lee un modelo STL desde `model/model.stl`.
- Divide el modelo en 98 planos equidistantes a lo largo del eje Z.
- Genera imágenes PNG con contornos negros sobre fondo blanco, representando las intersecciones del modelo con cada plano, que sirven como guías para los hilos del *string art*.
- Guarda las imágenes como `seccion_1.png` a `seccion_98.png` en la carpeta `sections-export/`.

**Dependencias**:
- Bibliotecas de Python: `numpy`, `trimesh`, `matplotlib`, `PIL`.
- Instalar dependencias:
  ```bash
  pip install numpy trimesh matplotlib pillow
  ```

**Uso**:
```bash
cd main
python cut-model.py
```

**Salida**:
- 98 imágenes PNG (`seccion_1.png` a `seccion_98.png`) en `sections-export/`.

---

### 2. `cut-model-fill.py`
**Propósito**: Procesa las imágenes de secciones para rellenar los contornos, simulando las regiones cubiertas por hilos en *string art*.

**Funcionalidad**:
- Carga las imágenes de secciones (`seccion_1.png` a `seccion_98.png`) desde `sections-export/`.
- Aplica técnicas de procesamiento de imágenes para rellenar los contornos negros, creando regiones sólidas negras sobre fondo blanco.
- Guarda las imágenes rellenadas en `sections-export/`, sobrescribiendo los archivos originales.

**Dependencias**:
- Bibliotecas de Python: `numpy`, `PIL`, `scipy` (para procesamiento de imágenes).
- Instalar dependencias:
  ```bash
  pip install numpy pillow scipy
  ```

**Uso**:
```bash
cd main
python cut-model-fill.py
```

**Salida**:
- Imágenes PNG actualizadas (`seccion_1.png` a `seccion_98.png`) en `sections-export/` con contornos rellenados.

---

### 3. `visualize_cross_sections_3d.py`
**Propósito**: Visualiza las secciones transversales como una pila 3D interactiva para planificar la escultura en *string art*.

**Funcionalidad**:
- Carga 98 imágenes de secciones (`seccion_1.png` a `seccion_98.png`) desde `sections-export/`.
- Renderiza las imágenes como planos texturizados apilados a lo largo del eje Z en un entorno 3D usando OpenGL.
- Procesa las imágenes para hacer el fondo blanco transparente, mostrando solo las regiones negras rellenadas (representando los hilos del *string art*).
- Ofrece controles interactivos:
  - **Rotar**: Arrastrar con el botón izquierdo del ratón.
  - **Trasladar**: Arrastrar con el botón derecho del ratón.
  - **Zoom**: Desplazar la rueda del ratón.
- Muestra la escena con un fondo blanco, y las secciones son visibles desde todos los ángulos (arriba y abajo) con un manejo correcto de la transparencia.

**Dependencias**:
- Bibliotecas de Python: `pygame`, `PyOpenGL`, `numpy`.
- Instalar dependencias:
  ```bash
  pip install pygame PyOpenGL numpy
  ```

**Uso**:
```bash
cd main
python visualize_cross_sections_3d.py
```

**Salida**:
- Una ventana interactiva de visualización 3D que muestra las secciones apiladas.

**Notas**:
- Asegúrate de que las 98 imágenes estén presentes en `sections-export/` antes de ejecutar.
- El script asume que las imágenes tienen un fondo blanco (RGB: 255, 255, 255) y regiones negras rellenadas.

## Configuración e Instalación
1. Clona el repositorio:
   ```bash
   git clone https://github.com/<tu-usuario>/string-art-sculpture.git
   cd string-art-sculpture
   ```
2. Instala las dependencias:
   ```bash
   pip install numpy trimesh matplotlib pillow scipy pygame PyOpenGL
   ```
3. Coloca el modelo STL en `main/model/model.stl`.
4. Ejecuta los scripts en orden:
   ```bash
   python cut-model.py
   python cut-model-fill.py
   python visualize_cross_sections_3d.py
   ```

## Requisitos
- Python 3.11 o superior.
- Una GPU que soporte OpenGL para una visualización 3D fluida.
- Modelo STL de entrada (`model.stl`) en `main/model/`.

## Licencia
Este proyecto está licenciado bajo la Licencia MIT. Consulta el archivo `LICENSE` para más detalles.

## Contribuciones
¡Las contribuciones son bienvenidas! Por favor, envía un *pull request* o abre un *issue* en GitHub para sugerencias o reportes de errores.