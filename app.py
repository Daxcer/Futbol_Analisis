import streamlit as st

pages = {
    "Navegación": [ 
        st.Page("contenido/inicio.py", title="Inicio"), 
        st.Page("contenido/analisis_de_jugadores.py", title="Análisis de los Jugadores"), 
        st.Page("contenido/analisis_por_equipo.py", title="Análisis por Equipo"), 
        st.Page("contenido/comparacion_entre_equipos.py", title="Comparación entre Equipos"), 
        st.Page("contenido/global_liga.py", title="Global Liga") 
    ]  
}

pg = st.navigation(pages)

pg.run()