import streamlit as st
import pandas as pd
from utils_streamlit import load_data


from collections import Counter



def calculate_hierarchical_percentages(df):
    total_count = len(df)
    
    # Calculate percentages for Tipo
    tipo_counts = df['Tipo'].value_counts()
    tipo_percentages = round((tipo_counts / total_count * 100), 2)
    
    results = []
    
    for tipo in tipo_counts.index:

        tipo_df = df[df['Tipo'] == tipo]
        tipo_count = len(tipo_df)
        
        # Calculate percentages for Subtipo within each Tipo
        subtipo_counts = tipo_df['Subtipo'].value_counts()
        subtipo_percentages = round((subtipo_counts / tipo_count * 100), 2)
        
        for subtipo in subtipo_counts.index:
            subtipo_df = tipo_df[tipo_df['Subtipo'] == subtipo]
            subtipo_count = len(subtipo_df)
            
            # Calculate percentages for Detalle within each Subtipo
            detalle_items = [item for sublist in subtipo_df['Detalle'].tolist() for item in sublist]
            detalle_counts = Counter(detalle_items)
            total_detalle_count = sum(detalle_counts.values())
            
            if total_detalle_count > 0:
                for detalle, detalle_count in detalle_counts.items():

                    detalle_percentage = round((detalle_count / total_detalle_count * 100), 2)
                    
                    # Calculate percentages for Subelemento within each Detalle
                    Subelemento_df = subtipo_df[subtipo_df['Detalle'].apply(lambda x: detalle in x)]
                    Subelemento_items = [item for sublist in Subelemento_df['Subelemento'].tolist() for item in sublist]
                    Subelemento_counts = Counter(Subelemento_items)
                    
                    # si esta en nan lo contamos:
                    empty_list_count = sum(1 for sublist in Subelemento_df['Subelemento'].tolist() if not sublist)
                    Subelemento_counts[''] = empty_list_count

                    # total de las listas
                    total_Subelemento_count = sum(Subelemento_counts.values())

                    
                    if total_Subelemento_count > 0:
                        for Subelemento, Subelemento_count in Subelemento_counts.items():
                            Subelemento_percentage = round((Subelemento_count / total_Subelemento_count * 100), 2)
                            results.append({
                                'Tipo': tipo,
                                'Tipo_Percentage': tipo_percentages[tipo],
                                'Subtipo': subtipo,
                                'Subtipo_Percentage': subtipo_percentages[subtipo],
                                'Detalle': detalle,
                                'Detalle_Percentage': detalle_percentage,
                                'Subelemento': Subelemento,
                                'Subelemento_Percentage': Subelemento_percentage,
                                'Tipo_Count': tipo_count,
                                'Subtipo_Count': subtipo_count,
                                'Detalle_Count': detalle_count,
                                'Subelemento_Count': Subelemento_count
                            })
                    else:
                        # Handle empty Subelemento list
                        results.append({
                            'Tipo': tipo,
                            'Tipo_Percentage': tipo_percentages[tipo],
                            'Subtipo': subtipo,
                            'Subtipo_Percentage': subtipo_percentages[subtipo],
                            'Detalle': detalle,
                            'Detalle_Percentage': detalle_percentage,
                            'Subelemento': 'N/A',
                            'Subelemento_Percentage': 0,
                            'Tipo_Count': tipo_count,
                            'Subtipo_Count': subtipo_count,
                            'Detalle_Count': detalle_count,
                            'Subelemento_Count': 0
                        })
            else:
                # Handle empty Detalle list
                results.append({
                    'Tipo': tipo,
                    'Tipo_Percentage': tipo_percentages[tipo],
                    'Subtipo': subtipo,
                    'Subtipo_Percentage': subtipo_percentages[subtipo],
                    'Detalle': 'N/A',
                    'Detalle_Percentage': 0,
                    'Subelemento': 'N/A',
                    'Subelemento_Percentage': 0,
                    'Tipo_Count': tipo_count,
                    'Subtipo_Count': subtipo_count,
                    'Detalle_Count': 0,
                    'Subelemento_Count': 0
                })
    
    return pd.DataFrame(results)



st.markdown("""
<style>
    .stApp {
        max-width: 1200px;
        margin: 0 auto;
    }
    .stDataFrame {
        font-size: 16px;
    }
    .st-cb {
        font-size: 20px;
    }
    h1 {
        color: #3366cc;
        font-size: 36px;
        margin-bottom: 20px;
    }
    .stAlert {
        background-color: #f0f2f6;
        padding: 10px;
        border-radius: 5px;
        margin-bottom: 20px;
    }
    /* Add alternating row colors */
    .stDataFrame tbody tr:nth-of-type(even) {
        background-color: #f2f2f2;
    }
    .stDataFrame tbody tr:nth-of-type(odd) {
        background-color: #ffffff;
    }
    /* Ensure the checkbox column doesn't get colored */
    .stDataFrame tbody tr td:first-child {
        background-color: transparent !important;
    }
</style>
""", unsafe_allow_html=True)


