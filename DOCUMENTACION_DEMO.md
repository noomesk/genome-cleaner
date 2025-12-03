# Genome Cleaner: Documentación Técnica y Guion de Demo

## 📘 Explicación Técnica Detallada

Genome Cleaner es una aplicación web de bioinformática construida con una arquitectura modular en Python, diseñada para procesar, limpiar y validar secuencias genómicas (DNA).

### 1. Arquitectura del Sistema

La aplicación sigue el patrón Modelo-Vista (Model-View) simplificado:

*   **Frontend (Vista)**: Construido con **Streamlit**. Se encarga de la interfaz de usuario, la gestión del estado de la sesión (`st.session_state`) y la visualización de datos.
*   **Backend (Lógica)**: Módulos Python puros ubicados en `src/` que manejan la lógica de negocio.

### 2. Desglose de Módulos

#### A. `app.py` (El Controlador/Vista)
Es el punto de entrada.
*   **Gestión de Estado**: Mantiene los resultados en `st.session_state` para que no se pierdan al interactuar con los widgets.
*   **UI Layout**: Define el sidebar (carga de archivos) y las pestañas principales (Resumen, Validación, Visualización, Reportes).
*   **Estilos**: Inyecta CSS personalizado para un tema oscuro profesional y responsivo.

#### B. `src/parser.py` (Ingesta de Datos)
*   **Detección de Formato**: Analiza las primeras líneas del archivo para determinar automáticamente si es FASTA (`>`) o FASTQ (`@`).
*   **Parsing**: Lee el archivo línea por línea.
    *   *FASTA*: Extrae cabeceras y concatena líneas de secuencia.
    *   *FASTQ*: Extrae cabeceras, secuencias y salta las líneas de calidad (`+` y scores) para centrarse en la secuencia biológica.

#### C. `src/validator.py` (Núcleo de Procesamiento)
Es el cerebro de la herramienta. Realiza dos funciones principales:
1.  **Validación**:
    *   *Caracteres*: Verifica que solo contenga bases válidas (A, C, G, T, N).
    *   *Longitud*: Marca como error si es menor al umbral (default 20bp).
    *   *Duplicados*: Detecta cabeceras repetidas usando `collections.Counter`.
    *   *Complejidad*: Alerta sobre secuencias repetitivas o de baja complejidad.
2.  **Sanitización** (Si se activa):
    *   Convierte todo a mayúsculas.
    *   Reemplaza caracteres inválidos con 'N' (base desconocida) para no perder la posición en la secuencia.

#### D. `src/stats.py` (Análisis)
Genera las métricas para los reportes.
*   Calcula el contenido GC (Guanina-Citosina), crucial para determinar la estabilidad de la molécula.
*   Genera distribuciones de longitud y calidad.
*   Prepara los datos para la exportación en JSON y CSV.

### 3. Flujo de Datos
1.  **Upload**: El usuario sube un archivo -> Se guarda temporalmente en `temp/`.
2.  **Parse**: `parser.py` lee el archivo y devuelve una lista de tuplas `(header, sequence)`.
3.  **Process**: `validator.py` itera sobre cada secuencia, aplicando reglas y sanitización. Genera una lista de diccionarios con metadatos (`is_valid`, `errors`, `gc_content`).
4.  **Visualize**: `app.py` toma estos resultados y usa **Plotly** para renderizar gráficos interactivos (histogramas de longitud, distribución de errores).
5.  **Export**: Se generan archivos descargables (CSV, JSON, FASTA limpio) a partir de los datos procesados.

---

## 🎬 Guion para Video Demo (Portfolio/LinkedIn)

**Objetivo**: Demostrar competencia técnica en Bioinformática y Desarrollo Full Stack (Python).
**Duración estimada**: 60-90 segundos.

### Estructura del Video
1.  **Intro (0-10s)**: El problema (datos sucios).
2.  **La Solución (10-20s)**: Qué es Genome Cleaner.
3.  **Demo Técnica (20-50s)**: Flujo de uso (Upload -> Process -> Analyze).
4.  **Cierre (50-60s)**: Stack tecnológico y Call to Action.

