import streamlit as st
import pandas as pd
import re
from io import BytesIO
from streamlit_modal import Modal

# Función para extraer talla y modificar el nombre del producto
def extraer_talla(nombre_producto):
    patron = r"\b(\d{1,2}(?:\.\d{1,2})? ?[XSML]{1,3})\b"
    talla = re.search(patron, nombre_producto)
    if talla:
        talla = talla.group(0)
        nombre_producto = re.sub(patron, "", nombre_producto).strip()
    else:
        talla = None
    return nombre_producto, talla

# Función para organizar los datos
def organizar_datos(df):
    df.columns = [col.strip() for col in df.columns]
    return df

# Función para eliminar filas no deseadas
def eliminar_filas_no_deseadas(df):
    return df.dropna(how='all')

# Función para actualizar códigos
def actualizar_codigos(df):
    st.write("Ingrese el código de barras para el producto:")
    for i, row in df.iterrows():
        producto = row["Nombre del producto"]
        codigo_de_barras = st.text_input(f"Codigo de barras para '{producto}'", key=f"barcode_{i}")
        if st.button("Guardar", key=f"save_{i}"):
            df.at[i, "Codigo del producto"] = codigo_de_barras
            st.success(f"Código de barras actualizado para '{producto}'")
        if st.button("Continuar", key=f"next_{i}"):
            break
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
        st.dataframe(cleaned_df.head())

        if st.button('Actualizar códigos'):
            updated_df = actualizar_codigos(cleaned_df)
            st.write('Datos actualizados:')
            st.dataframe(updated_df)

            # Botón para guardar progreso
            if st.button('Guardar progreso'):
                buffer_temp = BytesIO()
                updated_df.to_excel(buffer_temp, index=False)
                buffer_temp.seek(0)

                st.download_button(
                    label='Descargar progreso guardado',
                    data=buffer_temp,
                    file_name='progreso_guardado.xlsx',
                    mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                )

        # Botón para descargar datos limpios
        buffer_cleaned = BytesIO()
        cleaned_df.to_excel(buffer_cleaned, index=False)
        buffer_cleaned.seek(0)

        st.download_button(
            label='Descargar archivo organizado',
            data=buffer_cleaned,
            file_name='archivo_organizado_Antioquia_Ventas.xlsx',
            mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )

if __name__ == '__main__':
    main()
