import streamlit as st
import os

st.set_page_config(
    page_title="Sistema de Autorizaciones",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Usuarios ──────────────────────────────────────────────────────────────
USERS = {
    "admin@ejemplo.com":       {"password": "admin123", "profile": 1, "name": "Administrador"},
    "auth1@ejemplo.com":       {"password": "pass123",  "profile": 2, "name": "Autorizante 1"},
    "auth2@ejemplo.com":       {"password": "pass123",  "profile": 3, "name": "Autorizante 2"},
    "user@ejemplo.com":        {"password": "pass123",  "profile": 4, "name": "Usuario"},
    "solicitante@ejemplo.com": {"password": "pass123",  "profile": 5, "name": "Solicitante"},
}

# ─── Inicializar session_state ─────────────────────────────────────────────
if "logged_in" not in st.session_state:
    st.session_state.logged_in  = False
if "user_email" not in st.session_state:
    st.session_state.user_email = ""
if "user_profile" not in st.session_state:
    st.session_state.user_profile = None
if "user_name" not in st.session_state:
    st.session_state.user_name  = ""

# ─── CSS ───────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    [data-testid="stSidebarNav"] { display: none; }
    .stButton>button { border-radius: 8px; font-weight: 600; }
</style>
""", unsafe_allow_html=True)


# ─── Página de login ───────────────────────────────────────────────────────
def login_page():
    col_l, col_c, col_r = st.columns([1, 1.2, 1])
    with col_c:
        st.markdown("## 📋 Sistema de Autorizaciones")
        st.markdown("Ingresa tus credenciales para continuar.")
        st.divider()

        with st.form("login_form"):
            email    = st.text_input("📧 Email", placeholder="usuario@ejemplo.com")
            password = st.text_input("🔒 Contraseña", type="password")
            submitted = st.form_submit_button("Ingresar", use_container_width=True, type="primary")

        if submitted:
            if email in USERS and USERS[email]["password"] == password:
                user = USERS[email]
                st.session_state.logged_in    = True
                st.session_state.user_email   = email
                st.session_state.user_profile = user["profile"]
                st.session_state.user_name    = user["name"]
                st.rerun()
            else:
                st.error("Email o contraseña incorrectos.")

        with st.expander("🔑 Credenciales de prueba"):
            st.markdown("""
| Email | Contraseña | Acceso |
|-------|------------|--------|
| admin@ejemplo.com | admin123 | Todo |
| auth1@ejemplo.com | pass123 | Aut. 1 |
| auth2@ejemplo.com | pass123 | Dashboard |
| user@ejemplo.com | pass123 | Dashboard |
| solicitante@ejemplo.com | pass123 | Solo Formulario |
""")


# ─── Si NO está logueado: mostrar solo login ───────────────────────────────
if not st.session_state.logged_in:
    login_page()
    st.stop()   # ← detiene todo lo demás


# ─── Si SÍ está logueado: construir navegación ────────────────────────────
profile = st.session_state.user_profile

# Definir todas las páginas posibles
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

pg_formulario   = st.Page(os.path.join(BASE_DIR, "pages", "01_carga_formulario.py"), title="📝 Carga Formulario")
pg_dashboard    = st.Page(os.path.join(BASE_DIR, "pages", "02_dashboard.py"),        title="📊 Dashboard")
pg_autorizante1 = st.Page(os.path.join(BASE_DIR, "pages", "03_autorizante1.py"),     title="✅ Autorizante 1")
pg_autorizante2 = st.Page(os.path.join(BASE_DIR, "pages", "04_autorizante2.py"),     title="🔐 Autorizante 2")

# Páginas según perfil
PAGES_BY_PROFILE = {
    1: [pg_formulario, pg_dashboard, pg_autorizante1, pg_autorizante2],
    2: [pg_formulario, pg_dashboard, pg_autorizante1],
    3: [pg_formulario, pg_dashboard],
    4: [pg_formulario, pg_dashboard],
    5: [pg_formulario],
}

pages = PAGES_BY_PROFILE.get(profile, [pg_formulario])

# Sidebar: info de usuario + logout
with st.sidebar:
    st.markdown(f"### 👤 {st.session_state.user_name}")
    st.caption(st.session_state.user_email)
    st.caption(f"Perfil {profile}")
    st.divider()
    if st.button("🚪 Cerrar sesión", use_container_width=True):
        st.session_state.logged_in    = False
        st.session_state.user_email   = ""
        st.session_state.user_profile = None
        st.session_state.user_name    = ""
        st.rerun()

# Lanzar navegación
nav = st.navigation(pages)
nav.run()
