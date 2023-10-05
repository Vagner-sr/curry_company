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

st.set_page_config(page_title='Visão Entregadores', layout='wide')

# ---------------------------------------------
# Funcoes 
# ---------------------------------------------

def top_delivers(df, top_asc):
    df2 = ( df.loc[:,['Delivery_person_ID', 'City', 'Time_taken(min)']]
       .groupby(['City','Delivery_person_ID']).max().sort_values(['City', 'Time_taken(min)'], ascending = top_asc).reset_index() )
    df_aux01 = df2.loc[df2['City'] == 'Metropolitian', :].head(10)
    df_aux02 = df2.loc[df2['City'] == 'Urban', :].head(10)
    df_aux03 = df2.loc[df2['City'] == 'Semi-Urban', :].head(10)
    df3 = pd.concat( [df_aux01, df_aux02, df_aux03] ).reset_index(drop=True)
    
    return df3

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

# Import dataset
df_raw = pd.read_csv('dataset/train.csv')

# Cleaning dataset
df = clean_code(df_raw)


# =============================================================
# Barra lateral
# =============================================================
st.header('Marketplace - Visão Entregadores')

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

tab1, tab2, tab3 = st.tabs(['Visão Gerencial', '_' , '_'])

with tab1:
    with st.container():
        st.title('Overal Metrics')
        col1, col2, col3, col4 = st.columns(4, gap='large')
        with col1:
            # A maior idade entre os entregadores
            maior_idade = df.loc[:, "Delivery_person_Age"].max()
            col1.metric('Maior idade', maior_idade)

        with col2:
            # A menor idade entre os entregadores
            menor_idade = df.loc[:, "Delivery_person_Age"].min()
            col2.metric('Menor idade', menor_idade)
            
        with col3:
            # Veiculo com a melhor condicao
            melhor_condicao = df.loc[:, 'Vehicle_condition'].max()
            col3.metric('Veiculo com a melhor condicao', melhor_condicao)
            
        with col4:
            # Veiculo com a pior condicao
            pior_condicao = df.loc[:, 'Vehicle_condition'].min()
            col4.metric('Veiculo com a pior condicao', pior_condicao)
            
    with st.container():
        st.markdown("""___""")
        st.subheader('Avaliacoes')
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown('##### Avaliacao media por entregador')
            rating_med = (df.loc[:,['Delivery_person_ID', 'Delivery_person_Ratings']]
                          .groupby('Delivery_person_ID').median().reset_index())
            st.dataframe(rating_med)
            
        with col2:
            st.markdown('##### Avaliacao media por transito')
            
            ava_media_e_padrao = ( df.loc[:,['Road_traffic_density', 'Delivery_person_Ratings']]
                                  .groupby('Road_traffic_density')
                                  .agg({'Delivery_person_Ratings': ['mean', 'std']}) )

            ava_media_e_padrao.columns = ['delivery_mean', 'delivery_std']
            ava_media_e_padrao = ava_media_e_padrao.reset_index()
            st.dataframe(ava_media_e_padrao)
            
            st.markdown('##### Avaliacao media por clima')
            
            ava_media_e_padrao_clima = ( df.loc[:,['Weatherconditions', 'Delivery_person_Ratings']]
                                        .groupby('Weatherconditions')
                                        .agg({'Delivery_person_Ratings': ['mean', 'std']}) )

            ava_media_e_padrao_clima.columns = ['delivery_mean', 'delivery_std']
            ava_media_e_padrao_clima = ava_media_e_padrao_clima.reset_index()
            st.dataframe(ava_media_e_padrao_clima)
            
    with st.container():
        st.markdown("""___""")
        st.title('Velocidade de Entrega')
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader('Top entregadores mais rapidos')
            df3 = top_delivers(df, top_asc=True)
            st.dataframe(df3)
            
        with col2:
            st.subheader('Top entregadores mais lentos')
            df3 = top_delivers(df, top_asc=False)
            st.dataframe(df3)
            
            
                
            
            

            
            
            
            
            



























