import streamlit as st
import pandas as pd
import re
from st_aggrid import AgGrid, GridOptionsBuilder
from io import BytesIO

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

# Cargar y organizar el archivo
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
                referencia_fabrica = row[2]
                saldo_cantidades = row[3]

                organized_data.append({
                    'Bodega del producto': bodega,
                    'Código del producto': codigo_producto,
                    'Nombre del producto': nombre_producto,
                    'Talla': None,
                    'Cantidad': saldo_cantidades
                })

    organized_df = pd.DataFrame(organized_data)
    return organized_df

# Eliminar filas no deseadas
def eliminar_filas_no_deseadas(df):
    df = df.drop(index=range(0, 8))
    df.reset_index(drop=True, inplace=True)
    return df

# Función principal de la aplicación
def main():
    st.title('GestionAV - Organización de Productos')
    uploaded_file = st.file_uploader('Subir archivo Excel', type=['xlsx'])
    
    if uploaded_file is not None:
        df = pd.read_excel(uploaded_file)
        st.write('Datos subidos:')
        st.dataframe(df.head())
        
        organized_df = organizar_datos(df)
        cleaned_df = eliminar_filas_no_deseadas(organized_df)
        cleaned_df[['Nombre del producto', 'Talla']] = cleaned_df['Nombre del producto'].apply(lambda x: pd.Series(extraer_talla(x)))
        
        st.write('Datos organizados:')
        gb = GridOptionsBuilder.from_dataframe(cleaned_df)
        gb.configure_default_column(editable=True)
        grid_options = gb.build()

        response = AgGrid(
            cleaned_df,
            gridOptions=grid_options,
            update_mode='MODEL_CHANGED',
            editable=True,
            allow_unsafe_jscode=True,
            fit_columns_on_grid_load=True
        )

        edited_df = response['data']
        st.write("Datos editados:")
        st.dataframe(edited_df.head())

        buffer = BytesIO()
        edited_df.to_excel(buffer, index=False)
        buffer.seek(0)
        
        st.download_button(
            label='Descargar archivo editado',
            data=buffer,
            file_name='archivo_editado_Antioquia_Ventas.xlsx',
            mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )

if __name__ == '__main__':
    main()