"""
01_carga_formulario.py — Carga de nuevos formularios de gasto.
Acceso: Perfiles 1-5 (todos).
"""
import streamlit as st
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from utils import require_page_access, get_connection
from sqlalchemy import text

# ─── Seguridad ─────────────────────────────────────────────────────────────
require_page_access("formulario")

st.title("📝 Carga de Formulario")
st.caption("Completa todos los campos para registrar una solicitud de gasto.")
st.divider()

conn = get_connection()

# ─── Formulario ────────────────────────────────────────────────────────────
with st.form("form_carga", clear_on_submit=True):
    st.subheader("📌 Datos del Solicitante")
    col1, col2 = st.columns(2)
    with col1:
        solicitante = st.text_input("Nombre del Solicitante *", placeholder="Ej: Juan Pérez")
    with col2:
        area = st.text_input("Área / Dependencia *", placeholder="Ej: Dirección de Salud")

    st.subheader("🛒 Detalle del Bien o Servicio")
    col3, col4 = st.columns([2, 1])
    with col3:
        bien_servicio = st.text_input("Bien / Servicio *", placeholder="Ej: Resmas A4")
    with col4:
        unidad_medida = st.text_input("Unidad de Medida *", placeholder="Ej: Resma, Litro, Unidad")

    col5, col6 = st.columns(2)
    with col5:
        precio_unitario = st.number_input(
            "Precio Unitario ($) *",
            min_value=0.01, step=0.01, format="%.2f",
            help="Precio por unidad en ARS"
        )
    with col6:
        cantidad = st.number_input(
            "Cantidad *",
            min_value=1, step=1,
            help="Número de unidades"
        )

    total_preview = precio_unitario * cantidad
    st.info(f"💰 **Total estimado:** $ {total_preview:,.2f}")

    st.subheader("📋 Clasificación")
    col7, col8 = st.columns(2)
    with col7:
        tipo_gasto = st.selectbox(
            "Tipo de Gasto *",
            options=["Esencial", "Serv. Basico", "Politica del gobernador"],
            help="Categoría presupuestaria del gasto"
        )
    with col8:
        prioridad = st.selectbox(
            "Prioridad *",
            options=["Alta", "Media", "Baja"],
            help="Nivel de urgencia o importancia"
        )

    gasto_escuelas = st.checkbox(
        "🏫 ¿Es gasto destinado a Escuelas?",
        help="Marcar si el gasto impacta directamente en establecimientos educativos"
    )

    st.subheader("📄 Justificación")
    justificacion = st.text_area(
        "Justificación del gasto *",
        height=120,
        placeholder="Describe brevemente por qué se requiere este gasto, su impacto y urgencia...",
        help="Mínimo 20 caracteres"
    )

    st.divider()
    submitted = st.form_submit_button("💾 Registrar Solicitud", use_container_width=True, type="primary")

# ─── Validación y guardado ─────────────────────────────────────────────────
if submitted:
    errors = []
    if not solicitante.strip():
        errors.append("El nombre del solicitante es obligatorio.")
    if not area.strip():
        errors.append("El área es obligatoria.")
    if not bien_servicio.strip():
        errors.append("El bien/servicio es obligatorio.")
    if not unidad_medida.strip():
        errors.append("La unidad de medida es obligatoria.")
    if precio_unitario <= 0:
        errors.append("El precio unitario debe ser mayor a 0.")
    if cantidad <= 0:
        errors.append("La cantidad debe ser mayor a 0.")
    if len(justificacion.strip()) < 20:
        errors.append("La justificación debe tener al menos 20 caracteres.")

    if errors:
        for err in errors:
            st.error(f"⚠️ {err}")
    else:
        try:
            sql = text("""
                INSERT INTO formularios
                    (solicitante, area, bien_servicio, unidad_medida,
                     precio_unitario, cantidad, justificacion,
                     tipo_gasto, prioridad, gasto_escuelas)
                VALUES
                    (:solicitante, :area, :bien_servicio, :unidad_medida,
                     :precio_unitario, :cantidad, :justificacion,
                     :tipo_gasto, :prioridad, :gasto_escuelas)
            """)
            with conn.session as session:
                session.execute(sql, {
                    "solicitante":    solicitante.strip(),
                    "area":           area.strip(),
                    "bien_servicio":  bien_servicio.strip(),
                    "unidad_medida":  unidad_medida.strip(),
                    "precio_unitario": float(precio_unitario),
                    "cantidad":        int(cantidad),
                    "justificacion":   justificacion.strip(),
                    "tipo_gasto":      tipo_gasto,
                    "prioridad":       prioridad,
                    "gasto_escuelas":  bool(gasto_escuelas),
                })
                session.commit()

            st.success(
                f"✅ **Solicitud registrada exitosamente.**\n\n"
                f"Solicitante: **{solicitante}** | Total: **$ {total_preview:,.2f}** | "
                f"Prioridad: **{prioridad}**"
            )
            st.balloons()

        except Exception as e:
            st.error(f"❌ Error al guardar en la base de datos: {e}")

# ─── Info de ayuda ─────────────────────────────────────────────────────────
with st.expander("ℹ️ Ayuda sobre los campos"):
    st.markdown("""
| Campo | Descripción |
|-------|-------------|
| **Tipo de Gasto** | Clasificación presupuestaria: *Esencial* (indispensable), *Serv. Basico* (servicios base), *Politica del gobernador* (lineamiento político) |
| **Prioridad** | *Alta*: urgente/crítico · *Media*: necesario · *Baja*: puede esperar |
| **Gasto Escuelas** | Marcar si el destino final son establecimientos educativos |
| **Total** | Se calcula automáticamente: Precio Unitario × Cantidad |
""")
