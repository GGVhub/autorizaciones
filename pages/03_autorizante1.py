"""
03_autorizante1.py — Panel de autorización de primer nivel.
Acceso: Perfiles 1 y 2.
"""
import streamlit as st
import pandas as pd
from datetime import datetime
from sqlalchemy import text
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from utils import require_page_access, get_connection, fmt_currency

require_page_access("autorizante1")

st.title("✅ Autorizante — Nivel 1")
st.caption("Gestiona las solicitudes pendientes de primera autorización.")

conn = get_connection()

# ─── Cargar pendientes ─────────────────────────────────────────────────────
def load_pending():
    return conn.query(
        "SELECT * FROM formularios WHERE (autorizado1 IS NULL OR autorizado1 = FALSE) ORDER BY prioridad, created_at",
        ttl=0
    )

try:
    df = load_pending()
except Exception as e:
    st.error(f"❌ Error de base de datos: {e}")
    st.stop()

# ─── KPIs ──────────────────────────────────────────────────────────────────
c1, c2, c3 = st.columns(3)
c1.metric("📋 Pendientes",       len(df))
c2.metric("💰 Monto Pendiente",  fmt_currency(pd.to_numeric(df["total"], errors="coerce").sum()) if not df.empty else "$ 0,00")
alta_count = len(df[df["prioridad"] == "Alta"]) if not df.empty else 0
c3.metric("🔴 Alta Prioridad",   alta_count)

st.divider()

if df.empty:
    st.success("🎉 ¡No hay formularios pendientes de autorización!")
    st.stop()

# ─── Filtro rápido ─────────────────────────────────────────────────────────
col_f1, col_f2 = st.columns(2)
with col_f1:
    prioridad_filter = st.multiselect(
        "Filtrar por prioridad", ["Alta", "Media", "Baja"],
        default=["Alta", "Media", "Baja"]
    )
with col_f2:
    area_filter = st.multiselect(
        "Filtrar por área",
        df["area"].dropna().unique().tolist(),
    )

df_show = df.copy()
if prioridad_filter:
    df_show = df_show[df_show["prioridad"].isin(prioridad_filter)]
if area_filter:
    df_show = df_show[df_show["area"].isin(area_filter)]

st.subheader(f"📄 Solicitudes Pendientes ({len(df_show)})")

# ─── Tabla con botones de acción ───────────────────────────────────────────
PRIORIDAD_COLORS = {"Alta": "🔴", "Media": "🟡", "Baja": "🟢"}

for _, row in df_show.iterrows():
    fid = int(row["id"])
    with st.container():
        with st.expander(
            f"#{fid} — {row['solicitante']} | {row['area']} | "
            f"{PRIORIDAD_COLORS.get(row['prioridad'],'')} {row['prioridad']} | "
            f"💰 {fmt_currency(row['total'])}",
            expanded=False,
        ):
            col_det1, col_det2, col_det3 = st.columns(3)
            col_det1.markdown(f"**Bien/Servicio:** {row['bien_servicio']}")
            col_det1.markdown(f"**Unidad:** {row['unidad_medida']}")
            col_det2.markdown(f"**Cantidad:** {row['cantidad']}")
            col_det2.markdown(f"**P. Unitario:** {fmt_currency(row['precio_unitario'])}")
            col_det3.markdown(f"**Tipo Gasto:** {row['tipo_gasto']}")
            col_det3.markdown(f"**Escuelas:** {'✅' if row['gasto_escuelas'] else '❌'}")

            st.markdown(f"**Justificación:** {row['justificacion']}")
            st.markdown(f"*Cargado:* {pd.to_datetime(row['created_at']).strftime('%d/%m/%Y %H:%M') if pd.notna(row['created_at']) else '—'}")

            st.markdown("---")
            btn_col1, btn_col2, btn_col3 = st.columns([2, 2, 4])

            with btn_col1:
                if st.button(f"✅ Autorizar", key=f"aut1_si_{fid}", type="primary"):
                    st.session_state[f"confirm_aut1_{fid}"] = "autorizar"

            with btn_col2:
                if st.button(f"❌ Rechazar", key=f"aut1_no_{fid}"):
                    st.session_state[f"confirm_aut1_{fid}"] = "rechazar"

            # Confirmación
            if st.session_state.get(f"confirm_aut1_{fid}"):
                action = st.session_state[f"confirm_aut1_{fid}"]
                action_label = "autorizar" if action == "autorizar" else "rechazar"
                st.warning(f"⚠️ ¿Confirmas que deseas **{action_label}** el formulario #{fid}?")

                c_yes, c_no = st.columns(2)
                with c_yes:
                    if st.button(f"Sí, confirmar", key=f"confirm_yes_aut1_{fid}", type="primary"):
                        nuevo_val = True if action == "autorizar" else False
                        try:
                            sql = text("""
                                UPDATE formularios
                                SET autorizado1 = :val, fecha_aut1 = :now
                                WHERE id = :id
                            """)
                            with conn.session as session:
                                session.execute(sql, {
                                    "val": nuevo_val,
                                    "now": datetime.now(),
                                    "id":  fid,
                                })
                                session.commit()
                            del st.session_state[f"confirm_aut1_{fid}"]
                            verb = "autorizado" if nuevo_val else "rechazado"
                            st.success(f"✅ Formulario #{fid} {verb} correctamente.")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error al actualizar: {e}")

                with c_no:
                    if st.button("Cancelar", key=f"confirm_no_aut1_{fid}"):
                        del st.session_state[f"confirm_aut1_{fid}"]
                        st.rerun()

st.divider()
if st.button("🔄 Actualizar lista", use_container_width=True):
    st.rerun()

# ─── Historial reciente ────────────────────────────────────────────────────
with st.expander("📜 Historial — últimas autorizaciones/rechazos"):
    df_hist = conn.query(
        "SELECT id, solicitante, area, total, autorizado1, fecha_aut1 "
        "FROM formularios WHERE fecha_aut1 IS NOT NULL ORDER BY fecha_aut1 DESC LIMIT 20",
        ttl=0
    )
    if not df_hist.empty:
        df_hist["autorizado1"] = df_hist["autorizado1"].apply(lambda x: "✅ Autorizado" if x else "❌ Rechazado")
        df_hist["total"]       = pd.to_numeric(df_hist["total"], errors="coerce").apply(fmt_currency)
        df_hist["fecha_aut1"]  = pd.to_datetime(df_hist["fecha_aut1"]).dt.strftime("%d/%m/%Y %H:%M")
        df_hist.columns = ["ID", "Solicitante", "Área", "Total", "Estado", "Fecha"]
        st.dataframe(df_hist, use_container_width=True, hide_index=True)
    else:
        st.info("Sin historial aún.")
