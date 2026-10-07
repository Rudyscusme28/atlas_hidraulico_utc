from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

# CONFIGURACIÓN GENERAL

st.set_page_config(
    page_title="Atlas Hidráulico UTC",
    page_icon="💧",
    layout="wide",
)

# FUNCIONES AUXILIARES

def mostrar_valor(valor):
    """
    Devuelve un guion cuando el dato está vacío.

    El símbolo "-" representa información no disponible
    y no equivale a cero.
    """

    if pd.isna(valor):
        return "-"

    if isinstance(valor, float) and valor.is_integer():
        return str(int(valor))

    texto = str(valor).strip()

    if texto == "":
        return "-"

    return texto

# RUTA DE LA BASE DE DATOS

RUTA_EXCEL = Path("data") / "base_datos_rc.xlsx"

# ENCABEZADO

st.title(
    "Atlas Geoespacial de Vinculación "
    "en Ingeniería Hidráulica"
)

st.caption(
    "Universidad Técnica de Cotopaxi"
)

# COMPROBACIÓN DEL ARCHIVO

if not RUTA_EXCEL.exists():
    st.error(
        "No se encontró el archivo "
        "`data/base_datos_rc.xlsx`."
    )

    st.info(
        "Compruebe que el archivo se encuentre dentro "
        "de la carpeta `data` y que el nombre coincida "
        "exactamente."
    )

    st.stop()

# CARGA DE LA BASE

try:
    proyectos = pd.read_excel(
        RUTA_EXCEL,
        sheet_name="TB_PROYECTOS",
        engine="openpyxl",
    )

except ValueError:
    st.error(
        "No se encontró la hoja `TB_PROYECTOS` "
        "dentro del archivo Excel."
    )
    st.stop()

except Exception as error:
    st.error(
        "Ocurrió un error al leer la base de datos."
    )
    st.exception(error)
    st.stop()

# VALIDACIÓN DE COLUMNAS

columnas_requeridas = [
    "ID_Proyecto",
    "Periodo_Academico",
    "Nombre_Proyecto",
    "Entidad_Beneficiaria",
    "Tipo_Entidad",
    "Provincia",
    "Canton",
    "Parroquia",
    "Comunidad",
    "Linea_Tematica",
    "Producto_Principal",
    "Estudiantes",
    "Horas_Vinculacion",
    "Beneficiarios_Valor",
    "Beneficiarios_Unidad",
    "Latitud",
    "Longitud",
]

columnas_ausentes = [
    columna
    for columna in columnas_requeridas
    if columna not in proyectos.columns
]

if columnas_ausentes:
    st.error(
        "La base no contiene todas las columnas requeridas."
    )

    st.write(
        "Columnas ausentes:",
        columnas_ausentes,
    )

    st.stop()

# CONVERSIÓN Y VALIDACIÓN DE DATOS

proyectos["Latitud"] = pd.to_numeric(
    proyectos["Latitud"],
    errors="coerce",
)

proyectos["Longitud"] = pd.to_numeric(
    proyectos["Longitud"],
    errors="coerce",
)

proyectos["Estudiantes"] = pd.to_numeric(
    proyectos["Estudiantes"],
    errors="coerce",
)

proyectos["Horas_Vinculacion"] = pd.to_numeric(
    proyectos["Horas_Vinculacion"],
    errors="coerce",
)

proyectos["Beneficiarios_Valor"] = pd.to_numeric(
    proyectos["Beneficiarios_Valor"],
    errors="coerce",
)


# Comprobar que existen 21 proyectos
if len(proyectos) != 21:
    st.warning(
        f"La base contiene {len(proyectos)} filas. "
        "La cohorte esperada contiene 21 proyectos."
    )


# Comprobar identificadores duplicados
if proyectos["ID_Proyecto"].duplicated().any():
    identificadores_duplicados = proyectos.loc[
        proyectos["ID_Proyecto"].duplicated(
            keep=False
        ),
        "ID_Proyecto",
    ].tolist()

    st.error(
        "Se encontraron identificadores de proyecto "
        "duplicados."
    )

    st.write(
        identificadores_duplicados
    )

    st.stop()


# MENSAJE DE CARGA

st.success(
    f"Base cargada correctamente: "
    f"{len(proyectos)} proyectos."
)

# FILTROS LATERALES

st.sidebar.header("Filtros de consulta")


# Filtro por período académico
periodos_disponibles = sorted(
    proyectos["Periodo_Academico"]
    .dropna()
    .unique()
)

periodos_seleccionados = st.sidebar.multiselect(
    label="Período académico",
    options=periodos_disponibles,
    default=periodos_disponibles,
)


