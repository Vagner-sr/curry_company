# Libraries
from haversine import haversine
import plotly.express as px
import plotly.graph_objects as go

# Bibliotecas necessarias
import folium
import pandas as pd
from datetime import datetime
import streamlit as st
from PIL import Image
from streamlit_folium import folium_static

st.set_page_config(page_title='Visão Empresa', layout='wide')

# ---------------------------------------------
# Funcoes 
# ---------------------------------------------

def country_maps(df):
    df_aux = df.loc[:, ['City','Road_traffic_density', 'Delivery_location_latitude', 'Delivery_location_longitude']].groupby(['City', 'Road_traffic_density']).median().reset_index()
    
    df_aux = df_aux.head()
    map = folium.Map()
    
    for index, location_info in df_aux.iterrows():
      folium.Marker([location_info['Delivery_location_latitude'],
                    location_info['Delivery_location_longitude']],
                   popup=location_info[['City', 'Road_traffic_density']]).add_to(map)
    folium_static( map, width=2024, height=600)

def order_share_by_week(df):
    df_aux1 = df.loc[:, ['ID', 'week_of_year']].groupby('week_of_year').count().reset_index()
    df_aux2 = df.loc[:, ['Delivery_person_ID', 'week_of_year']].groupby('week_of_year').nunique().reset_index()
    df_aux = pd.merge(df_aux1, df_aux2, how='inner')
    df_aux['Order_by_deliver'] = df_aux['ID'] / df_aux['Delivery_person_ID']
    fig = px.line(df_aux, x='week_of_year', y='Order_by_deliver')
    return fig

def order_by_week(df):
    df['week_of_year'] = df['Order_Date'].dt.strftime('%U')
    df_aux = df.loc[:, ['ID', 'week_of_year']].groupby('week_of_year').count().reset_index()
    fig = px.line(df_aux, x='week_of_year', y="ID")
    return fig

def traffic_order_city(df):
    df_aux = df.loc[:, ['ID', 'City', 'Road_traffic_density']].groupby(['City', 'Road_traffic_density']).count().reset_index()
    fig = px.scatter(df_aux, x='City', y="Road_traffic_density", size='ID', color='City')
    return fig

def traffic_order_share(df):
    df_aux = df.loc[:, ['ID',   'Road_traffic_density']].groupby('Road_traffic_density').count().reset_index()
    df_aux['Delivery_percentage'] = df_aux['ID'] / df_aux['ID'].sum()
    fig = px.pie(df_aux, values = 'Delivery_percentage', names = 'Road_traffic_density')
    return fig         

def order_metric(df):
    df_aux = df.loc[:, ['ID', 'Order_Date']].groupby('Order_Date').count().reset_index()
    df_aux.columns = ['order_date', 'order_quantity']
    # Grafico
    fig = px.bar(df_aux, x='order_date', y='order_quantity')
    return fig

