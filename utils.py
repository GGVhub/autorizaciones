"""
utils.py — Funciones de base de datos y utilidades compartidas.
"""
import streamlit as st
import pandas as pd
from datetime import datetime


# ─── Perfiles y accesos ────────────────────────────────────────────────────
PAGE_ACCESS = {
    1: ["formulario", "dashboard", "autorizante1", "autorizante2"],
    2: ["formulario", "dashboard", "autorizante1"],
    3: ["formulario", "dashboard"],
    4: ["formulario", "dashboard"],
    5: ["formulario"],
}


def require_login():
    """Redirige a login si no está autenticado."""
    if not st.session_state.get("logged_in"):
        st.error("🔒 Debes iniciar sesión primero.")
        st.stop()


def require_page_access(page_slug: str):
    """Con st.navigation() el acceso ya está controlado en app.py. 
    Esta función queda como fallback."""
    if not st.session_state.get("logged_in"):
        st.error("🔒 Sesión expirada. Volvé al inicio.")
        st.stop()


# ─── Conexión ──────────────────────────────────────────────────────────────
@st.cache_resource
@st.cache_resource
@st.cache_resource
@st.cache_resource
def get_connection():
    try:
        return st.connection("postgres", type="sql")
    except Exception as e:
        st.error(f"❌ No se pudo conectar a la base de datos: {e}")
        st.stop()

def run_query(sql: str, params: tuple = None, fetch: bool = True):
    """
    Ejecuta una query. 
    - fetch=True  → retorna DataFrame
    - fetch=False → ejecuta INSERT/UPDATE sin retorno
    """
    conn = get_connection()
    if fetch:
        if params:
            return conn.query(sql, params=params, ttl=0)
        return conn.query(sql, ttl=0)
    else:
        with conn.session as session:
            if params:
                session.execute(sql, params)
            else:
                session.execute(sql)
            session.commit()


# ─── Helpers de formato ────────────────────────────────────────────────────
def fmt_currency(val) -> str:
    """Formatea número como moneda ARS."""
    try:
        return f"$ {float(val):,.2f}"
    except (TypeError, ValueError):
        return "$ 0,00"


def fmt_bool(val) -> str:
    return "✅" if val else "❌"


def badge_prioridad(val: str) -> str:
    colors = {"Alta": "🔴", "Media": "🟡", "Baja": "🟢"}
    return f"{colors.get(val, '⚪')} {val}"
