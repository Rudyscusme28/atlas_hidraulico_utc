import pandas as pd
import plotly.express as px
import streamlit as st
from src.core import configurar,cabecera,cargar,filtrar,valor
configurar('Consulta de proyectos','📋'); cabecera('Consulta individual de proyectos','Ficha territorial, académica, social y técnica de cada intervención')
p,_,_=cargar(); df=filtrar(p); opciones=(df.ID_Proyecto.astype(str)+' | '+df.Nombre_Proyecto.astype(str)).sort_values().tolist(); s=st.selectbox('Proyecto',opciones); pid=s.split(' | ',1)[0]; f=df[df.ID_Proyecto.astype(str).eq(pid)].iloc[0]
a,b=st.columns(2)
with a:
 st.subheader('Identificación')
 for e,c in [('ID','ID_Proyecto'),('Nombre','Nombre_Proyecto'),('Período','Periodo_Academico'),('Línea','Linea_Tematica'),('Entidad','Entidad_Beneficiaria')]: st.write(f'**{e}:** {valor(f.get(c))}')
with b:
 st.subheader('Localización')
 for e,c in [('Provincia','Provincia'),('Cantón','Canton'),('Parroquia','Parroquia'),('Comunidad','Comunidad')]: st.write(f'**{e}:** {valor(f.get(c))}')
c1,c2,c3=st.columns(3); c1.metric('Estudiantes',valor(f.get('Estudiantes'))); c2.metric('Horas por estudiante',valor(f.get('Horas_Vinculacion'))); c3.metric('Beneficiarios',valor(f.get('Beneficiarios_Valor'))+' '+valor(f.get('Beneficiarios_Unidad')))
st.subheader('Producto técnico principal'); st.info(valor(f.get('Producto_Principal')))
if pd.notna(f.Latitud) and pd.notna(f.Longitud):
 u=pd.DataFrame({'Proyecto':[f.Nombre_Proyecto],'Latitud':[f.Latitud],'Longitud':[f.Longitud]}); fig=px.scatter_map(u,lat='Latitud',lon='Longitud',hover_name='Proyecto',center={'lat':f.Latitud,'lon':f.Longitud},zoom=12,height=460,map_style='open-street-map'); fig.update_traces(marker={'size':20,'color':'#D96C3B'}); st.plotly_chart(fig,use_container_width=True)
