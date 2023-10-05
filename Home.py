import streamlit as st
from PIL import Image

st.set_page_config(
    page_title='Home', layout='wide'
)



image = Image.open('logo.png')
st.sidebar.image(image, width=120)

st.sidebar.markdown('# Cury Company')
st.sidebar.markdown('## Fastest delivery in town')
st.sidebar.markdown("""---""")

st.write("# Curry Company Growth Dashboard")

st.markdown(
    """
    Growth Dashboard foi construído para acompanhar as metricas de crescimentos dos entregadores e restaurantes    
    """
)