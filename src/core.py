from pathlib import Path
import pandas as pd
import streamlit as st
BASE=Path(__file__).resolve().parents[1]
ARCHIVO=BASE/'data'/'base_datos_rc.xlsx'
PALETA=['#006D77','#118AB2','#2A9D8F','#457B9D','#00A6A6','#6A994E','#4D908E','#577590','#F4A261']

def configurar(titulo,icono='💧'):
    st.set_page_config(page_title=titulo,page_icon=icono,layout='wide')
    css='<style>.block-container{padding-top:1.3rem}[data-testid="stMetric"]{background:white;border:1px solid #CFE8EC;padding:14px;border-radius:14px}h1,h2,h3{color:#075A66}.hero{background:linear-gradient(120deg,#064E5B,#087E8B,#3BA7B2);padding:26px;border-radius:20px;color:white;margin-bottom:18px}.hero h1{color:white;margin:0;font-size:2.05rem}.hero p{margin:.45rem 0 0;opacity:.92}</style>'
    st.markdown(css,unsafe_allow_html=True)

def cabecera(titulo,subtitulo):
    st.markdown('<div class="hero"><h1>'+titulo+'</h1><p>'+subtitulo+'</p></div>',unsafe_allow_html=True)

def valor(v):
    if pd.isna(v) or str(v).strip()=='': return '-'
    if isinstance(v,float) and v.is_integer(): return str(int(v))
    return str(v)

def entero(v):
    return '-' if pd.isna(v) else f'{int(v):,}'.replace(',','.')

@st.cache_data(show_spinner=False)
def cargar():
    if not ARCHIVO.exists(): raise FileNotFoundError(f'No se encontró {ARCHIVO}')
    p=pd.read_excel(ARCHIVO,sheet_name='TB_PROYECTOS',engine='openpyxl')
    pub=pd.read_excel(ARCHIVO,sheet_name='TB_PUBLICACIONES',engine='openpyxl')
    rel=pd.read_excel(ARCHIVO,sheet_name='TB_PROYECTO_PUBLICACION',engine='openpyxl')
    for c in ['Latitud','Longitud','Estudiantes','Horas_Vinculacion','Beneficiarios_Valor']:
        if c in p: p[c]=pd.to_numeric(p[c],errors='coerce')
    return p,pub,rel

def filtrar(df):
    st.sidebar.markdown('## 💧 Filtros')
    ps=sorted(df.Periodo_Academico.dropna().unique())
    ls=sorted(df.Linea_Tematica.dropna().unique())
    sp=st.sidebar.multiselect('Período académico',ps,default=ps)
    sl=st.sidebar.multiselect('Línea temática',ls,default=ls)
    out=df[df.Periodo_Academico.isin(sp)&df.Linea_Tematica.isin(sl)].copy()
    if out.empty: st.warning('No existen proyectos para los filtros seleccionados.'); st.stop()
    return out
