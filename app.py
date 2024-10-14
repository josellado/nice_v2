import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import boto3
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
from PIL import Image
import base64
import os
import math
import json
import ast
import hashlib
import re
import streamlit.components.v1 as components

st.set_page_config(layout="wide")
from datos_utils import (create_interactive_df,
                             on_change)


# libraries 
from utils_streamlit import (load_data,
                             create_styled_pie_chart_2,hash_password,
                             check_password,
                             download_html_file_s3,
                             display_html)



def conversacion_chat_2(json_conver):
    json_conver_limpio = ast.literal_eval(json_conver)
    for message in json_conver_limpio:
        if message["speaker"] == "agente":
            st.markdown(f"""
            <div class="message agente">
             <img src="data:image/jpeg;base64,{img_base64}" class="agent-image" alt="Agent">
                <div class="message-content">
                    {message["text"]}
                    <div class="timestamp">12:00 PM</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="message cliente">
                <div class="message-content">
                    {message["text"]}
                    <div class="timestamp">12:00 PM</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

def conversacion_chat(json_conver):
    json_conver_limpio = ast.literal_eval(json_conver)
    with st.container():
        #st.markdown('<div class="chat-container">', unsafe_allow_html=True)
        for message in json_conver_limpio:
            print(message)
            col1, col2 = st.columns([7, 3])
            with col1:
                if message["speaker"] == "agente":
                    if img_base64:
                        img_html = f'<img src="data:image/jpeg;base64,{img_base64}" class="agent-image" alt="Agent">'
                    else:
                        img_html = '<img src="https://via.placeholder.com/30" class="agent-image" alt="Agent">'
                    
                    st.markdown(f"""
                    <div class="message agente">
                        {img_html}
                        <div class="message-content">
                            {message["text"]}
                            <div class="timestamp">12:00 PM</div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div class="message cliente">
                        <div class="message-content">
                            {message["text"]}
                            <div class="timestamp">12:00 PM</div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            with col2:
                st.write("")  # Empty column for spacing
        #st.markdown('</div>', unsafe_allow_html=True)



def get_image_base64(image_path):
    if not os.path.exists(image_path):
        st.error(f"Image file not found: {image_path}")
        return None
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()


def borrar_df_cache():

    if 'Aceptar_mostrar' in st.session_state:
        st.session_state.Aceptar_mostrar = False

    if 'df_interactive' in st.session_state:
        del st.session_state.df_interactive


@st.cache_data
def get_weeks(df):
    return df['week'].unique()


@st.cache_data
def get_month(df):
    return df['month'].unique()

@st.cache_data
def get_year(df):
    return df['year'].unique()





@st.cache_data
def get_latest_month(months):
    month_order = {month: index for index, month in enumerate(months)}
    return max(months, key=lambda m: month_order[m])

@st.cache_data
def get_latest_week(weeks):
    month_order = {week: index for index, week in enumerate(weeks)}
    return max(weeks, key=lambda m: month_order[m])



 
# Custom CSS to style the chat
st.markdown("""
<style>
.chat-container {
    background-color: #e5ddd5;
    border-radius: 10px;
    padding: 20px;
    max-width: 600px;
    margin: auto;
}
.message {
    padding: 10px;
    border-radius: 10px;
    margin-bottom: 10px;
    max-width: 70%;
    display: flex;
    align-items: flex-start;
}
.agente {
    background-color: #e3f2fd;  /* Light blue color for agent */
    float: left;
    clear: both;
}
.cliente {
    background-color: #dcf8c6;
    float: right;
    clear: both;
}
.timestamp {
    font-size: 0.75em;
    color: #999;
    text-align: right;
    margin-top: 5px;
}
.agent-image {
    width: 30px;
    height: 30px;
    border-radius: 50%;
    margin-right: 10px;
}
.message-content {
    flex-grow: 1;
}
</style>
""", unsafe_allow_html=True)


##

def main():

    
    df_entero = load_data()

    # Create a row for filters
    filter_col1, filter_col2, filter_col3 = st.columns(3)

    with filter_col1:
        years = get_year(df_entero)
        latest_year = max(years)
        selected_years = st.multiselect("Selecciona Año(s)", years, default=[latest_year], key="year_filter")


    with filter_col2:
        months =get_month(df_entero)
        latest_month=get_latest_month(months)

        selected_months = st.multiselect("Selecciona mes(es)", months, default=[latest_month], key="month_filter")

    with filter_col3:
        weeks = get_weeks(df_entero)
        latest_week = get_latest_week(weeks)
    

        selected_weeks = st.multiselect("Selecciona semana(es)", weeks, default=[latest_week],
                                         key="week_filter",
                                         on_change=borrar_df_cache)

    df = df_entero[
        (df_entero['year'].isin(selected_years)) & 
        (df_entero['month'].isin(selected_months)) & 
        (df_entero['week'].isin(selected_weeks))
    ]


    with filter_col3: 
        st.write(f"Num de llamadas: {df.shape[0]}")
 
    aceptar = st.checkbox("Aceptar Seleccion",key="Aceptar_mostrar")

    st.markdown("---")

    if aceptar:
        
        #lo primero un st tab para dividir las 2 paginas. 1 reusmens 2 datos 
        tab_datos,tab_llamadas, tab_resumnen = st.tabs(["Datos", "Filtrar Llamadas", "Resumen Semanal"])


        with tab_resumnen:
            for week in selected_weeks:

                week_name = week.replace("_", " ").title()

                with st.expander(f"Resumen semanal:  {week_name}"):

                    s3_path = f"html_informes/call_center/{week}.txt"
                    html_content= download_html_file_s3(key=s3_path)

                    if html_content:

                        html_content=html_content.replace('\\n', '')

                        html_content = html_content.replace('<th style="background-color: #f2f2f2; border: 1px solid #ddd; padding: 8px; text-align: left;"ead>'," ")
                        st.markdown(html_content, unsafe_allow_html=True)
                    else:
                        st.write("No pudimos cargar contenido")

        with tab_llamadas:

            ## Explorar la  tabla entera!!!!
            st.subheader("Filtrar Llamadas")
            

            # Filter by Tipo
            selected_tipo = st.selectbox("Seleccionar Tipo", ["All"] + list(df['Tipo'].unique()))

            # Filter by Subtipo (multiselect)
            if selected_tipo != "All":
                subtipos = df[df['Tipo'] == selected_tipo]['Subtipo'].unique()
                selected_subtipos = st.multiselect("Seleccionar Subtipo(s)", options=list(subtipos), default=[])
            else:
                selected_subtipos = []

            # Filter by Detalle
            if selected_tipo != "All" and selected_subtipos:
                detalle_mask = df['Tipo'] == selected_tipo
                detalle_mask &= df['Subtipo'].isin(selected_subtipos)

                detalles = df[detalle_mask]['Detalle'].explode().unique()
                selected_detalle = st.multiselect("Seleccionar Detalles", list(detalles),default=list(detalles))

            else:
                selected_detalle = "All"


            # Filter the dataframe based on selections
            filtered_df = df


            if selected_tipo != "All":
                filtered_df = filtered_df[filtered_df['Tipo'] == selected_tipo]

            if selected_subtipos:
                filtered_df = filtered_df[filtered_df['Subtipo'].isin(selected_subtipos)]

            #if selected_detalle != "All":
            #    filtered_df = filtered_df[filtered_df['Detalle'].apply(lambda x: any(item in x for item in selected_detalle))]

            if selected_detalle != "All":
                filtered_df = filtered_df[filtered_df['Detalle'].apply(lambda x: any(item in x for item in selected_detalle))]
            # --------------------------------------------------------------

            # PADNAS DF 
            # Custom CSS for dataframe styling
            def color_rows(row):
                return ['background-color: #f9f9f9' if i % 2 == 0 else '' for i in range(len(row))]

            styled_df = filtered_df[["Tipo","Subtipo","Detalle","Subelemento","Llamada","year","month","Seleccion"]].style\
                .set_properties(**{
                    'background-color': '#f2f2f2',
                    'color': '#333333',
                    'border-bottom': '1px solid #dddddd',
                    'text-align': 'left',
                    'font-family': 'Arial, sans-serif',
                    'font-size': '12px',
                    'padding': '8px'
                })\
                .set_table_styles([
                    {'selector': 'th', 'props': [
                        ('background-color', '#f2f2f2'),
                        ('color', '#333333'),
                        ('font-weight', 'bold'),
                        ('border-bottom', '2px solid #dddddd'),
                        ('padding', '10px')
                    ]},
                    {'selector': 'tr:hover', 'props': [('background-color', '#f5f5f5')]}
                ])\
                .apply(color_rows, axis=1)\
                .format({'id_call': lambda x: f'{x:,.0f}'})
            
            edited_df = st.data_editor(
                styled_df,
                #hide_index=True,
                use_container_width=True,
                hide_index=False,
                column_config={
                    "Seleccion": st.column_config.CheckboxColumn(
                        "Select",
                        help="Selecciona para descargar la llamada",
                        default=False,
                    ),
                "Detalle": st.column_config.ListColumn(
                    "Detalle"
                ),

                "Subelemento": st.column_config.ListColumn(
                    "Subelemento"
                ),


                },
                #disabled=["s3_path", "tematica", "cliente", "clase", "id_call", "new_class", "new_subclass", "direction"],
                num_rows="fixed"
            )

            col_bottones_1, col_bottones_2 = st.columns(2)

            # Reset Filters button
            if col_bottones_1.button('Quitar Filtros'):
                # Your existing reset filters code here
                st.rerun()

            # Download S3 Paths button
            if col_bottones_2.button('Descargar Llamadas'):
                # Get the s3 paths from the filtered dataframe
                selected_indices = edited_df.index[edited_df['Seleccion']].tolist()

                print(selected_indices,"??")
                # Use these indices to get the corresponding s3 paths from the original filtered_df
                selected_paths = filtered_df.loc[selected_indices, 's3_path']
                print(selected_paths.to_list())

                # version stream sin seguridad
                llamadas_descargadas=   filtered_df[filtered_df['s3_path'].isin(selected_paths.to_list())][['Tematica', 'Contenido']]

                #llamadas_descargadas =  # downlaod_llamadas_selecciondas(selected_paths.to_list())
                                        # sacar la funcion de NICE/V2       
                print(llamadas_descargadas)

                tabs = st.tabs([f"{i+1}" for i in range(len(llamadas_descargadas))])

                # Loop through each row and display its content in a tab
                for i, (index, row) in enumerate(llamadas_descargadas.iterrows()):
                    with tabs[i]:

                        with st.expander(f"Resumen Llamada: {index}", expanded=True):
                            st.write(row["Tematica"])
                        #st.write(row['content'])

                        with st.expander(f"Llamada Completa: {index}", expanded=False):
                            conversacion_chat_2(row["Contenido"])


        with tab_datos:
        
            if 'df_interactive' not in st.session_state:
                st.session_state.df_interactive = create_interactive_df(df)

            st.data_editor(
                st.session_state.df_interactive,
                hide_index=True,
                column_config={
                    "expanded": st.column_config.CheckboxColumn("Expand", help="Click to expand/collapse", default=False, width="small"),
                    "Tipo": st.column_config.TextColumn("Category", width="medium"),
                    "Subtipo": st.column_config.TextColumn("Subcategory", width="medium"),
                    "Detalle": st.column_config.TextColumn("Detail", width="medium"),
                    "Subelemento": st.column_config.TextColumn("Subelemento", width="medium"),
                    "Percentage": st.column_config.TextColumn("Percentage", width="small"),
                    "Count": st.column_config.NumberColumn("Count", format="%d", width="small"),
                    
                    "level": None,  # Hide this column
                },
                disabled=["Tipo", "Subtipo", "Detalle","Subelemento", "Percentage", "Count", "level"],
                key="editor",
                on_change=on_change,
                #kwargs=(df),
                use_container_width=True,
                column_order=["expanded", "Tipo", "Subtipo", "Detalle","Subelemento", "Percentage", "Count"]
                )
            
            st.caption("Data is displayed hierarchically. Expand categories to view subcategories and details.")





# Initialize session state
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

# Define username and password (in a real app, store these securely)
correct_username = "nice"
correct_password_hash = hash_password("Nice123")


image_path = "v2/images/logo.jpg"
img_base64 = get_image_base64(image_path)






# Authentication form
if not st.session_state.authenticated:
    #main()
    st.title("Login  NICE")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    
    if st.button("Login"):
        if username == correct_username and check_password(password, correct_password_hash):
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("Incorrect username or password")


else:
    # Your main app code 
    main()

    if st.button("Logout"):
        st.session_state.authenticated = False
        st.rerun()





