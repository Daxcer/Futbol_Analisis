import streamlit as st

pages = {
    "Navegación": [ 
        st.Page("contenido/inicio.py", title="Inicio"), 
        st.Page("contenido/analisis_de_jugadores.py", title="Análisis de los Jugadores"), 
    ]  
}

pg = st.navigation(pages)

pg.run()