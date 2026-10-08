import pandas as pd
import plotly.express as px
import streamlit as st
from src.core import configurar,cabecera,cargar,filtrar
configurar('Capacidades técnicas','⚙️'); cabecera('Capacidades técnicas aplicadas','Levantamiento, diseño, modelación, aforos, calidad del agua y representación territorial')
p,_,_=cargar(); df=filtrar(p); n=len(df)
h={'Planos':'Tiene_Planos','SIG':'Tiene_SIG','Civil 3D':'Tiene_Civil3D','EPANET':'Tiene_EPANET','Modelación':'Tiene_Modelacion','Aforos':'Tiene_Aforos','Calidad del agua':'Tiene_Calidad_Agua','Topografía':'Tiene_Topografia'}
f=[c for c in h.values() if c not in df.columns]
if f: st.error(f'Faltan columnas: {f}'); st.stop()
r=[]
for nom,col in h.items():
 q=int(pd.to_numeric(df[col],errors='coerce').fillna(0).eq(1).sum()); r.append({'Herramienta':nom,'Proyectos':q,'Porcentaje':100*q/n if n else 0})
r=pd.DataFrame(r)
for inicio in (0,4):
 cs=st.columns(4)
 for j in range(4):
  x=r.iloc[inicio+j]; cs[j].metric(x.Herramienta,f'{int(x.Proyectos)} de {n}',f'{x.Porcentaje:.1f}%',delta_color='off')
fig=px.bar(r.sort_values('Proyectos'),x='Proyectos',y='Herramienta',orientation='h',text='Proyectos',color='Porcentaje',range_color=[0,100],color_continuous_scale=['#D8F3F1','#087E8B'],title='Presencia documental de capacidades técnicas'); fig.update_xaxes(dtick=1); st.plotly_chart(fig,use_container_width=True)
