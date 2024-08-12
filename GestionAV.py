import streamlit as st
import pandas as pd
import re
from io import BytesIO

# Función para organizar los datos del DataFrame
def organizar_datos(df):
    organized_data = []
    producto = None
    bodega = None

    for i, row in df.iterrows():
        cell_value = str(row[0]).strip()
        if cell_value.startswith('Producto:'):
            producto = cell_value.replace('Producto: ', '')
        elif cell_value.startswith('Bodega:'):
            bodega = cell_value.replace('Bodega: ', '')
        else:
            # Si el valor de la celda no es un número y no está vacío
            if cell_value and not cell_value.isdigit():
                codigo_producto = cell_value
                nombre_producto = row[1]  # Mantener el nombre del producto
                referencia_fabrica = row[2]
                saldo_cantidades = row[3]
                organized_data.append({
                    'Bodega del producto': bodega,
                    'Código del producto': codigo_producto,
                    'Nombre del producto': nombre_producto,
                    'Talla': None,
                    'Cantidad': saldo_cantidades
                })
    return pd.DataFrame(organized_data)

# Función para eliminar filas no deseadas sin perder información
def eliminar_filas_no_deseadas(df):
    # Realiza la limpieza evitando eliminar información relevante
    df_cleaned = df.dropna(subset=['Código del producto', 'Nombre del producto'])
    df_cleaned = df_cleaned[df_cleaned['Código del producto'].str.startswith('7') | df_cleaned['Código del producto'].str.startswith('5')]
    df_cleaned.reset_index(drop=True, inplace=True)
    return df_cleaned

# Función para extraer talla y modificar el nombre del producto
def extraer_talla(nombre_producto):
    if not isinstance(nombre_producto, str):
        return nombre_producto, None

    talla_pattern = re.compile(r'\b(T|TALLA)\s?(XS|S|M|L|XL|XXL|XXXL)\b$')
    match = talla_pattern.search(nombre_producto)
    if match:
        talla = match.group(2)
        nombre_producto = talla_pattern.sub('', nombre_producto).strip()
        return nombre_producto, talla
    return nombre_producto, None

# Función principal de la aplicación
def main():
    st.title('GestionAV - Organización de Productos')
    uploaded_file = st.file_uploader('Subir archivo Excel', type=['xlsx'])

    if uploaded_file is not None:
        df = pd.read_excel(uploaded_file)
        st.write('Datos subidos:')
        st.dataframe(df.head())

        # Organizar datos sin perder información
        organized_df = organizar_datos(df)
        cleaned_df = eliminar_filas_no_deseadas(organized_df)
        cleaned_df[['Nombre del producto', 'Talla']] = cleaned_df['Nombre del producto'].apply(lambda x: pd.Series(extraer_talla(x)))

        st.write('Datos organizados:')
        st.dataframe(cleaned_df.head())

        buffer_cleaned = BytesIO()
        cleaned_df.to_excel(buffer_cleaned, index=False)
        buffer_cleaned.seek(0)

        st.download_button(
            label='Descargar datos limpios',
            data=buffer_cleaned,
            file_name='datos_limpios_Antioquia_Ventas.xlsx',
            mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )

if __name__ == '__main__':
    main()
