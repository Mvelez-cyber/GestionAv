# Gestión de Inventarios Antioquia Ventas

## Descripción

Este proyecto es una aplicación de Streamlit para la organización y gestión de inventarios de productos. Permite subir un archivo Excel con datos de productos, organizarlos, limpiar datos no deseados, extraer tallas de los nombres de productos y actualizar códigos de barras. Además, ofrece opciones para descargar los datos limpios y los datos con el progreso actualizado.

## Características

- **Subida de archivos Excel**: Permite cargar un archivo Excel con datos de productos.
- **Organización de datos**: Procesa y organiza los datos para su análisis.
- **Limpieza de datos**: Elimina filas no deseadas y limpia el DataFrame.
- **Extracción de tallas**: Identifica y extrae tallas de los nombres de productos.
- **Actualización de códigos de barras**: Permite actualizar códigos de barras para productos de una bodega seleccionada.
- **Descarga de archivos**: Ofrece opciones para descargar tanto los datos limpios como los datos con el progreso actualizado.

## Instalación

Para ejecutar esta aplicación, necesitas tener Python 3.x instalado y las siguientes bibliotecas:

- `streamlit`
- `pandas`
- `re`
- `st_aggrid`
- `streamlit_modal`

Puedes instalar las bibliotecas necesarias usando `pip`:

```bash
pip install streamlit pandas st-aggrid streamlit-modal
