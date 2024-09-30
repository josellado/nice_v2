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

st.set_page_config(layout="wide")


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

def replace_values(x):
    if x == "client":
        return "Si"
    else:
        return "No"

def duplicate_if_single_element(lst):
    if len(lst) == 1:
        return lst * 2  # Duplicate the single element
    return lst


def get_text_file_content_from_s3(bucket_name, object_key):
      
    """
    Retrieves the content of a text file from an S3 bucket.

    :param bucket_name: str. The name of the S3 bucket.
    :param object_key: str. The key of the object in the S3 bucket.
    :return: str. The content of the text file.
    """
    # Initialize a session using Amazon S3
    s3 = boto3.client('s3')


    # Get the object from the S3 bucket
    response = s3.get_object(Bucket=bucket_name, Key=object_key)
    
    # Read the content of the file
    content = response['Body'].read().decode('utf-8')
    
    return content


@st.cache_data(ttl=200)
def load_data():
    # Sample DataFrame
    #df_nice = pd.read_csv("new_clase/maestro.csv")
 

    df_nice = pd.read_csv("data.csv")

    # Limpiamos y ordenadomos la columna direction
    df_nice['direction'] = df_nice['direction'].str.replace(' ', '')
    df_nice['direction'] = df_nice['direction'].replace('Outgoing', 'Entrante')
    df_nice['direction'] = df_nice['direction'].replace('Incoming', 'Saliente')


    # columna cliente si si o no
    #df_nice['cliente'] = df_nice['cliente'].apply(replace_values)

    #df_nice = df_nice[["s3_path","direction","new_class","new_subclass","tematica"]]

    df_nice = df_nice[["s3_path","direction","year","month","tematica","tipo","subtipo","detalle","subelemento","content"]]

    #df_nice['new_subclass']=df_nice['new_subclass'].apply(ast.literal_eval)
#
    #    # palbra asistencia esta mal 
    #df_nice["new_subclass"] = df_nice["new_subclass"].replace(["Asistecia"],["Asistencia"])


    # ordenadmos los valores 
    #df_nice['new_subclass']=df_nice['new_subclass'].apply(sorted)

    df_nice["Seleccion"] = False

    
    # renombramos columnas
    df_nice.columns = ["s3_path","Llamada","year","month","Tematica","Tipo","Subtipo","Detalle","Subelemento","Contenido","Seleccion"]


    # ordenamos por ellas
    df_nice['Detalle_tuple'] = df_nice['Detalle'].apply(tuple)

    # Sort using the tuple column
    df_nice = df_nice.sort_values(by=['Tipo', 'Subtipo', 'Detalle_tuple'])

    # Remove the temporary column
    df_nice = df_nice.drop('Detalle_tuple', axis=1)
    #df_nice = df_nice.sort_values(by=['Tipo', 'Subtipo', 'Detalle'])


    # quitar Nans de subtipo 
    df_nice['Subtipo'] = df_nice['Subtipo'].fillna(df_nice['Tipo'])


    df_nice['week'] = df_nice['s3_path'].str.split('/').str[3]




    return  df_nice


def extract_s3_keys(indices,df):

    lista_s3 = df.loc[indices, "s3_path"].tolist()
    print(lista_s3)

    return lista_s3


def create_styled_pie_chart_2(data, title, colors):
    labels = data["Subtipo"].unique()
    
    # Count occurrences of each subclass
    subclass_counts = pd.Series(labels).value_counts()
    
    fig = go.Figure(data=[go.Pie(
        labels=subclass_counts.index, 
        values=subclass_counts.values,
        marker=dict(colors=colors[:len(subclass_counts)]),
        textinfo='percent',
        insidetextorientation='radial',
        textfont=dict(size=8),
        showlegend=True
    )])
    
    fig.update_layout(
        height=300,  # Increased height to accommodate legend
        width=400,   # Set a fixed width
        font=dict(family="Arial", size=10),
        title=dict(text=f"{title}", font=dict(size=12), y=0.95, x=0.5, xanchor='center', yanchor='top'),
        margin=dict(l=20, r=100, t=60, b=20),  # Increased right margin for legend
        legend=dict(
            orientation="v",  # Vertical orientation
            yanchor="middle",
            y=0.5,
            xanchor="right",
            x=1.1,
            font=dict(size=8),  # Smaller font size for legend
            itemsizing='constant',  # Constant size for legend items
            traceorder='normal'
        )
    )
    
    # Adjust the pie chart size to make room for the legend
    fig.update_traces(
        domain=dict(x=[0, 0.7], y=[0, 1])  # Adjust the domain of the pie chart
    )
    
    return fig