def clean_code(df):
    """ Esta funca tem a responsabilidade de limpar o dataframe
        Tipos de limpeza:
        1. Remocao dos dados NaN
        2. Mudanca do tipo da coluna de dados
        3. Remocao dos espacos das variaveis
        4. Formatacao da coluna de datas
        5. Limpeza da coluna de tempo (remocao do texto da variavel numerica)

        input: Dataframe
        Output: Dataframe    
    """
    # Removendo o espaço vazio da String
    df.loc[:,'ID'] = df.loc[:,'ID'].str.strip()
    df.loc[:, "Delivery_person_ID"] = df.loc[:, "Delivery_person_ID"].str.strip()
    df.loc[:, "Type_of_order"] = df.loc[:, "Type_of_order"].str.strip()
    df.loc[:,"Type_of_vehicle"] = df.loc[:,"Type_of_vehicle"].str.strip()
    df.loc[:,"City"] = df.loc[:,"City"].str.strip()
    df.loc[:,"Road_traffic_density"] = df.loc[:,"Road_traffic_density"].str.strip()
    df.loc[:,"Festival"] = df.loc[:,"Festival"].str.strip()
    
    # Excluindo as linhas com NaN
    linhas_vazias = df['Delivery_person_Age'] != 'NaN '
    df = df.loc[linhas_vazias,:]
    
    linhas_vazias2 = df['Weatherconditions'] != 'conditions NaN'
    df = df.loc[linhas_vazias2, :]
    
    linhas_vazias3 = df['multiple_deliveries'] != 'NaN '
    df = df.loc[linhas_vazias3,:]
    
    linhas_vazias4 = df['City'] != 'NaN'
    df = df.loc[linhas_vazias4, :]
    
    linhas_vazias5 = df['Festival'] != 'NaN '
    df = df.loc[linhas_vazias5, :]
    
    #Convertendo texto/categoria/strings para numeros inteiros e decimais
    df['Delivery_person_Age'] = df['Delivery_person_Age'].astype(int)
    df['Delivery_person_Ratings'] = df['Delivery_person_Ratings'].astype(float)
    df['multiple_deliveries'] = df['multiple_deliveries'].astype(int)
    
    # Convertendo texto para data
    df['Order_Date'] = pd.to_datetime(df['Order_Date'], format = '%d-%m-%Y')
    
    # Limpando a coluna de Time Taken 
    df['Time_taken(min)'] = df['Time_taken(min)'].apply(lambda x: x.split('(min) ')[1])
    df['Time_taken(min)'] = df['Time_taken(min)'].astype(int)
    
    return df


# ------------------------------------ Inicio da Estrutura logica do codigo

# --------------------------
# Import dataset
# --------------------------
df_raw = pd.read_csv('dataset/train.csv')

# --------------------------
# Limpando os dados
# --------------------------
df = clean_code(df_raw)

# =============================================================
# Barra lateral
# =============================================================
st.header('Marketplace - Visão Cliente')

#image_path = 'dataset/logo.png'
image = Image.open('logo.png')
st.sidebar.image(image, width=120)

st.sidebar.markdown('# Cury Company')
st.sidebar.markdown('## Fastest delivery in town')
st.sidebar.markdown("""---""")

st.sidebar.markdown('## Selecione uma data limite')

date_slider = st.sidebar.slider(
    'Até qual valor?',
    value = datetime(2022, 4, 13),
    min_value = datetime(2022, 2, 11),
    max_value = datetime(2022, 4, 6),
    format= 'DD-MM-YYYY')

st.header(date_slider)
st.sidebar.markdown("""---""")


traffic_option = st.sidebar.multiselect(
    'Quais as condições de trânsito?',
    ['Low', 'Medium', 'High', 'Jam'],
    default = ['Low', 'Medium', 'High', 'Jam'])

st.sidebar.markdown("""---""")
st.sidebar.markdown('### Powered by Vagner Rodrigues')

# Filtro de data
linhas_selecionadas = df['Order_Date'] < date_slider
df = df.loc[linhas_selecionadas, :]

# Filtro de transito
linhas_selecionadas = df['Road_traffic_density'].isin(traffic_option)
df = df.loc[linhas_selecionadas, :]


# =============================================================
# Layout no Streamleat
# =============================================================
tab1, tab2, tab3 = st.tabs(['Visão Gerencial', 'Visão Tática', 'Visão Geográfica'])

with tab1:
    with st.container():
        fig = order_metric(df)
        st.markdown('# Orders by day')
        st.plotly_chart (fig, use_container_width = True)
        

    with st.container():
        col1, col2 = st.columns (2)
        
        with col1:
            fig = traffic_order_share(df)
            st.header('Traffic Order Share')
            st.plotly_chart (fig, use_container_width = True)
            
        with col2:
            st.header('Traffic Order City')
            fig = traffic_order_city(df)
            st.plotly_chart (fig, use_container_width = True)
            

with tab2:
    with st.container():
        st.markdown('# Order by Week')
        fig = order_by_week(df)
        st.plotly_chart(fig, user_container_width = True)
        

    with st.container():
        st.markdown('# Order Share by Week')
        fig = order_share_by_week(df)
        st.plotly_chart(fig, user_container_width = True)

        
with tab3:
    st.markdown('# Country Maps')
    country_maps(df)
        
        
















