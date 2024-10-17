import streamlit as st
import boto3
import pandas as pd
import hashlib
import plotly.express as px
import plotly.graph_objects as go
from bs4 import BeautifulSoup
import re
import ast
import codecs
import streamlit.components.v1 as components
import numpy as np

def to_empty_list(val):
    if isinstance(val, (list, np.ndarray)):
        return [] if len(val) == 0 else val
    if pd.isna(val) or val is None:
        return []
    return val

def parse_categories(s):
    if isinstance(s, str):
        # Use the original regex-based parsing
        items = re.findall(r'"([^"]*)"|\b(\w+)\b', s)
        # Flatten the list of tuples and remove empty strings
        result = [item for sublist in items for item in sublist if item]
        # Sort the result
        return sorted(result)
    elif isinstance(s, list):
        # If it's already a list, just sort it
        return sorted(s)
    else:
        # For any other type, convert to string and wrap in a list
        return [str(s)]

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

    df_nice = pd.read_csv("data.csv")

    # Limpiamos y ordenadomos la columna direction
    df_nice['direction'] = df_nice['direction'].str.replace(' ', '')
    df_nice['direction'] = df_nice['direction'].replace('Outgoing', 'Entrante')
    df_nice['direction'] = df_nice['direction'].replace('Incoming', 'Saliente')


    df_nice = df_nice[["s3_path","direction","year","month","tematica","tipo","subtipo","detalle","subelemento","content"]]



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


    # cambiamos lo que se muestra en el front
    df_nice['Tipo'] = df_nice['Tipo'].replace('cuentas y acceso', 'gestion de cuenta y soporte clientes')

    # Replace values in the 'Subtipo' column
    df_nice['Subtipo'] = df_nice['Subtipo'].replace('incidencias', 'soporte web/app')

    
            # convertir las llamada a listas 
    try: 
        df_nice['Detalle']=df_nice['Detalle'].apply(parse_categories)
    except: 
        # Filter the dataframe based on selections
        df_nice['Detalle'] = df_nice['Detalle'].apply(ast.literal_eval).apply(sorted)

    try: 
        df_nice['Subelemento']=df_nice['Subelemento'].apply(parse_categories)
    except: 
        # Filter the dataframe based on selections
        df_nice['Subelemento'] = df_nice['Subelemento'].apply(ast.literal_eval).apply(sorted)
    

    # cambiar quejas por otros temas
    df_nice.loc[(df_nice['Tipo'] == 'otros temas') & (df_nice['Subtipo'] == 'quejas'), 'Subtipo'] = 'otros'

    # cambiar todas las listas sin Nan values
    df_nice['Detalle'] = df_nice['Detalle'].apply(to_empty_list)
    df_nice['Subelemento'] = df_nice['Subelemento'].apply(to_empty_list)
    
    
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



def download_html_file_s3(key,bucket_name="audios-nice"):
    
    #s3 = boto3.client('s3')
    #response = s3.get_object(Bucket=bucket_name, Key=key)
    #file_content = response['Body'].read().decode('utf-8')
    #return file_content
    file_path= key.replace("html_informes/call_center/", "")
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            file_content = file.read()

        print("aqui")
        return file_content
    except IOError as e:

        return None



def display_html(html_content):
    print("hola")
    # Decode the content from bytes to string
    try:
        decoded_content = html_content.decode('iso-8859-1')
    except UnicodeDecodeError:
            # If ISO-8859-1 fails, try UTF-8 with error handling
        decoded_content = html_content.decode('utf-8', errors='replace')
        
        # Display the HTML using st.components.v1.html
    components.html(decoded_content, scrolling=True, height=600)