import plotly.express as px
import streamlit as st
from src.core import configurar,cabecera,cargar,filtrar,entero,PALETA
configurar('Atlas Hidráulico UTC')
cabecera('Atlas Geoespacial de Vinculación en Ingeniería Hidráulica','Resultados territoriales, académicos, sociales, técnicos y científicos vinculados al recurso hídrico')
p,pub,rel=cargar(); df=filtrar(p); rf=rel[rel.ID_Proyecto.isin(df.ID_Proyecto)]
n=df.ID_Proyecto.nunique(); est=df.Estudiantes.sum(min_count=1); hp=(df.Estudiantes.fillna(0)*df.Horas_Vinculacion.fillna(0)).sum()
c1,c2,c3,c4=st.columns(4); c1.metric('Proyectos',n); c2.metric('Estudiantes',int(est) if est==est else 0); c3.metric('Horas-persona',entero(hp)); c4.metric('Artículos asociados',rf.ID_Articulo.nunique())
a,b=st.columns(2)
with a:
 x=df.groupby('Periodo_Academico',as_index=False).ID_Proyecto.nunique(); fig=px.bar(x,x='Periodo_Academico',y='ID_Proyecto',text='ID_Proyecto',title='Evolución por período',color_discrete_sequence=['#087E8B']); fig.update_layout(showlegend=False); st.plotly_chart(fig,use_container_width=True)
with b:
 x=df.groupby('Linea_Tematica',as_index=False).ID_Proyecto.nunique().sort_values('ID_Proyecto'); fig=px.bar(x,x='ID_Proyecto',y='Linea_Tematica',orientation='h',text='ID_Proyecto',color='Linea_Tematica',color_discrete_sequence=PALETA,title='Proyectos por línea temática'); fig.update_layout(showlegend=False); st.plotly_chart(fig,use_container_width=True)
st.info('Navegue por las páginas laterales para consultar territorio, alcance social, capacidades técnicas, transferencia científica, fichas de proyectos y metodología.')
