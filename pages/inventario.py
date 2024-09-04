import streamlit as st
import pandas as pd
from io import BytesIO
import re
# Import functions from the pipeline script
from pages import inventario

# Function definitions from your pipeline
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
            if not cell_value.isdigit():
                codigo_producto = cell_value
                nombre_producto = row[1]
                saldo_cantidades = row[3]  # Asegurarse de que esta columna es la de cantidades
                organized_data.append({
                    'Bodega del producto': bodega,
                    'Código del producto': codigo_producto,
                    'Nombre del producto': nombre_producto,
                    'Cantidad': saldo_cantidades,
                    'Talla': None
                })

    return pd.DataFrame(organized_data)

def limpiar_datos(df):
    cleaned_data = []
    current_producto = None

    for i, row in df.iterrows():
        cell_value = str(row[0]).strip()

        if 'Producto:' in cell_value:
            current_producto = {
                'producto': cell_value.replace('Producto: ', ''),
                'nombre': row[1],
                'cantidad': row[3]
            }
        elif 'Bodega:' in cell_value:
            if current_producto:
                bodega = cell_value.replace('Bodega: ', '')
                cleaned_data.append({
                    'Bodega del producto': bodega,
                    'Código del producto': current_producto['producto'],
                    'Nombre del producto': current_producto['nombre'],
                    'Cantidad': current_producto['cantidad']
                })
        elif current_producto and cell_value.isdigit():
            current_producto['cantidad'] = cell_value

    return pd.DataFrame(cleaned_data)

def separar_codigo_y_nombre(df):
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

    df[['Código del producto', 'Nombre del producto']] = df['Código del producto'].str.split('-', n=1, expand=True)
    df[['Nombre del producto', 'Talla']] = df['Nombre del producto'].apply(lambda x: pd.Series(extraer_talla(x)))
    return df

def main():
    st.title("Inventario Completo")
    uploaded_file = st.file_uploader('Subir archivo Excel', type=['xlsx'])

    if uploaded_file is not None:
        df = pd.read_excel(uploaded_file)
        st.write('Datos subidos:')
        st.dataframe(df.head())

        # Process the data
        cleaned_df = limpiar_datos(df)
        cleaned_df = separar_codigo_y_nombre(cleaned_df)

        st.write('Inventario procesado:')
        st.dataframe(cleaned_df)

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
