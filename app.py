import streamlit as st
from datetime import date
from io import BytesIO
from html import escape

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    PageBreak,
)

st.set_page_config(
    page_title="Calculadora PSG Pediátrica",
    page_icon="💤",
    layout="wide"
)

st.markdown(
    """
    <style>
    .main-title {
        font-size: 2.25rem;
        font-weight: 800;
        margin-bottom: 0.2rem;
    }
    .subtitle {
        color: #555;
        font-size: 1rem;
        margin-bottom: 1.4rem;
    }
    .metric-card {
        background-color: #F7F8FA;
        border: 1px solid #E5E7EB;
        padding: 1rem;
        border-radius: 14px;
    }
    .report-box {
        background-color: #FAFAFA;
        border: 1px solid #E5E7EB;
        border-radius: 12px;
        padding: 1.2rem;
        line-height: 1.6;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.markdown('<div class="main-title">Calculadora clínica de polisomnografía pediátrica</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="subtitle">Ingrese los valores del estudio y genere automáticamente una impresión clínica integrada en PDF.</div>',
    unsafe_allow_html=True
)


# ============================================================
# Funciones de interpretación
# ============================================================

def clasificar_iah(iah: float) -> str:
    if iah < 1:
        return "sin evidencia polisomnográfica de apnea obstructiva del sueño pediátrica"
    elif iah < 5:
        return "apnea obstructiva del sueño pediátrica leve"
    elif iah < 10:
        return "apnea obstructiva del sueño pediátrica moderada"
    return "apnea obstructiva del sueño pediátrica severa"


def grado_corto_iah(iah: float) -> str:
    if iah < 1:
        return "normal"
    elif iah < 5:
        return "leve"
    elif iah < 10:
        return "moderada"
    return "severa"


def interpretar_oxigenacion(spo2_min: float, tiempo_menor_90: float) -> str:
    if spo2_min < 80 or tiempo_menor_90 > 5:
        return "compromiso significativo de la oxigenación nocturna"
    elif spo2_min < 90 or tiempo_menor_90 > 0:
        return "desaturación nocturna leve a moderada"
    return "oxigenación nocturna conservada"


def interpretar_eficiencia(eficiencia: float) -> str:
    if eficiencia >= 85:
        return "eficiencia del sueño conservada"
    elif eficiencia >= 75:
        return "eficiencia del sueño discretamente reducida"
    return "eficiencia del sueño reducida"


def interpretar_arousals(indice_arousal: float) -> str:
    if indice_arousal < 10:
        return "sin fragmentación significativa del sueño"
    elif indice_arousal < 20:
        return "fragmentación leve a moderada del sueño"
    return "fragmentación importante del sueño"


def interpretar_plmi(plmi: float) -> str:
    if plmi < 5:
        return "sin incremento patológico de movimientos periódicos de extremidades"
    return "incremento del índice de movimientos periódicos de extremidades"


def patron_rem(iah_rem: float, iah_nrem: float) -> str:
    if iah_nrem == 0 and iah_rem > 0:
        return "con predominio durante sueño REM"
    if iah_rem >= iah_nrem * 1.5:
        return "con predominio durante sueño REM"
    return "sin predominio REM claramente dominante"


def patron_posicional(iah_supino: float, iah_lateral: float) -> str:
    if iah_lateral == 0 and iah_supino > 0:
        return "con componente posicional en decúbito supino"
    if iah_supino >= iah_lateral * 2:
        return "con componente posicional en decúbito supino"
    return "sin patrón posicional claramente dominante"


def safe_text(value) -> str:
    return escape(str(value)).replace("\n", "<br/>")


# ============================================================
# Generador de PDF
# ============================================================

def build_pdf(data: dict) -> bytes:
    buffer = BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=1.6 * cm,
        leftMargin=1.6 * cm,
        topMargin=1.5 * cm,
        bottomMargin=1.5 * cm,
        title="Reporte de polisomnografía pediátrica"
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "TitleCustom",
        parent=styles["Title"],
        fontName="Helvetica-Bold",
        fontSize=15,
        leading=18,
        alignment=TA_CENTER,
        textColor=colors.HexColor("#1F2937"),
        spaceAfter=10,
    )

    subtitle_style = ParagraphStyle(
        "SubtitleCustom",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9,
        leading=12,
        alignment=TA_CENTER,
        textColor=colors.HexColor("#4B5563"),
        spaceAfter=10,
    )

    h_style = ParagraphStyle(
        "HeadingCustom",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=11,
        leading=14,
        textColor=colors.HexColor("#111827"),
        spaceBefore=8,
        spaceAfter=6,
    )

    normal_style = ParagraphStyle(
        "NormalCustom",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9,
        leading=12,
        alignment=TA_JUSTIFY,
        textColor=colors.HexColor("#111827"),
    )

    note_style = ParagraphStyle(
        "NoteCustom",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=8,
        leading=10,
        alignment=TA_LEFT,
        textColor=colors.HexColor("#4B5563"),
    )

    story = []

    institution = data.get("institucion", "").strip()
    if institution:
        story.append(Paragraph(safe_text(institution), subtitle_style))

    story.append(Paragraph("REPORTE DE POLISOMNOGRAFÍA PEDIÁTRICA", title_style))
    story.append(Paragraph("Reporte automatizado de apoyo clínico para interpretación de PSG pediátrica.", subtitle_style))
    story.append(Spacer(1, 6))

    def section(title):
        story.append(Paragraph(title, h_style))

    def p(text):
        story.append(Paragraph(text, normal_style))
        story.append(Spacer(1, 4))

    def table(rows, widths=None):
        table_obj = Table(rows, colWidths=widths, hAlign="LEFT")
        table_obj.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#E5E7EB")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor("#111827")),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
            ("FONTSIZE", (0, 0), (-1, -1), 8.5),
            ("ALIGN", (1, 1), (-1, -1), "RIGHT"),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#D1D5DB")),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F9FAFB")]),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ("TOPPADDING", (0, 0), (-1, -1), 5),
        ]))
        story.append(table_obj)
        story.append(Spacer(1, 6))

    section("1. Indicación clínica")
    p(safe_text(data["indicacion"]))

    section("2. Condiciones del estudio")
    table([
        ["Parámetro", "Resultado"],
        ["Fecha del estudio", str(data["fecha_estudio"])],
        ["Tipo de estudio", data["tipo_estudio"]],
        ["Duración total del registro", f'{data["duracion_registro"]:.1f} min'],
        ["Tiempo en cama (TIB)", f'{data["tiempo_cama"]:.1f} min'],
        ["Tiempo total de sueño (TST)", f'{data["tiempo_sueno"]:.1f} min'],
        ["Eficiencia del sueño", f'{data["eficiencia"]:.1f}%'],
        ["Latencia al sueño", f'{data["latencia_sueno"]:.1f} min'],
        ["Latencia REM", f'{data["latencia_rem"]:.1f} min'],
        ["Posición predominante", data["posicion_predominante"]],
    ], widths=[9 * cm, 7 * cm])

    section("3. Arquitectura del sueño")
    table([
        ["Estadio", "% del TST"],
        ["N1", f'{data["n1"]:.1f}%'],
        ["N2", f'{data["n2"]:.1f}%'],
        ["N3", f'{data["n3"]:.1f}%'],
        ["REM", f'{data["rem"]:.1f}%'],
    ], widths=[9 * cm, 7 * cm])
    p(f'Interpretación: el estudio muestra {data["interp_eficiencia"]}. La arquitectura debe analizarse con la edad, la duración del sueño REM y el grado de fragmentación.')

    section("4. Eventos respiratorios")
    table([
        ["Parámetro", "Resultado"],
        ["IAH total", f'{data["iah"]:.1f} eventos/hora'],
        ["IAH obstructivo", f'{data["iah_obstructivo"]:.1f} eventos/hora'],
        ["IAH central", f'{data["iah_central"]:.1f} eventos/hora'],
        ["Índice de hipopneas", f'{data["indice_hipopneas"]:.1f} eventos/hora'],
        ["IAH REM", f'{data["iah_rem"]:.1f} eventos/hora'],
        ["IAH NREM", f'{data["iah_nrem"]:.1f} eventos/hora'],
    ], widths=[9 * cm, 7 * cm])
    p(f'Interpretación: hallazgos compatibles con {data["diagnostico_iah"]}, {data["frase_rem"]}.')

    section("5. Oxigenación")
    table([
        ["Parámetro", "Resultado"],
        ["SpO₂ basal", f'{data["spo2_basal"]:.1f}%'],
        ["SpO₂ mínima", f'{data["spo2_min"]:.1f}%'],
        ["Tiempo con SpO₂ <90%", f'{data["tiempo_menor_90"]:.1f}% del TST'],
        ["ODI", f'{data["odi"]:.1f} eventos/hora'],
    ], widths=[9 * cm, 7 * cm])
    p(f'Interpretación: se documenta {data["interp_oxigenacion"]}.')

    section("6. Eventos cardiovasculares")
    table([
        ["Parámetro", "Resultado"],
        ["Frecuencia cardíaca promedio", f'{data["fc_promedio"]:.1f} lpm'],
        ["Frecuencia cardíaca mínima", f'{data["fc_min"]:.1f} lpm'],
        ["Frecuencia cardíaca máxima", f'{data["fc_max"]:.1f} lpm'],
        ["Arritmias", data["arritmias"]],
    ], widths=[9 * cm, 7 * cm])

    section("7. Movimientos periódicos de extremidades")
    table([
        ["Parámetro", "Resultado"],
        ["PLMI", f'{data["plmi"]:.1f} eventos/hora'],
    ], widths=[9 * cm, 7 * cm])
    p(f'Interpretación: {data["interp_plmi"]}.')

    section("8. Microdespertares")
    table([
        ["Parámetro", "Resultado"],
        ["Índice de arousal", f'{data["indice_arousal"]:.1f} eventos/hora'],
    ], widths=[9 * cm, 7 * cm])
    p(f'Interpretación: {data["interp_arousal"]}.')

    section("9. Análisis posicional")
    table([
        ["Posición", "IAH"],
        ["Supino", f'{data["iah_supino"]:.1f} eventos/hora'],
        ["Lateral", f'{data["iah_lateral"]:.1f} eventos/hora'],
    ], widths=[9 * cm, 7 * cm])
    p(f'Interpretación: {data["frase_posicion"]}.')

    section("10. Calidad técnica del estudio")
    p(f'Calidad técnica: <b>{safe_text(data["calidad"])}</b>.<br/>Observaciones técnicas: {safe_text(data["artefactos"])}')

    section("11. Conclusión diagnóstica")
    p(
        f'Estudio compatible con <b>{data["diagnostico_iah"]}</b>, con IAH total de '
        f'<b>{data["iah"]:.1f} eventos/hora</b>, IAH obstructivo de '
        f'<b>{data["iah_obstructivo"]:.1f} eventos/hora</b>, saturación mínima de '
        f'<b>{data["spo2_min"]:.1f}%</b> y {data["interp_oxigenacion"]}. '
        f'El patrón respiratorio fue descrito como {data["frase_rem"]} y {data["frase_posicion"]}.'
    )

    section("12. Impresión clínica automática para impresión")
    p(
        f'La polisomnografía pediátrica muestra un tiempo total de sueño de '
        f'<b>{data["tiempo_sueno"]:.1f} minutos</b> y una eficiencia del sueño de '
        f'<b>{data["eficiencia"]:.1f}%</b>, compatible con {data["interp_eficiencia"]}. '
        f'El índice de apnea-hipopnea fue de <b>{data["iah"]:.1f} eventos/hora</b>, '
        f'con componente obstructivo de <b>{data["iah_obstructivo"]:.1f} eventos/hora</b>, '
        f'hallazgo que clasifica el estudio como <b>{data["diagnostico_iah"]}</b>.'
    )
    p(
        f'Desde el punto de vista fisiológico, la saturación basal fue de '
        f'<b>{data["spo2_basal"]:.1f}%</b>, con nadir de <b>{data["spo2_min"]:.1f}%</b> '
        f'y tiempo con SpO₂ <90% de <b>{data["tiempo_menor_90"]:.1f}%</b> del TST, '
        f'lo cual sugiere {data["interp_oxigenacion"]}. El índice de arousal fue de '
        f'<b>{data["indice_arousal"]:.1f} eventos/hora</b>, indicando {data["interp_arousal"]}. '
        f'El análisis por fases del sueño mostró IAH REM de <b>{data["iah_rem"]:.1f}</b> '
        f'e IAH NREM de <b>{data["iah_nrem"]:.1f}</b> eventos/hora, por lo que el patrón '
        f'se interpreta como {data["frase_rem"]}. El análisis posicional muestra {data["frase_posicion"]}.'
    )
    p(
        f'En conjunto, los hallazgos son consistentes con trastorno respiratorio obstructivo '
        f'del sueño pediátrico de severidad <b>{data["grado_corto"]}</b>, con repercusión '
        f'sobre la oxigenación descrita como {data["interp_oxigenacion"]} y grado de '
        f'fragmentación del sueño descrito como {data["interp_arousal"]}.'
    )

    if data.get("mostrar_nota"):
        story.append(Spacer(1, 8))
        story.append(Paragraph(
            "Nota técnica: la clasificación automática usa umbrales pediátricos habituales del IAH "
            "(normal <1; leve 1 a <5; moderada 5 a <10; severa >=10 eventos/hora). "
            "La interpretación final debe integrarse con edad, síntomas, comorbilidades, examen físico "
            "y criterios vigentes del laboratorio de sueño.",
            note_style
        ))

    story.append(Spacer(1, 18))

    firma_rows = []
    if data.get("medico_lector", "").strip():
        firma_rows.append(["Médico lector", data["medico_lector"]])
    if data.get("registro_medico", "").strip():
        firma_rows.append(["Registro profesional", data["registro_medico"]])
    if firma_rows:
        story.append(Spacer(1, 6))
        table([["Firma", ""]] + firma_rows, widths=[6 * cm, 10 * cm])

    doc.build(story)
    return buffer.getvalue()


# ============================================================
# Formulario
# ============================================================

with st.sidebar:
    st.header("Datos opcionales del reporte")
    institucion = st.text_input("Institución / laboratorio", value="")
    medico_lector = st.text_input("Médico lector", value="")
    registro_medico = st.text_input("Registro profesional", value="")
    mostrar_nota = st.checkbox("Incluir nota técnica", value=True)

st.header("1. Indicación clínica")
indicacion = st.text_area(
    "Indicación",
    value="Evaluación de trastorno respiratorio del sueño en paciente pediátrico.",
    height=80
)

st.header("2. Condiciones del estudio")
col1, col2, col3 = st.columns(3)

with col1:
    fecha_estudio = st.date_input("Fecha del estudio", value=date.today())
    tipo_estudio = st.selectbox(
        "Tipo de estudio",
        [
            "Polisomnografía nocturna completa nivel I",
            "Polisomnografía hospitalaria",
            "Polisomnografía ambulatoria",
            "Otro"
        ]
    )
    duracion_registro = st.number_input("Duración total del registro (min)", min_value=0.0, value=480.0, step=5.0)

with col2:
    tiempo_cama = st.number_input("Tiempo en cama - TIB (min)", min_value=0.0, value=480.0, step=5.0)
    tiempo_sueno = st.number_input("Tiempo total de sueño - TST (min)", min_value=0.0, value=420.0, step=5.0)
    eficiencia = st.number_input("Eficiencia del sueño (%)", min_value=0.0, max_value=100.0, value=87.5, step=0.1)

with col3:
    latencia_sueno = st.number_input("Latencia al sueño (min)", min_value=0.0, value=15.0, step=1.0)
    latencia_rem = st.number_input("Latencia REM (min)", min_value=0.0, value=90.0, step=1.0)
    posicion_predominante = st.selectbox("Posición predominante", ["Supino", "Lateral", "Prono", "Mixta"])

st.header("3. Arquitectura del sueño")
col1, col2, col3, col4 = st.columns(4)

with col1:
    n1 = st.number_input("N1 (% TST)", min_value=0.0, max_value=100.0, value=5.0, step=0.1)
with col2:
    n2 = st.number_input("N2 (% TST)", min_value=0.0, max_value=100.0, value=45.0, step=0.1)
with col3:
    n3 = st.number_input("N3 (% TST)", min_value=0.0, max_value=100.0, value=25.0, step=0.1)
with col4:
    rem = st.number_input("REM (% TST)", min_value=0.0, max_value=100.0, value=25.0, step=0.1)

suma_estadios = n1 + n2 + n3 + rem
if abs(suma_estadios - 100) > 2:
    st.warning(f"La suma de estadios es {suma_estadios:.1f}%. Revise si los porcentajes están completos.")

st.header("4. Eventos respiratorios")
col1, col2, col3, col4 = st.columns(4)

with col1:
    iah = st.number_input("IAH total (eventos/hora)", min_value=0.0, value=3.2, step=0.1)
with col2:
    iah_obstructivo = st.number_input("IAH obstructivo (eventos/hora)", min_value=0.0, value=3.0, step=0.1)
with col3:
    iah_central = st.number_input("IAH central (eventos/hora)", min_value=0.0, value=0.2, step=0.1)
with col4:
    indice_hipopneas = st.number_input("Índice de hipopneas (eventos/hora)", min_value=0.0, value=2.5, step=0.1)

col1, col2 = st.columns(2)
with col1:
    iah_rem = st.number_input("IAH en REM (eventos/hora)", min_value=0.0, value=6.0, step=0.1)
with col2:
    iah_nrem = st.number_input("IAH en NREM (eventos/hora)", min_value=0.0, value=2.0, step=0.1)

st.header("5. Oxigenación")
col1, col2, col3, col4 = st.columns(4)

with col1:
    spo2_basal = st.number_input("SpO₂ basal (%)", min_value=0.0, max_value=100.0, value=96.0, step=0.1)
with col2:
    spo2_min = st.number_input("SpO₂ mínima (%)", min_value=0.0, max_value=100.0, value=88.0, step=0.1)
with col3:
    tiempo_menor_90 = st.number_input("Tiempo con SpO₂ <90% (% TST)", min_value=0.0, max_value=100.0, value=1.5, step=0.1)
with col4:
    odi = st.number_input("ODI / índice de desaturación", min_value=0.0, value=4.0, step=0.1)

st.header("6. Eventos cardiovasculares y movimientos")
col1, col2, col3, col4 = st.columns(4)

with col1:
    fc_promedio = st.number_input("Frecuencia cardíaca promedio", min_value=0.0, value=85.0, step=1.0)
with col2:
    fc_min = st.number_input("Frecuencia cardíaca mínima", min_value=0.0, value=62.0, step=1.0)
with col3:
    fc_max = st.number_input("Frecuencia cardíaca máxima", min_value=0.0, value=125.0, step=1.0)
with col4:
    arritmias = st.selectbox("Arritmias", ["No", "Sí"])

col1, col2 = st.columns(2)
with col1:
    plmi = st.number_input("PLMI (eventos/hora)", min_value=0.0, value=2.0, step=0.1)
with col2:
    indice_arousal = st.number_input("Índice de arousal (eventos/hora)", min_value=0.0, value=8.0, step=0.1)

st.header("7. Análisis posicional")
col1, col2 = st.columns(2)

with col1:
    iah_supino = st.number_input("IAH en supino", min_value=0.0, value=5.0, step=0.1)
with col2:
    iah_lateral = st.number_input("IAH en lateral", min_value=0.0, value=2.0, step=0.1)

st.header("8. Calidad técnica del estudio")
calidad = st.selectbox("Calidad técnica", ["Adecuada", "Limitada", "Subóptima"])
artefactos = st.text_area(
    "Canales perdidos o artefactos relevantes",
    value="Sin artefactos significativos que limiten la interpretación.",
    height=80
)


# ============================================================
# Datos derivados
# ============================================================

diagnostico_iah = clasificar_iah(iah)
grado_corto = grado_corto_iah(iah)
interp_oxigenacion = interpretar_oxigenacion(spo2_min, tiempo_menor_90)
interp_eficiencia = interpretar_eficiencia(eficiencia)
interp_arousal = interpretar_arousals(indice_arousal)
interp_plmi = interpretar_plmi(plmi)
frase_rem = patron_rem(iah_rem, iah_nrem)
frase_posicion = patron_posicional(iah_supino, iah_lateral)

data = {
    "institucion": institucion,
    "medico_lector": medico_lector,
    "registro_medico": registro_medico,
    "mostrar_nota": mostrar_nota,
    "indicacion": indicacion,
    "fecha_estudio": fecha_estudio,
    "tipo_estudio": tipo_estudio,
    "duracion_registro": duracion_registro,
    "tiempo_cama": tiempo_cama,
    "tiempo_sueno": tiempo_sueno,
    "eficiencia": eficiencia,
    "latencia_sueno": latencia_sueno,
    "latencia_rem": latencia_rem,
    "posicion_predominante": posicion_predominante,
    "n1": n1,
    "n2": n2,
    "n3": n3,
    "rem": rem,
    "iah": iah,
    "iah_obstructivo": iah_obstructivo,
    "iah_central": iah_central,
    "indice_hipopneas": indice_hipopneas,
    "iah_rem": iah_rem,
    "iah_nrem": iah_nrem,
    "spo2_basal": spo2_basal,
    "spo2_min": spo2_min,
    "tiempo_menor_90": tiempo_menor_90,
    "odi": odi,
    "fc_promedio": fc_promedio,
    "fc_min": fc_min,
    "fc_max": fc_max,
    "arritmias": arritmias,
    "plmi": plmi,
    "indice_arousal": indice_arousal,
    "iah_supino": iah_supino,
    "iah_lateral": iah_lateral,
    "calidad": calidad,
    "artefactos": artefactos,
    "diagnostico_iah": diagnostico_iah,
    "grado_corto": grado_corto,
    "interp_oxigenacion": interp_oxigenacion,
    "interp_eficiencia": interp_eficiencia,
    "interp_arousal": interp_arousal,
    "interp_plmi": interp_plmi,
    "frase_rem": frase_rem,
    "frase_posicion": frase_posicion,
}

pdf_bytes = build_pdf(data)

st.divider()
st.header("Resumen automático")

m1, m2, m3, m4 = st.columns(4)
m1.metric("IAH", f"{iah:.1f}/h", grado_corto)
m2.metric("SpO₂ mínima", f"{spo2_min:.1f}%")
m3.metric("Arousal", f"{indice_arousal:.1f}/h")
m4.metric("PLMI", f"{plmi:.1f}/h")

st.markdown(
    f"""
    <div class="report-box">
    <b>Impresión clínica integrada:</b><br><br>
    La polisomnografía pediátrica muestra un tiempo total de sueño de <b>{tiempo_sueno:.1f} minutos</b>
    y una eficiencia del sueño de <b>{eficiencia:.1f}%</b>, compatible con {interp_eficiencia}.
    El índice de apnea-hipopnea fue de <b>{iah:.1f} eventos/hora</b>, con componente obstructivo de
    <b>{iah_obstructivo:.1f} eventos/hora</b>, hallazgo que clasifica el estudio como
    <b>{diagnostico_iah}</b>.<br><br>
    La saturación basal fue de <b>{spo2_basal:.1f}%</b>, con nadir de <b>{spo2_min:.1f}%</b>
    y tiempo con SpO₂ &lt;90% de <b>{tiempo_menor_90:.1f}%</b> del TST, lo cual sugiere
    <b>{interp_oxigenacion}</b>. El índice de arousal fue de <b>{indice_arousal:.1f} eventos/hora</b>,
    compatible con <b>{interp_arousal}</b>. El patrón respiratorio fue {frase_rem} y {frase_posicion}.
    </div>
    """,
    unsafe_allow_html=True
)

st.download_button(
    label="📄 Descargar reporte en PDF",
    data=pdf_bytes,
    file_name="reporte_polisomnografia_pediatrica.pdf",
    mime="application/pdf",
    use_container_width=True
)
