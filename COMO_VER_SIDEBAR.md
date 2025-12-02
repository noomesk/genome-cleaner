# INSTRUCCIONES: Cómo Ver el Sidebar en Genome Cleaner

## El Problema

No ves el menú lateral (sidebar) donde debes subir los archivos FASTA/FASTQ.

## La Solución

El sidebar **SÍ ESTÁ AHÍ**, pero puede estar **colapsado** (oculto).

### Paso 1: Busca el Botón de Flecha

En la esquina **superior izquierda** de la página de Streamlit, busca un pequeño botón con una **flecha (>)**.

### Paso 2: Haz Click en la Flecha

Haz click en ese botón de flecha para **expandir el sidebar**.

### Paso 3: Verás el Menú

Una vez expandido, verás:
- **"File Upload & Settings"** (título del sidebar)
- **"Upload FASTA/FASTQ file"** (botón para subir archivos)
- Opciones de procesamiento
- Botón "Process File"

## Ubicación del Sidebar

```
┌─────────────────────────────────────┐
│ [>] Genome Cleaner          ← FLECHA│
├──────────┬──────────────────────────┤
│          │                          │
│ SIDEBAR  │   CONTENIDO PRINCIPAL    │
│ (aquí    │   (pantalla de           │
│ subes    │   bienvenida)            │
│ archivos)│                          │
│          │                          │
└──────────┴──────────────────────────┘
```

## Si Aún No Lo Ves

1. **Refresca la página** (F5 o Ctrl+R)
2. **Verifica la URL**: Debe ser `http://localhost:8501`
3. **Revisa el ancho de tu ventana**: Si la ventana es muy estrecha, el sidebar se colapsa automáticamente

## Formatos Soportados

Una vez que veas el sidebar, puedes subir archivos con estas extensiones:
- `.fasta`
- `.fa`
- `.fastq`
- `.fq`

## Archivo de Prueba

Puedes usar el archivo de muestra que ya tienes:
- `test_sample.fasta`