---

### 🇪🇸 Opción A: Guion en Español

| Tiempo | Acción Visual en Pantalla | Guion (Voz en Off) |
| :--- | :--- | :--- |
| **0:00** | Muestra un archivo FASTA desordenado en un editor de texto (con caracteres raros, minúsculas). | "¿Alguna vez has perdido horas limpiando manualmente archivos FASTA corruptos o con secuencias basura?" |
| **0:08** | Transición al **Home** de Genome Cleaner (Logo y título). | "Te presento **Genome Cleaner**, una herramienta profesional que desarrollé para automatizar la validación de secuencias genómicas." |
| **0:15** | Click en el **Sidebar**. Arrastra el archivo `test_sample.fasta`. | "Su interfaz es intuitiva. Simplemente subes tu archivo FASTA o FASTQ..." |
| **0:22** | Activa el checkbox **"Sanitization Mode"** y ajusta el slider de longitud. Click en **"Process File"**. | "...configuras tus reglas de limpieza, como el filtrado por longitud mínima o la sanitización automática de caracteres inválidos, y procesas." |
| **0:30** | Muestra la pestaña **"Summary"** y luego **"Visualizations"** (pasa el mouse por los gráficos). | "En segundos, obtienes un análisis completo: métricas de calidad, distribución de contenido GC y detección de errores." |
| **0:40** | Muestra la pestaña **"Cleaning & Validation"** (la tabla de datos). | "Puedes inspeccionar cada secuencia detalle a detalle..." |
| **0:45** | Click en **"Reports"** y descarga el JSON o el FASTA limpio. | "...y exportar tus datos ya limpios y listos para el análisis downstream." |
| **0:52** | Pantalla final con tu nombre, tecnologías (Python, Streamlit, Pandas) y enlace a GitHub. | "Desarrollado con Python, Streamlit y Pandas. Soy [Tu Nombre], y este es mi aporte a la bioinformática reproducible." |

---

### 🇺🇸 Option B: English Script

| Time | Visual Action on Screen | Script (Voiceover) |
| :--- | :--- | :--- |
| **0:00** | Show a messy FASTA file in a text editor. | "Tired of spending hours manually cleaning corrupt FASTA files or dealing with sequencing errors?" |
| **0:08** | Transition to **Genome Cleaner Home**. | "Meet **Genome Cleaner**, a professional tool I built to automate genomic sequence validation." |
| **0:15** | Click **Sidebar**. Drag & drop `test_sample.fasta`. | "The interface is seamless. Just upload your FASTA or FASTQ raw data..." |
| **0:22** | Check **"Sanitization Mode"**, adjust length slider. Click **"Process File"**. | "...set your cleaning rules—like minimum length thresholds or auto-sanitization of invalid bases—and hit process." |
| **0:30** | Show **"Summary"** tab, then hover over charts in **"Visualizations"**. | "In seconds, you get a comprehensive analysis: quality metrics, GC content distribution, and error detection." |
| **0:40** | Show **"Cleaning & Validation"** tab (data table). | "You can inspect every single sequence in detail..." |
| **0:45** | Click **"Reports"** and download the clean FASTA. | "...and export your clean, validated datasets ready for downstream analysis." |
| **0:52** | Final screen with your name, tech stack (Python, Streamlit, Pandas), and GitHub link. | "Built with Python, Streamlit, and Pandas. I'm [Your Name], and this is my contribution to reproducible bioinformatics." |

### 💡 Tips para la Grabación
1.  **Graba la pantalla en alta resolución (1080p)**.
2.  Usa un mouse con movimiento suave (evita movimientos bruscos).
3.  Si no quieres usar tu voz, puedes usar herramientas de IA para "Text-to-Speech" con los guiones de arriba.
4.  **Zoom**: Haz zoom en partes clave (como cuando activas el "Sanitization Mode" o cuando ves los gráficos) para que se vea bien en móviles (LinkedIn).