# Filtro por línea temática
lineas_disponibles = sorted(
    proyectos["Linea_Tematica"]
    .dropna()
    .unique()
)

lineas_seleccionadas = st.sidebar.multiselect(
    label="Línea temática",
    options=lineas_disponibles,
    default=lineas_disponibles,
)


# Aplicar filtros
datos_filtrados = proyectos[
    proyectos["Periodo_Academico"].isin(
        periodos_seleccionados
    )
    & proyectos["Linea_Tematica"].isin(
        lineas_seleccionadas
    )
].copy()


# Interrumpir presentación si no existen coincidencias
if datos_filtrados.empty:
    st.warning(
        "No existen proyectos que coincidan "
        "con los filtros seleccionados."
    )

    st.stop()

# INDICADORES GENERALES

total_proyectos = datos_filtrados[
    "ID_Proyecto"
].nunique()

total_estudiantes = datos_filtrados[
    "Estudiantes"
].sum(
    min_count=1
)

horas_persona = (
    datos_filtrados["Estudiantes"].fillna(0)
    * datos_filtrados[
        "Horas_Vinculacion"
    ].fillna(0)
).sum()


# Mostrar tarjetas
columna_1, columna_2, columna_3 = st.columns(3)

with columna_1:
    st.metric(
        label="Proyectos incluidos",
        value=total_proyectos,
    )

with columna_2:
    st.metric(
        label="Estudiantes documentados",
        value=(
            int(total_estudiantes)
            if pd.notna(total_estudiantes)
            else 0
        ),
    )

with columna_3:
    st.metric(
        label="Horas-persona documentadas",
        value=f"{int(horas_persona):,}".replace(
            ",",
            ".",
        ),
    )

# ALCANCE SOCIAL DOCUMENTADO

st.subheader(
    "Alcance social documentado"
)


# Personas o habitantes
beneficiarios_personas = datos_filtrados.loc[
    datos_filtrados["Beneficiarios_Unidad"]
    == "Personas/Habitantes",
    "Beneficiarios_Valor",
].sum(
    min_count=1
)


# Usuarios
beneficiarios_usuarios = datos_filtrados.loc[
    datos_filtrados["Beneficiarios_Unidad"]
    == "Usuarios",
    "Beneficiarios_Valor",
].sum(
    min_count=1
)


# Familias
beneficiarios_familias = datos_filtrados.loc[
    datos_filtrados["Beneficiarios_Unidad"]
    == "Familias",
    "Beneficiarios_Valor",
].sum(
    min_count=1
)


# Proyectos que sí tienen un valor documentado
proyectos_con_beneficiarios = datos_filtrados.loc[
    datos_filtrados["Beneficiarios_Valor"].notna(),
    "ID_Proyecto",
].nunique()


# Función de formato para las tarjetas
def formatear_indicador(valor):
    if pd.isna(valor):
        return "-"

    return f"{int(valor):,}".replace(
        ",",
        ".",
    )


# Mostrar las cuatro tarjetas
social_columna_1, social_columna_2, social_columna_3, social_columna_4 = (
    st.columns(4)
)


with social_columna_1:
    st.metric(
        label="Personas / habitantes",
        value=formatear_indicador(
            beneficiarios_personas
        ),
    )


with social_columna_2:
    st.metric(
        label="Usuarios",
        value=formatear_indicador(
            beneficiarios_usuarios
        ),
    )


with social_columna_3:
    st.metric(
        label="Familias",
        value=formatear_indicador(
            beneficiarios_familias
        ),
    )


with social_columna_4:
    st.metric(
        label="Proyectos con dato social",
        value=(
            f"{proyectos_con_beneficiarios}"
            f" de {total_proyectos}"
        ),
    )


st.caption(
    "Las cantidades se presentan por unidad. "
    "Personas/habitantes, usuarios y familias "
    "no se suman entre sí."
)

# GRÁFICO POR PERÍODO ACADÉMICO

proyectos_por_periodo = (
    datos_filtrados.groupby(
        "Periodo_Academico",
        as_index=False,
    )["ID_Proyecto"]
    .nunique()
    .rename(
        columns={
            "ID_Proyecto": "Numero_Proyectos"
        }
    )
)


orden_periodos = [
    "2023-A",
    "2023-B",
    "2024-A",
    "2024-B",
    "2025-A",
]


figura_periodos = px.bar(
    proyectos_por_periodo,
    x="Periodo_Academico",
    y="Numero_Proyectos",
    category_orders={
        "Periodo_Academico": orden_periodos
    },
    text="Numero_Proyectos",
    title="Proyectos por período académico",
    labels={
        "Periodo_Academico": "Período académico",
        "Numero_Proyectos": "Número de proyectos",
    },
)