def load_all_df():  
    
    
    df_load_dos= load_data()

    if "year_filter" in st.session_state:
        selected_years = st.session_state.year_filter
    else:
        selected_years = []

    if "month_filter" in st.session_state:
        selected_months = st.session_state.month_filter
    else:
        selected_months = []


    if "week_filter" in st.session_state:
        selected_weeks = st.session_state.week_filter
    else:
        selected_weeks = []

    print(selected_months,selected_weeks,selected_years,"datos a filtrar")


    filtered_df = df_load_dos.copy()

    # Apply year filter only if selected_years is not empty
    if selected_years:
        filtered_df = filtered_df[filtered_df['year'].isin(selected_years)]

    # Apply month filter only if selected_months is not empty
    if selected_months:
        filtered_df = filtered_df[filtered_df['month'].isin(selected_months)]

    # Apply week filter only if selected_weeks is not empty
    if selected_weeks:
        filtered_df = filtered_df[filtered_df['week'].isin(selected_weeks)]


    filtered_df = calculate_hierarchical_percentages(filtered_df)

    print(filtered_df.head(60),"esto es fitlerd df")

    return filtered_df




def get_first_non_empty_from_bottom(df, column, start_index):
    for i in range(start_index, -1, -1):
        value = df.iloc[i][column]
        if pd.notna(value) and value != '':
            return value
    return None 





def create_interactive_df(df):

    df_filtrado_datos = calculate_hierarchical_percentages(df)
    df_tipo = df_filtrado_datos.groupby('Tipo').agg({
        'Tipo_Percentage': 'first',
        'Tipo_Count': 'first'
    }).reset_index()

    # ordenadmospara dejar otros temas abajo
    custom_order = ['gestion de cuenta y soporte clientes', 'productos bancarios e info comercial', 'otros temas']
    df_tipo['Tipo'] = pd.Categorical(df_tipo['Tipo'], categories=custom_order, ordered=True)
    df_tipo = df_tipo.sort_values('Tipo')
    df_tipo = df_tipo.reset_index(drop=True)

    
    df_tipo['Percentage'] = df_tipo['Tipo_Percentage'].apply(lambda x: f"{x:.2f}%")
    df_tipo['Count'] = df_tipo['Tipo_Count'].astype(int)
    df_tipo['Subtipo'] = ''
    df_tipo['Detalle'] = ''
    df_tipo["Subelemento"] = ''
    df_tipo['expanded'] = False
    df_tipo['level'] = 'Tipo'
    
    df_tipo = df_tipo[['Tipo', 'Subtipo', 'Detalle','Subelemento' ,'Percentage', 'Count', 'expanded', 'level']]

    print(df_tipo)
    
    return df_tipo

