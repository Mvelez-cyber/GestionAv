import streamlit as st
import pandas as pd
import re
from io import BytesIO
from st_aggrid import AgGrid, GridOptionsBuilder
import streamlit_modal as modal

st.set_page_config(
    page_title="Gestion de Inventarios Antioquia Ventas",
    page_icon="https://taplink.st/a/2/f/3/6/44927f.png?4",  # This is an emoji shortcode. Could be a URL too.
)

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
    return pd.DataFrame(organized_data)

# Función para eliminar filas no deseadas
def eliminar_filas_no_deseadas(df):
    df = df.drop(index=range(0, 8))
    df.reset_index(drop=True, inplace=True)
    return df

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

# Función para actualizar los códigos de barras
def actualizar_codigos(df, bodega):
    bodega_df = df[df['Bodega del producto'] == bodega].copy()
    updated_codes = {}
    total_productos = len(bodega_df)

    if 'current_index' not in st.session_state:
        st.session_state.current_index = 0

    index = st.session_state.current_index
    if index < total_productos:
        producto = bodega_df.iloc[index]

        modal.open(name="codigo_barras_modal")

        with modal.container(name="codigo_barras_modal", title="Actualizar Código de Barras"):
            st.write(f"Ingrese el código de barras para el producto: {producto['Nombre del producto']}")
            codigo_barras = st.text_input("Código de barras", key=f"codigo_{index}")
            
            if st.button('Guardar'):
                updated_codes[index] = codigo_barras
                bodega_df.at[bodega_df.index[index], 'Código del producto'] = codigo_barras
                st.session_state.current_index = (index + 1) % total_productos
                modal.close(name="codigo_barras_modal")

            if st.button('Continuar'):
                st.session_state.current_index = (index + 1) % total_productos
                modal.close(name="codigo_barras_modal")

    st.write('Datos actualizados:')
    st.dataframe(bodega_df.head())
    
    return bodega_df

# Función principal de la aplicación
def main():
    st.markdown(
    """
    <div style="display: flex; align-items: center;">
        <img src="https://taplink.st/a/2/f/3/6/44927f.png?4" style="width: 50px; height: auto; margin-right: 10px;">
        <h1 style="margin: 0;">Organización de Productos</h1>
    </div>
    """,
    unsafe_allow_html=True
    )
    st.title('Organización de Productos')
    uploaded_file = st.file_uploader('Subir archivo Excel', type=['xlsx'])

    if uploaded_file is not None:
        df = pd.read_excel(uploaded_file)
        st.write('Datos subidos:')
        st.dataframe(df.head())

        organized_df = organizar_datos(df)
        cleaned_df = eliminar_filas_no_deseadas(organized_df)
        cleaned_df[['Nombre del producto', 'Talla']] = cleaned_df['Nombre del producto'].apply(lambda x: pd.Series(extraer_talla(x)))

        st.write('Datos organizados:')
        st.dataframe(cleaned_df.head())

        bodega_list = cleaned_df['Bodega del producto'].unique().tolist()
        selected_bodega = st.selectbox('Seleccione la bodega para actualizar los códigos:', bodega_list)

        if st.button('Actualizar códigos'):
            updated_df = actualizar_codigos(cleaned_df, selected_bodega)

            buffer = BytesIO()
            updated_df.to_excel(buffer, index=False)
            buffer.seek(0)

            st.download_button(
                label='Descargar archivo con progreso',
                data=buffer,
                file_name='archivo_progreso_Antioquia_Ventas.xlsx',
                mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )

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