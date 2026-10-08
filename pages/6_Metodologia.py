import pandas as pd
import plotly.express as px
import streamlit as st
from src.core import configurar,cabecera,cargar,filtrar
configurar('Metodología y calidad','📘'); cabecera('Metodología y calidad documental','Cobertura, criterios de inclusión, reglas de tratamiento y limitaciones')
p,_,rel=cargar(); df=filtrar(p); n=len(df)
cond={'Estudiantes':df.Estudiantes.notna(),'Beneficiarios':df.Beneficiarios_Valor.notna(),'Coordenadas':df.Latitud.notna()&df.Longitud.notna(),'Producto técnico':df.Producto_Principal.notna(),'Entidad':df.Entidad_Beneficiaria.notna(),'Publicación registrada':df.ID_Proyecto.isin(rel.ID_Proyecto)}
r=[]
for nom,c in cond.items():
 q=int(c.fillna(False).sum()); r.append({'Variable':nom,'Con dato':q,'Sin dato':n-q,'Cobertura':100*q/n if n else 0})
r=pd.DataFrame(r); c1,c2,c3,c4=st.columns(4); c1.metric('Universo inicial',24); c2.metric('Cohorte',21); c3.metric('Excluidos',3); c4.metric('EPSG',4326)
fig=px.bar(r.sort_values('Cobertura'),x='Cobertura',y='Variable',orientation='h',text='Cobertura',color='Cobertura',range_color=[0,100],color_continuous_scale=['#F4A261','#E9C46A','#087E8B'],title='Cobertura documental por variable'); fig.update_traces(texttemplate='%{text:.1f}%'); fig.update_xaxes(range=[0,105],ticksuffix='%'); st.plotly_chart(fig,use_container_width=True)
st.dataframe(r,use_container_width=True,hide_index=True)
st.markdown("""### Criterios
- Universo inicial: **24**; cohorte: **21**; excluidos: **3**.
- Horas por estudiante: **160** en los períodos iniciales y **240** desde 2024.
- Las unidades sociales se presentan por separado.
- Coordenadas en **WGS 84 / EPSG:4326**.
- El símbolo **-** representa dato no disponible.
- Los resultados describen evidencia documental y no prueban impacto causal ni desempeño hidráulico en operación.
""")