figura_periodos.update_traces(
    textposition="outside",
    marker_color="#0B7285",
)


figura_periodos.update_layout(
    showlegend=False,
    xaxis_title="Período académico",
    yaxis_title="Número de proyectos",
    margin={
        "l": 20,
        "r": 20,
        "t": 70,
        "b": 20,
    },
)


st.plotly_chart(
    figura_periodos,
    use_container_width=True,
)

# MAPA TERRITORIAL

st.subheader(
    "Mapa territorial de los proyectos"
)


# Conservar únicamente proyectos con coordenadas
datos_mapa = datos_filtrados.dropna(
    subset=[
        "Latitud",
        "Longitud",
    ]
).copy()


# Verificar rango geográfico general
datos_mapa = datos_mapa[
    datos_mapa["Latitud"].between(
        -1.50,
        0.20,
    )
    & datos_mapa["Longitud"].between(
        -79.20,
        -77.80,
    )
].copy()


st.caption(
    f"Puntos representados en el mapa: "
    f"{len(datos_mapa)}"
)


if datos_mapa.empty:
    st.warning(
        "Los proyectos seleccionados no disponen "
        "de coordenadas válidas."
    )

else:
    # Campo auxiliar para controlar el tamaño
    datos_mapa["Tamano_Marcador"] = 10

    figura_mapa = px.scatter_map(
        datos_mapa,
        lat="Latitud",
        lon="Longitud",
        color="Linea_Tematica",
        size="Tamano_Marcador",
        size_max=18,
        hover_name="Nombre_Proyecto",
        hover_data={
            "ID_Proyecto": True,
            "Periodo_Academico": True,
            "Entidad_Beneficiaria": True,
            "Canton": True,
            "Parroquia": True,
            "Comunidad": True,
            "Linea_Tematica": True,
            "Producto_Principal": True,
            "Latitud": False,
            "Longitud": False,
            "Tamano_Marcador": False,
        },
        center={
            "lat": -0.93,
            "lon": -78.62,
        },
        zoom=9,
        height=650,
        map_style="open-street-map",
    )

    figura_mapa.update_traces(
        marker={
            "opacity": 0.90,
        }
    )

    figura_mapa.update_layout(
        legend_title_text="Línea temática",
        margin={
            "l": 0,
            "r": 0,
            "t": 10,
            "b": 0,
        },
    )

    st.plotly_chart(
        figura_mapa,
        use_container_width=True,
    )

    st.caption(
        "Los puntos representan ubicaciones "
        "referenciales de los proyectos. "
        "Varios proyectos pueden compartir "
        "coordenada cuando corresponden a una "
        "misma comunidad."
    )

# TABLA DE PROYECTOS

st.subheader(
    "Proyectos seleccionados"
)


columnas_tabla = [
    "ID_Proyecto",
    "Nombre_Proyecto",
    "Periodo_Academico",
    "Entidad_Beneficiaria",
    "Canton",
    "Parroquia",
    "Comunidad",
    "Linea_Tematica",
    "Producto_Principal",
]


tabla_proyectos = datos_filtrados[
    columnas_tabla
].copy()


# Mostrar guiones en la tabla sin modificar la base
tabla_proyectos = tabla_proyectos.fillna("-")


st.dataframe(
    tabla_proyectos,
    use_container_width=True,
    hide_index=True,
)

# FICHA INDIVIDUAL DEL PROYECTO

st.divider()

st.subheader(
    "Ficha individual del proyecto"
)


proyectos_disponibles = (
    datos_filtrados[
        [
            "ID_Proyecto",
            "Nombre_Proyecto",
        ]
    ]
    .sort_values(
        "Nombre_Proyecto"
    )
    .copy()
)


proyectos_disponibles[
    "Etiqueta_Proyecto"
] = (
    proyectos_disponibles["ID_Proyecto"]
    + " | "
    + proyectos_disponibles["Nombre_Proyecto"]
)


proyecto_seleccionado = st.selectbox(
    label="Seleccione un proyecto",
    options=proyectos_disponibles[
        "Etiqueta_Proyecto"
    ].tolist(),
)


id_seleccionado = proyecto_seleccionado.split(
    " | ",
    maxsplit=1,
)[0]


ficha = datos_filtrados[
    datos_filtrados["ID_Proyecto"]
    == id_seleccionado
].iloc[0]

# INFORMACIÓN DE IDENTIFICACIÓN Y LOCALIZACIÓN

ficha_columna_1, ficha_columna_2 = st.columns(2)


