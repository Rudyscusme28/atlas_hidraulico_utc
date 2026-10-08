import plotly.express as px
import streamlit as st
from src.core import configurar,cabecera,cargar,filtrar,entero
configurar('Alcance social','🌊'); cabecera('Alcance social del recurso hídrico','Cobertura documentada, manteniendo separadas personas, usuarios y familias')
p,_,_=cargar(); df=filtrar(p)
def suma(u): return df.loc[df.Beneficiarios_Unidad.eq(u),'Beneficiarios_Valor'].sum(min_count=1)
c1,c2,c3,c4=st.columns(4); c1.metric('Personas / habitantes',entero(suma('Personas/Habitantes'))); c2.metric('Usuarios',entero(suma('Usuarios'))); c3.metric('Familias',entero(suma('Familias'))); c4.metric('Proyectos con dato',f'{df.Beneficiarios_Valor.notna().sum()} de {len(df)}')
u=sorted(df.loc[df.Beneficiarios_Valor.notna()&df.Beneficiarios_Unidad.notna(),'Beneficiarios_Unidad'].astype(str).unique())
if u:
 s=st.selectbox('Unidad de análisis',u); x=df[df.Beneficiarios_Unidad.eq(s)&df.Beneficiarios_Valor.notna()].sort_values('Beneficiarios_Valor'); fig=px.bar(x,x='Beneficiarios_Valor',y='Nombre_Proyecto',orientation='h',text='Beneficiarios_Valor',color='Linea_Tematica',title=f'Beneficiarios por proyecto ({s})'); st.plotly_chart(fig,use_container_width=True)
st.info('Las unidades sociales no se suman entre sí. Un dato ausente no equivale a cero.')
