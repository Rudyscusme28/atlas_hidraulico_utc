import plotly.express as px
import streamlit as st
from src.core import configurar,cabecera,cargar,filtrar,PALETA
configurar('Territorio hídrico','🗺️'); cabecera('Territorio hídrico','Localización de intervenciones vinculadas al agua, riego, hidrología y saneamiento')
p,_,_=cargar(); df=filtrar(p).dropna(subset=['Latitud','Longitud']); df=df[df.Latitud.between(-1.5,.2)&df.Longitud.between(-79.2,-77.8)]
st.metric('Puntos cartografiados',len(df)); fig=px.scatter_map(df,lat='Latitud',lon='Longitud',color='Linea_Tematica',hover_name='Nombre_Proyecto',hover_data={'Periodo_Academico':True,'Entidad_Beneficiaria':True,'Comunidad':True,'Producto_Principal':True,'Latitud':False,'Longitud':False},zoom=8,height=720,map_style='open-street-map',color_discrete_sequence=PALETA); fig.update_traces(marker={'size':15}); st.plotly_chart(fig,use_container_width=True)
