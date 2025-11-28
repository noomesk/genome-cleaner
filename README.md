# Genome Cleaner

![Genome Cleaner Logo](https://img.shields.io/badge/Genome-Cleaner-brightgreen?style=for-the-badge&logo=DNA)

Esta es una aplicación profesional para limpieza y validación de secuencias FASTA/FASTQ desarrollada con Streamlit.

## 📋 Descripción del Proyecto

Genome Cleaner es una herramienta integral diseñada para bioinformáticos que necesitan procesar y validar grandes volúmenes de datos de secuencias. La aplicación combina una interfaz web intuitiva (responsive) con capacidades de línea de comandos para ofrecer flexibilidad máxima en el procesamiento de datos genómicos.

### Características Principales de la app

- **Limpieza Automática**: Detección y corrección automática de caracteres inválidos
- **Validación Completa**: Verificación de headers duplicados, secuencias vacías y caracteres sospechosos
- **Análisis Estadístico**: Cálculo automático de contenido GC, distribuciones de longitud y métricas clave
- **Visualización Interactiva**: Gráficos responsive con Plotly para análisis exploratorio
- **Interfaz Responsive**: Diseño adaptable a dispositivos móviles y tablets
- **Exportación Múltiple**: Descarga de informes en CSV y JSON
- **Línea de Comandos**: CLI completa para automatización de procesos

## Instalacióoooooon

### Prerrequisitos

- Python 3.8 o superior
- pip (gestor de paquetes de Python)

### Pasos de Instalación

1. **Clona o descarga el proyecto**:
```bash
git clone https://github.com/tu-usuario/genome-cleaner.git
cd genome-cleaner
```

2. **Instala las dependencias**:
```bash
pip install -r requirements.txt
```

## Uso de la Interfaz Web (Streamlit)

1. **Ejecuta la aplicación**:
```bash
streamlit run app.py
```

2. **Accede a la interfaz**: Abre el navegador web y ve a `http://localhost:8501`

3. **Sube tus archivos**: Arrastra y suelta archivos FASTA/FASTQ en la barra lateral

4. **Configura las opciones**:
   - **Modo de sanitización**: Define cómo tratar caracteres inválidos
   - **Umbral de longitud mínima**: Configura la longitud mínima aceptable (default: 20 pb)

5. **Explora los resultados** en las pestañas:
   - **Resumen**: Métricas clave del dataset
   - **Limpieza y Validación**: Tabla detallada de todas las secuencias
   - **Gráficos**: Análisis visual interactivo
   - **Informes**: Descarga de resultados

### Capturas de Pantalla

*[Aquí irían las capturas de pantalla de la interfaz juju]*

## Uso de la Línea de Comandos

### Comandos Básicos

```bash
# Validación simple
python -m src.cli --input mis_secuencias.fasta

# Pa limpieza y sanitización
python -m src.cli --input mis_secuencias.fasta --sanitize --output resultado_limpio.fasta

# Con umbral personalizado
python -m src.cli --input mis_secuencias.fasta --min-length 50

# Generar informe JSON
python -m src.cli --input mis_secuencias.fasta --report --format json

# Para mostrar ayuda
python -m src.cli --help
```

### Parámetros Disponibles

- `--input`: Archivo FASTA/FASTQ de entrada (requerido)
- `--sanitize`: Habilita el modo de sanitización
- `--min-length`: Longitud mínima de secuencia (default: 20)
- `--output`: Archivo de salida para secuencias limpiadas
- `--report`: Genera archivo de informe
- `--format`: Formato del informe (csv/json)
- `--verbose`: Salida detallada

## Tipos de Archivos Soportados por la app

### FASTA
```
>seq1_name_description
ACGTACGTACGTACGT
>seq2_name_description
TTAAGGCCATCGATCG
```

### FASTQ
```
@seq1_name_description
ACGTACGTACGTACGT
+
IIIIIIIIIIIIIIII
@seq2_name_description
TTAAGGCCATCGATCG
+
TTTTTTTTTTTTTTTT
```

## Validaciones necesarias

- **Caracteres válidos**: Solo A, C, G, T, N (y minúsculas)
- **Headers únicos**: Detección de duplicados
- **Secuencias vacías**: Filtrado automático
- **Longitud mínima**: Umbral configurable
- **Formato correcto**: Verificación de estructura FASTA/FASTQ

## Métricas Calculadas

- Total de secuencias procesadas
- Número de secuencias válidas y o inválidas
- Porcentaje de contenido GC promedio
- Longitudes máxima, mínima y promedio
- Top 10 secuencias más largas
- Distribución de errores por tipo de error

## Testing

```bash
# Ejecutar todos los tests con
pytest

# Tests específicos para c/u
pytest tests/test_parser.py
pytest tests/test_validator.py
pytest tests/test_stats.py

# Con cobertura de códigooo
pytest --cov=src tests/
```

## Estructura del Proyecto

```
genome-cleaner/
├── app.py                 # Interfaz principal de Streamlit (front/back)
├── requirements.txt       # Dependencias del proyecto (crear máquina virtual para optimizar recursos)
├── README.md             # Documentación 
├── src/                  # Código fuente
│   ├── __init__.py
│   ├── parser.py         # Parser FASTA/FASTQ jeje
│   ├── validator.py      # Motor de validación
│   ├── stats.py          # Cálculos estadísticos
│   └── cli.py           # Interfaz de línea de comandos
└── tests/               # Tests unitarios (pruebas)
    ├── __init__.py
    ├── test_parser.py
    ├── test_validator.py
    └── test_stats.py
```

## Tecnologías Utilizadas

- **Streamlit**: Este es un framework para interfaces web
- **Plotly**: Para hacer gráficos interactivos y responsive
- **Pandas**: Para manipulación y análisis de datos
- **Pytest**: Framework de testing para pruebas
- **Argparse/Click**: Parsing de argumentos de CLI

##  Contribuciones

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Haz commit a todos tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📝 Licencia

Este proyecto está bajo la Licencia MIT. Ver `LICENSE` para más detalles.

## Autora

**noomesk**  
Desarrolladora de Software esp en Bioinformática

---

*¿Encontraste útil esta herramienta? Dale una estrella al proyecto en mi github :3 
o déjame un mensaje en la sección de contacto en mi portafolio: https://noomesk.vercel.app