def update_df(expanded_index):

    print("exoande index ", expanded_index)


    df_filtrado_datos = load_all_df()
    #print(df_filtrado_datos.head(60),"esto si que si")


    df_updated = st.session_state.df_interactive.copy()
    if expanded_index is not None and expanded_index != []:
     
        expanded_row = df_updated.iloc[expanded_index]
        
        df_updated.loc[expanded_index, 'expanded'] = not expanded_row['expanded']
        
        if df_updated.loc[expanded_index, 'expanded']:
            
            if expanded_row['level'] == 'Tipo':
                tipo = expanded_row['Tipo']
                df_subtipo = df_filtrado_datos[df_filtrado_datos['Tipo'] == tipo].groupby('Subtipo').agg({
                    'Subtipo_Percentage': 'first',
                    'Subtipo_Count': 'first'
                }).reset_index()
                
                df_subtipo['Tipo'] = ''
                df_subtipo['Detalle'] = ''
                df_subtipo['Subelemento'] = ''  # Add Subelemento column
                df_subtipo['Percentage'] = df_subtipo['Subtipo_Percentage'].apply(lambda x: f"      {x:.2f} %")
                df_subtipo['Count'] = df_subtipo['Subtipo_Count'].astype(int)
                df_subtipo['expanded'] = False
                df_subtipo['level'] = 'Subtipo'
                
                df_subtipo = df_subtipo[['Tipo', 'Subtipo', 'Detalle', 'Subelemento', 'Percentage', 'Count', 'expanded', 'level']]
                
                df_updated = pd.concat([df_updated.iloc[:expanded_index + 1], 
                                        df_subtipo, 
                                        df_updated.iloc[expanded_index + 1:]]).reset_index(drop=True)
            
            elif expanded_row['level'] == 'Subtipo':
                tipo = df_updated.iloc[expanded_index - 1]['Tipo']

                # cehck that tipo is not empty
                if pd.isna(tipo) or tipo == '':
                    tipo= get_first_non_empty_from_bottom(df_updated, 'Tipo', expanded_index - 1)

                subtipo = expanded_row['Subtipo']

                df_detalle = df_filtrado_datos[(df_filtrado_datos['Tipo'] == tipo) & (df_filtrado_datos['Subtipo'] == subtipo)].groupby('Detalle').agg({
                    'Detalle_Percentage': 'first',
                    'Detalle_Count': 'first'
                }).reset_index()
                
                df_detalle['Tipo'] = ''
                df_detalle['Subtipo'] = ''
                df_detalle['Subelemento'] = ''  # Add Subelemento column
                df_detalle['Percentage'] = df_detalle['Detalle_Percentage'].apply(lambda x: f"              {x:.2f} %")
                df_detalle['Count'] = df_detalle['Detalle_Count'].astype(int)
                df_detalle['expanded'] = False
                df_detalle['level'] = 'Detalle'
                
                df_detalle = df_detalle[['Tipo', 'Subtipo', 'Detalle', 'Subelemento', 'Percentage', 'Count', 'expanded', 'level']]
                
                df_updated = pd.concat([df_updated.iloc[:expanded_index + 1], 
                                        df_detalle, 
                                        df_updated.iloc[expanded_index + 1:]]).reset_index(drop=True)
            
            elif expanded_row['level'] == 'Detalle':  # New condition for Detalle level

                
                
                # asegurarse que tippo no es nan
                tipo = df_updated.iloc[expanded_index - 2]['Tipo']
                if pd.isna(tipo) or tipo == '':
                    tipo= get_first_non_empty_from_bottom(df_updated, 'Tipo', expanded_index - 2)

                # asegurarse que subtippo no es nan
                subtipo = df_updated.iloc[expanded_index - 1]['Subtipo']
                
                if pd.isna(subtipo) or subtipo == '':
                    subtipo= get_first_non_empty_from_bottom(df_updated, 'Subtipo', expanded_index - 1)

                detalle = expanded_row['Detalle']

                print(subtipo, "subtipo")

                print(df_filtrado_datos[(df_filtrado_datos['Tipo'] == tipo) & 
                                            (df_filtrado_datos['Subtipo'] == subtipo) & 
                                            (df_filtrado_datos['Detalle'] == detalle)])
                print("-----------------")



        

                df_Subelemento = df_filtrado_datos[(df_filtrado_datos['Tipo'] == tipo) & 
                                            (df_filtrado_datos['Subtipo'] == subtipo) & 
                                            (df_filtrado_datos['Detalle'] == detalle)].groupby('Subelemento').agg({
                    'Subelemento_Percentage': 'first',
                    'Subelemento_Count': 'first'
                }).reset_index()
                
                df_Subelemento['Tipo'] = ''
                df_Subelemento['Subtipo'] = ''
                df_Subelemento['Detalle'] = ''
                df_Subelemento['Percentage'] = df_Subelemento['Subelemento_Percentage'].apply(lambda x: f"                      {x:.2f} %")
                df_Subelemento['Count'] = df_Subelemento['Subelemento_Count'].astype(int)
                df_Subelemento['expanded'] = False
                df_Subelemento['level'] = 'Subelemento'
                
                df_Subelemento = df_Subelemento[['Tipo', 'Subtipo', 'Detalle', 'Subelemento', 'Percentage', 'Count', 'expanded', 'level']]
                
                df_updated = pd.concat([df_updated.iloc[:expanded_index + 1], 
                                        df_Subelemento, 
                                        df_updated.iloc[expanded_index + 1:]]).reset_index(drop=True)
                
        else:
            if expanded_row['level'] == 'Tipo':
                df_updated = df_updated[~((df_updated.index > expanded_index) & 
                                        (df_updated['level'].isin(['Subtipo', 'Detalle', 'Subelemento'])))]
            elif expanded_row['level'] == 'Subtipo':
                df_updated = df_updated[~((df_updated.index > expanded_index) & 
                                        (df_updated['level'].isin(['Detalle', 'Subelemento'])))]
            elif expanded_row['level'] == 'Detalle':
                df_updated = df_updated[~((df_updated.index > expanded_index) & 
                                        (df_updated['level'] == 'Subelemento'))]
        
        st.session_state.df_interactive = df_updated.reset_index(drop=True)


    else:
        print("esta aqui?¿?¿")
        st.session_state.df_interactive = df_updated.reset_index(drop=True)



def on_change():
    print("hola lsss")
    changed_rows = st.session_state.editor.get("edited_rows", {})

    for idx, changes in changed_rows.items():
        print("hla hola ")
        if "expanded" in changes:
            update_df(int(idx))
 


    
    