with ficha_columna_1:
    st.markdown(
        "#### Identificación"
    )

    st.write(
        f"**ID del proyecto:** "
        f"{mostrar_valor(ficha['ID_Proyecto'])}"
    )

    st.write(
        f"**Nombre:** "
        f"{mostrar_valor(ficha['Nombre_Proyecto'])}"
    )

    st.write(
        f"**Período académico:** "
        f"{mostrar_valor(ficha['Periodo_Academico'])}"
    )

    st.write(
        f"**Línea temática:** "
        f"{mostrar_valor(ficha['Linea_Tematica'])}"
    )


with ficha_columna_2:
    st.markdown(
        "#### Localización"
    )

    st.write(
        f"**Provincia:** "
        f"{mostrar_valor(ficha['Provincia'])}"
    )

    st.write(
        f"**Cantón:** "
        f"{mostrar_valor(ficha['Canton'])}"
    )

    st.write(
        f"**Parroquia:** "
        f"{mostrar_valor(ficha['Parroquia'])}"
    )

    st.write(
        f"**Comunidad:** "
        f"{mostrar_valor(ficha['Comunidad'])}"
    )

# INFORMACIÓN TÉCNICA Y ACADÉMICA

st.markdown(
    "#### Información técnica y académica"
)


informacion_columna_1, informacion_columna_2, informacion_columna_3 = (
    st.columns(3)
)


with informacion_columna_1:
    st.write(
        f"**Entidad beneficiaria:** "
        f"{mostrar_valor(ficha['Entidad_Beneficiaria'])}"
    )

    st.write(
        f"**Tipo de entidad:** "
        f"{mostrar_valor(ficha['Tipo_Entidad'])}"
    )


with informacion_columna_2:
    st.write(
        f"**Estudiantes:** "
        f"{mostrar_valor(ficha['Estudiantes'])}"
    )

    st.write(
        f"**Horas por estudiante:** "
        f"{mostrar_valor(ficha['Horas_Vinculacion'])}"
    )


with informacion_columna_3:
    st.write(
        f"**Beneficiarios:** "
        f"{mostrar_valor(ficha['Beneficiarios_Valor'])}"
    )

    st.write(
        f"**Unidad:** "
        f"{mostrar_valor(ficha['Beneficiarios_Unidad'])}"
    )

# HORAS-PERSONA DEL PROYECTO SELECCIONADO

if (
    pd.notna(ficha["Estudiantes"])
    and pd.notna(ficha["Horas_Vinculacion"])
):
    horas_persona_proyecto = (
        ficha["Estudiantes"]
        * ficha["Horas_Vinculacion"]
    )

    horas_persona_proyecto = int(
        horas_persona_proyecto
    )

else:
    horas_persona_proyecto = None


if horas_persona_proyecto is not None:
    st.write(
        f"**Horas-persona del proyecto:** "
        f"{horas_persona_proyecto:,}".replace(
            ",",
            ".",
        )
    )

else:
    st.write(
        "**Horas-persona del proyecto:** -"
    )

# PRODUCTO PRINCIPAL

st.markdown(
    "#### Producto técnico principal"
)

st.info(
    mostrar_valor(
        ficha["Producto_Principal"]
    )
)

# UBICACIÓN DEL PROYECTO SELECCIONADO

st.markdown(
    "#### Ubicación del proyecto seleccionado"
)


if (
    pd.notna(ficha["Latitud"])
    and pd.notna(ficha["Longitud"])
):
    ubicacion_seleccionada = pd.DataFrame(
        {
            "Nombre_Proyecto": [
                ficha["Nombre_Proyecto"]
            ],
            "Latitud": [
                ficha["Latitud"]
            ],
            "Longitud": [
                ficha["Longitud"]
            ],
        }
    )

    figura_ubicacion = px.scatter_map(
        ubicacion_seleccionada,
        lat="Latitud",
        lon="Longitud",
        hover_name="Nombre_Proyecto",
        center={
            "lat": ficha["Latitud"],
            "lon": ficha["Longitud"],
        },
        zoom=12,
        height=400,
        map_style="open-street-map",
    )

    figura_ubicacion.update_traces(
        marker={
            "size": 18,
            "color": "#D62828",
            "opacity": 0.95,
        }
    )

    figura_ubicacion.update_layout(
        showlegend=False,
        margin={
            "l": 0,
            "r": 0,
            "t": 0,
            "b": 0,
        },
    )

    st.plotly_chart(
        figura_ubicacion,
        use_container_width=True,
    )

else:
    st.warning(
        "El proyecto seleccionado no dispone "
        "de coordenadas válidas."
    )

# NOTA METODOLÓGICA

st.divider()

st.caption(
    "Nota: el símbolo '-' representa información "
    "no disponible en la documentación consultada "
    "y no equivale a cero."
)