# Function to hash passwords
def hash_password(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

# Function to check if the entered password matches the stored hash
def check_password(password, hashed_password):
    return hash_password(password) == hashed_password


def main():

    df_entero = load_data()


    # Custom color palette
    colors = ['#4e79a7', '#f28e2c', '#e15759', '#76b7b2', '#59a14f', '#edc949', '#af7aa1', '#ff9da7', '#9c755f', '#bab0ab']



    # Create a row for filters
    filter_col1, filter_col2, filter_col3 = st.columns(3)

    with filter_col1:
        years = sorted(df_entero['year'].unique())
        latest_year = max(years)
        selected_years = st.multiselect("Selecciona Año(s)", years, default=[latest_year], key="year_filter")


    with filter_col2:
        months = df_entero['month'].unique()
        month_order = {month: index for index, month in enumerate(months)}
        latest_month = max(months, key=lambda m: month_order[m])
        selected_months = st.multiselect("Selecciona mes(es)", months, default=[latest_month], key="month_filter")

    with filter_col3:
        weeks = df_entero['week'].unique()
        month_order = {week: index for index, week in enumerate(weeks)}
        latest_month = max(weeks, key=lambda m: month_order[m])
        selected_weeks = st.multiselect("Selecciona semana(es)", weeks, default=[latest_month], key="week_filter")



    # Filter the dataframe
    df = df_entero[
        (df_entero['year'].isin(selected_years)) & 
        (df_entero['month'].isin(selected_months)) & 
        (df_entero['week'].isin(selected_weeks))
    ]

    with filter_col3: 
        st.write(f"Num de llamadas: {df.shape[0]}")


    ## EMPIEZAZAN LOS GRAFICOS -------------------------------------------

    # Create a row with two columns for the charts
    col1, col2 = st.columns(2)

    # Bar chart for new_class distribution (in the first column)
    with col1:
        st.subheader("Distribución de Clases")
        class_counts = df['Tipo'].value_counts()
        fig_bar = go.Figure(data=[go.Bar(
            x=class_counts.index, 
            y=class_counts.values,
            marker_color=colors[:len(class_counts)]
        )])
        fig_bar.update_layout(
            height=600,
            font=dict(family="Arial", size=12),
            #title=dict(text="Distribution of New Classes", font=dict(size=20), y=0.9),
            xaxis_title="Clase",
            yaxis_title="Count",
            margin=dict(l=50, r=50, t=80, b=50),
            plot_bgcolor='white',
            bargap=0.2
        )
        fig_bar.update_xaxes(tickangle=45)
        st.plotly_chart(fig_bar, use_container_width=True)

    # Pie charts for client and direction distribution (in the second column)
    with col2:


        # Direction distribution pie chart
        st.subheader("Tipo de Llamada")
        direction_counts = df['Llamada'].value_counts()
        fig_pie_direction = go.Figure(data=[go.Pie(
            labels=direction_counts.index, 
            values=direction_counts.values,
            marker=dict(colors=colors[:len(direction_counts)]),
            textinfo='percent+label',
            insidetextorientation='radial'
        )])
        fig_pie_direction.update_layout(
            height=300,
            font=dict(family="Arial", size=12),
            #title=dict(text="Distribution of Call Directions", font=dict(size=18), y=0.95),
            margin=dict(l=20, r=20, t=60, b=20)
        )
        st.plotly_chart(fig_pie_direction, use_container_width=True)




    # SUBTIPO 
    ### ---------------------------------------------------------
    with st.expander("Explorar Subtipos", expanded=False):
        # Get the unique classes
        unique_classes = df['Tipo'].unique()
        num_classes = len(unique_classes)

        # Determine the number of columns (you can adjust this as needed)
        num_columns = 2  # Default to 3 columns, but you can change this

        # Calculate the number of rows needed
        num_rows = math.ceil(num_classes / num_columns)

        # Create a list to hold all columns
        columns = []

        # Create the grid of columns
        for _ in range(num_rows):
            row_columns = st.columns(num_columns)
            columns.extend(row_columns)

        # Iterate through each unique new_class and create a pie chart
        for i, new_class in enumerate(unique_classes):
            print(new_class)
            class_data = df[df['Tipo'] == new_class]
            fig_pie = create_styled_pie_chart_2(class_data, f"{new_class}",colors)
            
            # Place each pie chart in the appropriate column
            columns[i].plotly_chart(fig_pie, use_container_width=True)



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
        detalles = df[detalle_mask]['Detalle'].unique()
        selected_detalle = st.selectbox("Seleccionar Detalle", ["All"] + list(detalles))
    else:
        selected_detalle = "All"

    # Filter the dataframe based on selections
    filtered_df = df

    if selected_tipo != "All":
        filtered_df = filtered_df[filtered_df['Tipo'] == selected_tipo]

    if selected_subtipos:
        filtered_df = filtered_df[filtered_df['Subtipo'].isin(selected_subtipos)]

    if selected_detalle != "All":
        filtered_df = filtered_df[filtered_df['Detalle'] == selected_detalle]

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
        hide_index=True,
        column_config={
            "Seleccion": st.column_config.CheckboxColumn(
                "Select",
                help="Selecciona para descargar la llamada",
                default=False,
            )
        },
        #disabled=["s3_path", "tematica", "cliente", "clase", "id_call", "new_class", "new_subclass", "direction"],
        num_rows="dynamic"
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

                with st.expander("Resumen Llamada", expanded=True):
                    st.write(row["Tematica"])
                #st.write(row['content'])

                with st.expander("Llamada Completa", expanded=False):
                    conversacion_chat_2(row["Contenido"])


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
        st.experimental_rerun()