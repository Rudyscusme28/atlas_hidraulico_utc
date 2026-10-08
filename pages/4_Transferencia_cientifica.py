import plotly.express as px
import streamlit as st
from src.core import configurar,cabecera,cargar,filtrar
configurar('Transferencia científica','🔬'); cabecera('Transferencia científica','Trazabilidad entre proyectos hidráulicos, productos técnicos y publicaciones')
p,pub,rel=cargar(); df=filtrar(p); rf=rel[rel.ID_Proyecto.isin(df.ID_Proyecto)].copy(); pf=pub[pub.ID_Articulo.isin(rf.ID_Articulo.dropna().unique())]
n=len(df); pp=rf.ID_Proyecto.nunique(); c1,c2,c3,c4=st.columns(4); c1.metric('Artículos asociados',pf.ID_Articulo.nunique()); c2.metric('Proyectos vinculados',f'{pp} de {n}'); c3.metric('ITI documental',f'{pp/n:.1%}' if n else '0%'); c4.metric('Relaciones',len(rf))
if not rf.empty:
 t=rf.merge(df[['ID_Proyecto','Nombre_Proyecto','Producto_Principal']],on='ID_Proyecto',how='left').merge(pub,on='ID_Articulo',how='left')
 if 'DOI' in t: t['Enlace_DOI']='https://doi.org/'+t.DOI.fillna('').astype(str)
 cols=[c for c in ['Nombre_Proyecto','Producto_Principal','Titulo','Año','Revista','Tipo_Relacion','Enlace_DOI'] if c in t]
 st.dataframe(t[cols].fillna('-'),use_container_width=True,hide_index=True,column_config={'Enlace_DOI':st.column_config.LinkColumn('DOI',display_text='Abrir')})
 x=rf.groupby('Tipo_Relacion',as_index=False).size().rename(columns={'size':'Relaciones'}); fig=px.bar(x,x='Relaciones',y='Tipo_Relacion',orientation='h',text='Relaciones',color='Tipo_Relacion',title='Tipos de relación proyecto-publicación'); fig.update_layout(showlegend=False); st.plotly_chart(fig,use_container_width=True)
else: st.info('No existen publicaciones para la selección actual.')
