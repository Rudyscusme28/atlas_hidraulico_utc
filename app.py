from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st


# ============================================================
# CONFIGURACIÓN GENERAL
# ============================================================

st.set_page_config(
    page_title="Atlas Hidráulico UTC",
    page_icon="💧",
    layout="wide",
)


# ============================================================
# FUNCIONES AUXILIARES
# ============================================================

def mostrar_valor(valor):
    """
    Muestra un guion cuando el dato está vacío.

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


def formatear_entero(valor):
    """
    Formatea un número entero con punto como separador
    de miles. Si no existe información, devuelve "-".
    """

    if pd.isna(valor):
        return "-"

    return f"{int(valor):,}".replace(",", ".")


# ============================================================
# RUTA DE LA BASE DE DATOS
# ============================================================

RUTA_EXCEL = Path("data") / "base_datos_rc.xlsx"


# ============================================================
# ENCABEZADO
# ============================================================

st.title(
    "Atlas Geoespacial de Vinculación "
    "en Ingeniería Hidráulica"
)

st.caption(
    "Universidad Técnica de Cotopaxi"
)


# ============================================================
# COMPROBACIÓN DEL ARCHIVO
# ============================================================

if not RUTA_EXCEL.exists():
    st.error(
        "No se encontró el archivo "
        "`data/base_datos_rc.xlsx`."
    )

    st.info(
        "Comprueba que el archivo se encuentre dentro "
        "de la carpeta `data` y que el nombre coincida "
        "exactamente."
    )

    st.stop()


# ============================================================
# CARGA DE LA BASE
# ============================================================

try:
    proyectos = pd.read_excel(
        RUTA_EXCEL,
        sheet_name="TB_PROYECTOS",
        engine="openpyxl",
    )

    publicaciones = pd.read_excel(
        RUTA_EXCEL,
        sheet_name="TB_PUBLICACIONES",
        engine="openpyxl",
    )

    relaciones_publicaciones = pd.read_excel(
        RUTA_EXCEL,
        sheet_name="TB_PROYECTO_PUBLICACION",
        engine="openpyxl",
    )

except ValueError:
    st.error(
        "No se encontraron todas las hojas requeridas: "
        "`TB_PROYECTOS`, `TB_PUBLICACIONES` o "
        "`TB_PROYECTO_PUBLICACION`."
    )
    st.stop()

except Exception as error:
    st.error(
        "Ocurrió un error al leer la base de datos."
    )
    st.exception(error)
    st.stop()



# ============================================================
# VALIDACIÓN DE COLUMNAS
# ============================================================

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


# ============================================================
# CONVERSIÓN DE DATOS
# ============================================================

columnas_numericas = [
    "Latitud",
    "Longitud",
    "Estudiantes",
    "Horas_Vinculacion",
    "Beneficiarios_Valor",
]

for columna in columnas_numericas:
    proyectos[columna] = pd.to_numeric(
        proyectos[columna],
        errors="coerce",
    )


# ============================================================
# CONTROLES DE CALIDAD
# ============================================================

if len(proyectos) != 21:
    st.warning(
        f"La base contiene {len(proyectos)} filas. "
        "La cohorte esperada contiene 21 proyectos."
    )


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


st.success(
    f"Base cargada correctamente: "
    f"{len(proyectos)} proyectos."
)


# ============================================================
# FILTROS LATERALES
# ============================================================

st.sidebar.header("Filtros de consulta")


periodos_disponibles = sorted(
    proyectos["Periodo_Academico"]
    .dropna()
    .unique()
    .tolist()
)

periodos_seleccionados = st.sidebar.multiselect(
    label="Período académico",
    options=periodos_disponibles,
    default=periodos_disponibles,
)


lineas_disponibles = sorted(
    proyectos["Linea_Tematica"]
    .dropna()
    .unique()
    .tolist()
)

lineas_seleccionadas = st.sidebar.multiselect(
    label="Línea temática",
    options=lineas_disponibles,
    default=lineas_disponibles,
)


datos_filtrados = proyectos.loc[
    proyectos["Periodo_Academico"].isin(
        periodos_seleccionados
    )
    & proyectos["Linea_Tematica"].isin(
        lineas_seleccionadas
    )
].copy()


if datos_filtrados.empty:
    st.warning(
        "No existen proyectos que coincidan "
        "con los filtros seleccionados."
    )

    st.stop()


# ============================================================
# INDICADORES GENERALES
# ============================================================

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
        value=formatear_entero(
            horas_persona
        ),
    )


# ============================================================
# ALCANCE SOCIAL DOCUMENTADO
# ============================================================

st.subheader(
    "Alcance social documentado"
)


beneficiarios_personas = datos_filtrados.loc[
    datos_filtrados["Beneficiarios_Unidad"]
    == "Personas/Habitantes",
    "Beneficiarios_Valor",
].sum(
    min_count=1
)


beneficiarios_usuarios = datos_filtrados.loc[
    datos_filtrados["Beneficiarios_Unidad"]
    == "Usuarios",
    "Beneficiarios_Valor",
].sum(
    min_count=1
)


beneficiarios_familias = datos_filtrados.loc[
    datos_filtrados["Beneficiarios_Unidad"]
    == "Familias",
    "Beneficiarios_Valor",
].sum(
    min_count=1
)


proyectos_con_beneficiarios = datos_filtrados.loc[
    datos_filtrados["Beneficiarios_Valor"].notna(),
    "ID_Proyecto",
].nunique()


social_1, social_2, social_3, social_4 = st.columns(4)

with social_1:
    st.metric(
        label="Personas / habitantes",
        value=formatear_entero(
            beneficiarios_personas
        ),
    )

with social_2:
    st.metric(
        label="Usuarios",
        value=formatear_entero(
            beneficiarios_usuarios
        ),
    )

with social_3:
    st.metric(
        label="Familias",
        value=formatear_entero(
            beneficiarios_familias
        ),
    )

with social_4:
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


# ============================================================
# TRANSFERENCIA CIENTÍFICA
# ============================================================

st.divider()

st.subheader(
    "Transferencia científica"
)


# Validar columnas de las tablas científicas
columnas_publicaciones_requeridas = [
    "ID_Articulo",
    "Titulo",
    "Año",
    "Revista",
    "DOI",
]

columnas_relaciones_requeridas = [
    "ID_Proyecto",
    "ID_Articulo",
    "Tipo_Relacion",
]


columnas_publicaciones_ausentes = [
    columna
    for columna in columnas_publicaciones_requeridas
    if columna not in publicaciones.columns
]

columnas_relaciones_ausentes = [
    columna
    for columna in columnas_relaciones_requeridas
    if columna not in relaciones_publicaciones.columns
]


if (
    columnas_publicaciones_ausentes
    or columnas_relaciones_ausentes
):
    st.warning(
        "No se puede construir el módulo científico "
        "porque faltan columnas en las tablas."
    )

    if columnas_publicaciones_ausentes:
        st.write(
            "Columnas ausentes en TB_PUBLICACIONES:",
            columnas_publicaciones_ausentes,
        )

    if columnas_relaciones_ausentes:
        st.write(
            "Columnas ausentes en "
            "TB_PROYECTO_PUBLICACION:",
            columnas_relaciones_ausentes,
        )

else:
    # Conservar únicamente relaciones correspondientes
    # a los proyectos actualmente visibles
    relaciones_filtradas = (
        relaciones_publicaciones.loc[
            relaciones_publicaciones[
                "ID_Proyecto"
            ].isin(
                datos_filtrados["ID_Proyecto"]
            )
        ]
        .copy()
    )


    # Artículos asociados a los proyectos filtrados
    identificadores_articulos_filtrados = (
        relaciones_filtradas[
            "ID_Articulo"
        ]
        .dropna()
        .unique()
        .tolist()
    )


    publicaciones_filtradas = publicaciones.loc[
        publicaciones["ID_Articulo"].isin(
            identificadores_articulos_filtrados
        )
    ].copy()


    # Indicadores científicos
    total_articulos = publicaciones_filtradas[
        "ID_Articulo"
    ].nunique()

    proyectos_con_publicacion = relaciones_filtradas[
        "ID_Proyecto"
    ].nunique()

    relaciones_directas = relaciones_filtradas.loc[
        relaciones_filtradas["Tipo_Relacion"]
        == "Directa"
    ].shape[0]

    relaciones_sistematizacion = relaciones_filtradas.loc[
        relaciones_filtradas["Tipo_Relacion"]
        == "Sistematización"
    ].shape[0]

    iti_documental = (
        proyectos_con_publicacion
        / total_proyectos
        if total_proyectos > 0
        else 0
    )


    # Tarjetas científicas
    cientifica_1, cientifica_2, cientifica_3, cientifica_4, cientifica_5 = (
        st.columns(5)
    )


    with cientifica_1:
        st.metric(
            label="Artículos asociados",
            value=total_articulos,
        )


    with cientifica_2:
        st.metric(
            label="Proyectos con publicación",
            value=(
                f"{proyectos_con_publicacion} "
                f"de {total_proyectos}"
            ),
        )


    with cientifica_3:
        st.metric(
            label="ITI documental",
            value=f"{iti_documental:.1%}",
        )


    with cientifica_4:
        st.metric(
            label="Relaciones directas",
            value=relaciones_directas,
        )


    with cientifica_5:
        st.metric(
            label="Sistematizaciones",
            value=relaciones_sistematizacion,
        )


    st.caption(
        "El ITI documental representa la proporción "
        "de proyectos visibles que poseen al menos una "
        "relación registrada con una publicación."
    )


    if relaciones_filtradas.empty:
        st.info(
            "Los proyectos seleccionados no tienen "
            "publicaciones asociadas."
        )

    else:
        # Incorporar nombre y producto del proyecto
        tabla_transferencia = (
            relaciones_filtradas.merge(
                datos_filtrados[
                    [
                        "ID_Proyecto",
                        "Nombre_Proyecto",
                        "Periodo_Academico",
                        "Producto_Principal",
                    ]
                ],
                on="ID_Proyecto",
                how="left",
            )
        )


        # Incorporar información de la publicación
        tabla_transferencia = (
            tabla_transferencia.merge(
                publicaciones[
                    [
                        "ID_Articulo",
                        "Titulo",
                        "Año",
                        "Revista",
                        "DOI",
                    ]
                ],
                on="ID_Articulo",
                how="left",
            )
        )


        # Crear enlace web a partir del DOI
        tabla_transferencia["Enlace_DOI"] = (
            "https://doi.org/"
            + tabla_transferencia[
                "DOI"
            ].fillna("").astype(str)
        )


        # Evitar enlaces inválidos en DOI vacíos
        tabla_transferencia.loc[
            tabla_transferencia["DOI"].isna()
            | (
                tabla_transferencia["DOI"]
                .astype(str)
                .str.strip()
                == ""
            ),
            "Enlace_DOI",
        ] = None


        tabla_transferencia = (
            tabla_transferencia.sort_values(
                by=[
                    "Año",
                    "Titulo",
                    "Nombre_Proyecto",
                ],
                ascending=[
                    False,
                    True,
                    True,
                ],
            )
        )


        st.markdown(
            "#### Trazabilidad proyecto-publicación"
        )


        tabla_transferencia_visible = (
            tabla_transferencia[
                [
                    "ID_Proyecto",
                    "Nombre_Proyecto",
                    "Periodo_Academico",
                    "Producto_Principal",
                    "Titulo",
                    "Año",
                    "Revista",
                    "Tipo_Relacion",
                    "Enlace_DOI",
                ]
            ]
            .copy()
        )


        tabla_transferencia_visible = (
            tabla_transferencia_visible.fillna("-")
        )


        st.dataframe(
            tabla_transferencia_visible,
            use_container_width=True,
            hide_index=True,
            column_config={
                "ID_Proyecto": st.column_config.TextColumn(
                    "ID del proyecto"
                ),
                "Nombre_Proyecto": st.column_config.TextColumn(
                    "Proyecto"
                ),
                "Periodo_Academico": st.column_config.TextColumn(
                    "Período"
                ),
                "Producto_Principal": st.column_config.TextColumn(
                    "Producto técnico"
                ),
                "Titulo": st.column_config.TextColumn(
                    "Artículo"
                ),
                "Año": st.column_config.NumberColumn(
                    "Año",
                    format="%d",
                ),
                "Revista": st.column_config.TextColumn(
                    "Revista"
                ),
                "Tipo_Relacion": st.column_config.TextColumn(
                    "Tipo de relación"
                ),
                "Enlace_DOI": st.column_config.LinkColumn(
                    "DOI",
                    display_text="Abrir publicación",
                ),
            },
        )


        # Distribución por tipo de relación
        relaciones_por_tipo = (
            relaciones_filtradas.groupby(
                "Tipo_Relacion",
                as_index=False,
            )
            .size()
            .rename(
                columns={
                    "size": "Numero_Relaciones"
                }
            )
            .sort_values(
                by="Numero_Relaciones",
                ascending=True,
            )
        )


        figura_relaciones = px.bar(
            relaciones_por_tipo,
            x="Numero_Relaciones",
            y="Tipo_Relacion",
            orientation="h",
            text="Numero_Relaciones",
            title=(
                "Relaciones entre proyectos "
                "y publicaciones"
            ),
            labels={
                "Numero_Relaciones": (
                    "Número de relaciones"
                ),
                "Tipo_Relacion": "",
            },
            color="Tipo_Relacion",
        )


        figura_relaciones.update_traces(
            textposition="outside",
        )


        figura_relaciones.update_layout(
            showlegend=False,
            xaxis_title="Número de relaciones",
            yaxis_title="",
            height=max(
                350,
                len(relaciones_por_tipo) * 90,
            ),
            margin={
                "l": 20,
                "r": 80,
                "t": 70,
                "b": 20,
            },
        )


        figura_relaciones.update_xaxes(
            dtick=1,
        )


        st.plotly_chart(
            figura_relaciones,
            use_container_width=True,
        )


        st.caption(
            "Una relación directa indica correspondencia "
            "específica entre proyecto y artículo. "
            "La sistematización representa publicaciones "
            "que integran resultados de varios proyectos. "
            "Las relaciones pendientes deben mantenerse "
            "diferenciadas hasta confirmar el expediente."
        )

# ============================================================
# GRÁFICO DE BENEFICIARIOS POR PROYECTO
# ============================================================

st.markdown(
    "#### Beneficiarios por proyecto"
)


unidades_sociales = sorted(
    datos_filtrados.loc[
        datos_filtrados["Beneficiarios_Valor"].notna()
        & datos_filtrados["Beneficiarios_Unidad"].notna(),
        "Beneficiarios_Unidad",
    ]
    .astype(str)
    .unique()
    .tolist()
)


if not unidades_sociales:
    st.info(
        "Los proyectos seleccionados no tienen "
        "beneficiarios cuantificados."
    )

else:
    unidad_seleccionada = st.selectbox(
        label="Unidad de beneficiarios",
        options=unidades_sociales,
        key="selector_unidad_beneficiarios",
    )


    datos_beneficiarios = datos_filtrados.loc[
        (
            datos_filtrados["Beneficiarios_Unidad"]
            == unidad_seleccionada
        )
        & datos_filtrados[
            "Beneficiarios_Valor"
        ].notna()
    ].copy()


    datos_beneficiarios = (
        datos_beneficiarios.sort_values(
            by="Beneficiarios_Valor",
            ascending=True,
        )
    )


    if datos_beneficiarios.empty:
        st.info(
            "No existen proyectos con valores "
            "documentados para esta unidad."
        )

    else:
        figura_beneficiarios = px.bar(
            datos_beneficiarios,
            x="Beneficiarios_Valor",
            y="Nombre_Proyecto",
            orientation="h",
            color="Linea_Tematica",
            text="Beneficiarios_Valor",
            title=(
                "Beneficiarios documentados por proyecto "
                f"({unidad_seleccionada})"
            ),
            labels={
                "Beneficiarios_Valor": unidad_seleccionada,
                "Nombre_Proyecto": "Proyecto",
                "Linea_Tematica": "Línea temática",
            },
            hover_data={
                "ID_Proyecto": True,
                "Periodo_Academico": True,
                "Comunidad": True,
                "Beneficiarios_Unidad": True,
            },
        )


        figura_beneficiarios.update_traces(
            texttemplate="%{text:,.0f}",
            textposition="outside",
        )


        figura_beneficiarios.update_layout(
            xaxis_title=unidad_seleccionada,
            yaxis_title="",
            legend_title_text="Línea temática",
            height=max(
                400,
                len(datos_beneficiarios) * 55,
            ),
            margin={
                "l": 20,
                "r": 80,
                "t": 70,
                "b": 20,
            },
        )


        st.plotly_chart(
            figura_beneficiarios,
            use_container_width=True,
        )


        st.caption(
            "El gráfico presenta únicamente proyectos "
            f"expresados en {unidad_seleccionada}. "
            "Los datos ausentes no se consideran cero."
        )


# ============================================================
# CAPACIDADES Y HERRAMIENTAS TÉCNICAS
# ============================================================

st.divider()

st.subheader(
    "Capacidades y herramientas técnicas"
)


herramientas_tecnicas = {
    "Planos": "Tiene_Planos",
    "SIG": "Tiene_SIG",
    "Civil 3D": "Tiene_Civil3D",
    "EPANET": "Tiene_EPANET",
    "Modelación": "Tiene_Modelacion",
    "Aforos": "Tiene_Aforos",
    "Calidad del agua": "Tiene_Calidad_Agua",
    "Topografía": "Tiene_Topografia",
}


columnas_herramientas_ausentes = [
    columna
    for columna in herramientas_tecnicas.values()
    if columna not in datos_filtrados.columns
]


if columnas_herramientas_ausentes:
    st.warning(
        "No se pueden calcular todas las capacidades "
        "técnicas porque faltan columnas en la base."
    )

    st.write(
        "Columnas ausentes:",
        columnas_herramientas_ausentes,
    )

else:
    for columna in herramientas_tecnicas.values():
        datos_filtrados[columna] = pd.to_numeric(
            datos_filtrados[columna],
            errors="coerce",
        )


    resumen_herramientas = []

    for nombre_herramienta, columna in (
        herramientas_tecnicas.items()
    ):
        cantidad_proyectos = int(
            datos_filtrados[columna]
            .fillna(0)
            .eq(1)
            .sum()
        )

        porcentaje_proyectos = (
            cantidad_proyectos
            / total_proyectos
            * 100
            if total_proyectos > 0
            else 0
        )

        resumen_herramientas.append(
            {
                "Herramienta": nombre_herramienta,
                "Proyectos": cantidad_proyectos,
                "Porcentaje": porcentaje_proyectos,
            }
        )


    resumen_herramientas = pd.DataFrame(
        resumen_herramientas
    )


    # --------------------------------------------------------
    # TARJETAS TÉCNICAS
    # --------------------------------------------------------

    fila_tecnica_1 = st.columns(4)
    fila_tecnica_2 = st.columns(4)

    nombres_herramientas = list(
        herramientas_tecnicas.keys()
    )

    # Primera fila
    for posicion in range(4):
        nombre = nombres_herramientas[posicion]

        registro = resumen_herramientas.loc[
            resumen_herramientas["Herramienta"]
            == nombre
        ].iloc[0]

        with fila_tecnica_1[posicion]:
            st.metric(
                label=nombre,
                value=(
                    f"{int(registro['Proyectos'])} "
                    f"de {total_proyectos}"
                ),
                delta=(
                    f"{registro['Porcentaje']:.1f}%"
                ),
                delta_color="off",
            )


    # Segunda fila
    for posicion in range(4, 8):
        nombre = nombres_herramientas[posicion]

        registro = resumen_herramientas.loc[
            resumen_herramientas["Herramienta"]
            == nombre
        ].iloc[0]

        with fila_tecnica_2[posicion - 4]:
            st.metric(
                label=nombre,
                value=(
                    f"{int(registro['Proyectos'])} "
                    f"de {total_proyectos}"
                ),
                delta=(
                    f"{registro['Porcentaje']:.1f}%"
                ),
                delta_color="off",
            )

    # --------------------------------------------------------
    # GRÁFICO DE CAPACIDADES
    # --------------------------------------------------------

    resumen_herramientas = (
        resumen_herramientas.sort_values(
            by="Proyectos",
            ascending=True,
        )
    )


    figura_herramientas = px.bar(
        resumen_herramientas,
        x="Proyectos",
        y="Herramienta",
        orientation="h",
        text="Proyectos",
        title=(
            "Número de proyectos por capacidad "
            "o herramienta técnica"
        ),
        labels={
            "Proyectos": "Número de proyectos",
            "Herramienta": "",
        },
        color="Porcentaje",
        color_continuous_scale=[
            "#D8F3F1",
            "#0B7285",
        ],
        hover_data={
            "Proyectos": True,
            "Porcentaje": ":.1f",
        },
    )


    figura_herramientas.update_traces(
        textposition="outside",
    )


    maximo_herramientas = int(
        resumen_herramientas[
            "Proyectos"
        ].max()
    )


    figura_herramientas.update_layout(
        xaxis_title="Número de proyectos",
        yaxis_title="",
        coloraxis_colorbar={
            "title": "Porcentaje",
            "ticksuffix": "%",
        },
        height=500,
        margin={
            "l": 20,
            "r": 80,
            "t": 70,
            "b": 20,
        },
    )


    figura_herramientas.update_xaxes(
        dtick=1,
        range=[
            0,
            max(
                maximo_herramientas + 1,
                1,
            ),
        ],
    )


    st.plotly_chart(
        figura_herramientas,
        use_container_width=True,
    )


    st.caption(
        "La presencia de una herramienta indica que "
        "su uso está registrado en la documentación "
        "del proyecto. No implica necesariamente que "
        "el producto haya sido implementado o validado "
        "en operación."
    )


# ============================================================
# CALIDAD Y COBERTURA DOCUMENTAL
# ============================================================

st.divider()

st.subheader(
    "Calidad y cobertura documental"
)


# Relación entre el nombre visible del indicador
# y la condición que debe cumplir cada proyecto.
condiciones_cobertura = {
    "Estudiantes": (
        datos_filtrados["Estudiantes"].notna()
    ),
    "Beneficiarios": (
        datos_filtrados[
            "Beneficiarios_Valor"
        ].notna()
    ),
    "Coordenadas": (
        datos_filtrados["Latitud"].notna()
        & datos_filtrados["Longitud"].notna()
    ),
    "Producto técnico": (
        datos_filtrados[
            "Producto_Principal"
        ].notna()
    ),
    "Entidad beneficiaria": (
        datos_filtrados[
            "Entidad_Beneficiaria"
        ].notna()
    ),
}


# Añadir publicación asociada si la columna existe.
if "Publicacion_Asociada" in datos_filtrados.columns:
    condiciones_cobertura[
        "Publicación asociada"
    ] = (
        pd.to_numeric(
            datos_filtrados[
                "Publicacion_Asociada"
            ],
            errors="coerce",
        )
        .fillna(0)
        .eq(1)
    )


# Añadir madurez preliminar si la columna existe.
if (
    "Nivel_Madurez_Preliminar"
    in datos_filtrados.columns
):
    condiciones_cobertura[
        "Madurez preliminar"
    ] = (
        datos_filtrados[
            "Nivel_Madurez_Preliminar"
        ].notna()
    )


# Añadir fuente primaria si la columna existe.
if "Fuente_Primaria" in datos_filtrados.columns:
    condiciones_cobertura[
        "Fuente primaria"
    ] = (
        datos_filtrados[
            "Fuente_Primaria"
        ].notna()
        & (
            datos_filtrados[
                "Fuente_Primaria"
            ]
            .astype(str)
            .str.strip()
            != ""
        )
    )


# Construir la tabla resumen.
registros_cobertura = []

for indicador, condicion in condiciones_cobertura.items():
    proyectos_con_dato = int(
        condicion.fillna(False).sum()
    )

    proyectos_sin_dato = (
        total_proyectos
        - proyectos_con_dato
    )

    porcentaje_cobertura = (
        proyectos_con_dato
        / total_proyectos
        * 100
        if total_proyectos > 0
        else 0
    )

    registros_cobertura.append(
        {
            "Indicador": indicador,
            "Con_Dato": proyectos_con_dato,
            "Sin_Dato": proyectos_sin_dato,
            "Cobertura": porcentaje_cobertura,
        }
    )


resumen_cobertura = pd.DataFrame(
    registros_cobertura
)


# ============================================================
# INDICADORES RESUMIDOS DE CALIDAD
# ============================================================

cobertura_promedio = (
    resumen_cobertura[
        "Cobertura"
    ].mean()
)


proyectos_con_coordenadas = int(
    condiciones_cobertura[
        "Coordenadas"
    ]
    .fillna(False)
    .sum()
)


proyectos_con_estudiantes = int(
    condiciones_cobertura[
        "Estudiantes"
    ]
    .fillna(False)
    .sum()
)


proyectos_con_dato_social = int(
    condiciones_cobertura[
        "Beneficiarios"
    ]
    .fillna(False)
    .sum()
)


calidad_1, calidad_2, calidad_3, calidad_4 = (
    st.columns(4)
)


with calidad_1:
    st.metric(
        label="Cobertura documental media",
        value=f"{cobertura_promedio:.1f}%",
    )


with calidad_2:
    st.metric(
        label="Con estudiantes",
        value=(
            f"{proyectos_con_estudiantes} "
            f"de {total_proyectos}"
        ),
    )


with calidad_3:
    st.metric(
        label="Con dato social",
        value=(
            f"{proyectos_con_dato_social} "
            f"de {total_proyectos}"
        ),
    )


with calidad_4:
    st.metric(
        label="Con coordenadas",
        value=(
            f"{proyectos_con_coordenadas} "
            f"de {total_proyectos}"
        ),
    )


# ============================================================
# GRÁFICO DE COBERTURA
# ============================================================

resumen_cobertura_grafico = (
    resumen_cobertura.sort_values(
        by="Cobertura",
        ascending=True,
    )
)


figura_cobertura = px.bar(
    resumen_cobertura_grafico,
    x="Cobertura",
    y="Indicador",
    orientation="h",
    text="Cobertura",
    title=(
        "Cobertura de información "
        "por variable"
    ),
    labels={
        "Cobertura": "Cobertura documental (%)",
        "Indicador": "",
    },
    color="Cobertura",
    color_continuous_scale=[
        "#FDE2E2",
        "#F9C74F",
        "#0B7285",
    ],
    range_color=[
        0,
        100,
    ],
    hover_data={
        "Con_Dato": True,
        "Sin_Dato": True,
        "Cobertura": ":.1f",
    },
)


figura_cobertura.update_traces(
    texttemplate="%{text:.1f}%",
    textposition="outside",
)


figura_cobertura.update_layout(
    xaxis_title="Cobertura documental (%)",
    yaxis_title="",
    height=max(
        450,
        len(resumen_cobertura_grafico)
        * 55,
    ),
    coloraxis_colorbar={
        "title": "Cobertura",
        "ticksuffix": "%",
    },
    margin={
        "l": 20,
        "r": 80,
        "t": 70,
        "b": 20,
    },
)


figura_cobertura.update_xaxes(
    range=[
        0,
        105,
    ],
    ticksuffix="%",
)


st.plotly_chart(
    figura_cobertura,
    use_container_width=True,
)


# ============================================================
# TABLA DE DATOS FALTANTES
# ============================================================

st.markdown(
    "#### Resumen de disponibilidad"
)


tabla_cobertura = (
    resumen_cobertura[
        [
            "Indicador",
            "Con_Dato",
            "Sin_Dato",
            "Cobertura",
        ]
    ]
    .copy()
)


st.dataframe(
    tabla_cobertura,
    use_container_width=True,
    hide_index=True,
    column_config={
        "Indicador": st.column_config.TextColumn(
            "Variable"
        ),
        "Con_Dato": st.column_config.NumberColumn(
            "Proyectos con dato",
            format="%d",
        ),
        "Sin_Dato": st.column_config.NumberColumn(
            "Proyectos sin dato",
            format="%d",
        ),
        "Cobertura": st.column_config.ProgressColumn(
            "Cobertura",
            min_value=0,
            max_value=100,
            format="%.1f%%",
        ),
    },
)


st.caption(
    "La cobertura indica disponibilidad documental. "
    "No representa calidad técnica, ejecución física "
    "ni impacto causal del proyecto."
)

# ============================================================
# GRÁFICO POR PERÍODO ACADÉMICO
# ============================================================

st.divider()


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


figura_periodos.update_yaxes(
    dtick=1,
)


st.plotly_chart(
    figura_periodos,
    use_container_width=True,
)


# ============================================================
# MAPA TERRITORIAL
# ============================================================

st.subheader(
    "Mapa territorial de los proyectos"
)


datos_mapa = datos_filtrados.dropna(
    subset=[
        "Latitud",
        "Longitud",
    ]
).copy()


datos_mapa = datos_mapa.loc[
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


# ============================================================
# TABLA DE PROYECTOS
# ============================================================

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


tabla_proyectos = tabla_proyectos.fillna("-")


st.dataframe(
    tabla_proyectos,
    use_container_width=True,
    hide_index=True,
)


# ============================================================
# FICHA INDIVIDUAL DEL PROYECTO
# ============================================================

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


ficha = datos_filtrados.loc[
    datos_filtrados["ID_Proyecto"]
    == id_seleccionado
].iloc[0]


# ============================================================
# IDENTIFICACIÓN Y LOCALIZACIÓN
# ============================================================

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


# ============================================================
# INFORMACIÓN TÉCNICA Y ACADÉMICA
# ============================================================

st.markdown(
    "#### Información técnica y académica"
)


informacion_1, informacion_2, informacion_3 = (
    st.columns(3)
)


with informacion_1:
    st.write(
        f"**Entidad beneficiaria:** "
        f"{mostrar_valor(ficha['Entidad_Beneficiaria'])}"
    )

    st.write(
        f"**Tipo de entidad:** "
        f"{mostrar_valor(ficha['Tipo_Entidad'])}"
    )


with informacion_2:
    st.write(
        f"**Estudiantes:** "
        f"{mostrar_valor(ficha['Estudiantes'])}"
    )

    st.write(
        f"**Horas por estudiante:** "
        f"{mostrar_valor(ficha['Horas_Vinculacion'])}"
    )


with informacion_3:
    st.write(
        f"**Beneficiarios:** "
        f"{mostrar_valor(ficha['Beneficiarios_Valor'])}"
    )

    st.write(
        f"**Unidad:** "
        f"{mostrar_valor(ficha['Beneficiarios_Unidad'])}"
    )


# ============================================================
# HORAS-PERSONA DEL PROYECTO
# ============================================================

if (
    pd.notna(ficha["Estudiantes"])
    and pd.notna(ficha["Horas_Vinculacion"])
):
    horas_persona_proyecto = int(
        ficha["Estudiantes"]
        * ficha["Horas_Vinculacion"]
    )

else:
    horas_persona_proyecto = None


st.write(
    f"**Horas-persona del proyecto:** "
    f"{formatear_entero(horas_persona_proyecto)}"
)


# ============================================================
# PRODUCTO PRINCIPAL
# ============================================================

st.markdown(
    "#### Producto técnico principal"
)

st.info(
    mostrar_valor(
        ficha["Producto_Principal"]
    )
)


# ============================================================
# UBICACIÓN DEL PROYECTO SELECCIONADO
# ============================================================

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


# ============================================================
# NOTA METODOLÓGICA
# ============================================================

st.divider()

st.caption(
    "Nota: el símbolo '-' representa información "
    "no disponible en la documentación consultada "
    "y no equivale a cero."
)