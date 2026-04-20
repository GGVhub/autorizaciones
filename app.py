import streamlit as st

# ─── Configuración de página ───────────────────────────────────────────────
st.set_page_config(
    page_title="Sistema de Autorizaciones",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Usuarios hardcodeados ─────────────────────────────────────────────────
USERS = {
    "admin@ejemplo.com":       {"password": "admin123", "profile": 1, "name": "Administrador"},
    "auth1@ejemplo.com":       {"password": "pass123",  "profile": 2, "name": "Autorizante 1"},
    "auth2@ejemplo.com":       {"password": "pass123",  "profile": 3, "name": "Autorizante 2"},
    "user@ejemplo.com":        {"password": "pass123",  "profile": 4, "name": "Usuario"},
    "solicitante@ejemplo.com": {"password": "pass123",  "profile": 5, "name": "Solicitante"},
}

# Páginas por perfil (profile_id: lista de slugs)
PAGE_ACCESS = {
    1: ["formulario", "dashboard", "autorizante1", "autorizante2"],
    2: ["formulario", "dashboard", "autorizante1"],
    3: ["formulario", "dashboard"],
    4: ["formulario", "dashboard"],
    5: ["formulario"],
}

PAGE_META = {
    "formulario":   {"label": "📝 Carga Formulario",  "file": "pages/01_carga_formulario.py"},
    "dashboard":    {"label": "📊 Dashboard",          "file": "pages/02_dashboard.py"},
    "autorizante1": {"label": "✅ Autorizante 1",       "file": "pages/03_autorizante1.py"},
    "autorizante2": {"label": "🔐 Autorizante 2",       "file": "pages/04_autorizante2.py"},
}

# ─── Inicializar session_state ─────────────────────────────────────────────
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user_email" not in st.session_state:
    st.session_state.user_email = ""
if "user_profile" not in st.session_state:
    st.session_state.user_profile = None
if "user_name" not in st.session_state:
    st.session_state.user_name = ""

# ─── CSS global ───────────────────────────────────────────────────────────
st.markdown("""
<style>
    .login-box {
        max-width: 420px;
        margin: 60px auto;
        padding: 40px;
        background: #ffffff;
        border-radius: 16px;
        box-shadow: 0 4px 24px rgba(0,0,0,0.10);
    }
    .login-title {
        text-align: center;
        font-size: 2rem;
        font-weight: 700;
        color: #1a3a5c;
        margin-bottom: 8px;
    }
    .login-sub {
        text-align: center;
        color: #6b7280;
        margin-bottom: 28px;
        font-size: 0.95rem;
    }
    .stButton>button {
        width: 100%;
        border-radius: 8px;
        font-weight: 600;
        height: 2.8rem;
    }
    [data-testid="stSidebarNav"] { display: none; }
</style>
""", unsafe_allow_html=True)


# ─── LOGIN ─────────────────────────────────────────────────────────────────
def show_login():
    col_l, col_c, col_r = st.columns([1, 1.2, 1])
    with col_c:
        st.markdown('<div class="login-title">📋 Sistema de Autorizaciones</div>', unsafe_allow_html=True)
        st.markdown('<div class="login-sub">Ingresa tus credenciales para continuar</div>', unsafe_allow_html=True)

        with st.form("login_form", clear_on_submit=False):
            email    = st.text_input("📧 Email", placeholder="usuario@ejemplo.com")
            password = st.text_input("🔒 Contraseña", type="password", placeholder="••••••••")
            submitted = st.form_submit_button("Ingresar", use_container_width=True)

        if submitted:
            if not email or not password:
                st.error("Completa todos los campos.")
            elif email in USERS and USERS[email]["password"] == password:
                user = USERS[email]
                st.session_state.logged_in    = True
                st.session_state.user_email   = email
                st.session_state.user_profile = user["profile"]
                st.session_state.user_name    = user["name"]
                st.success(f"¡Bienvenido, {user['name']}!")
                st.rerun()
            else:
                st.error("Email o contraseña incorrectos.")

        st.markdown("---")
        with st.expander("🔑 Credenciales de prueba"):
            st.markdown("""
| Perfil | Email | Contraseña |
|--------|-------|------------|
| Admin  | admin@ejemplo.com | admin123 |
| Auth 1 | auth1@ejemplo.com | pass123 |
| Auth 2 | auth2@ejemplo.com | pass123 |
| User   | user@ejemplo.com | pass123 |
| Solicitante | solicitante@ejemplo.com | pass123 |
""")


# ─── SIDEBAR ───────────────────────────────────────────────────────────────
def show_sidebar():
    with st.sidebar:
        st.markdown(f"### 👤 {st.session_state.user_name}")
        st.caption(f"{st.session_state.user_email}")
        st.caption(f"Perfil {st.session_state.user_profile}")
        st.divider()

        allowed = PAGE_ACCESS.get(st.session_state.user_profile, [])
        st.markdown("**Navegación**")
        for slug in ["formulario", "dashboard", "autorizante1", "autorizante2"]:
            if slug in allowed:
                meta = PAGE_META[slug]
                st.page_link(meta["file"], label=meta["label"])

        st.divider()
        if st.button("🚪 Cerrar sesión", use_container_width=True):
            for key in ["logged_in", "user_email", "user_profile", "user_name"]:
                st.session_state[key] = False if key == "logged_in" else "" if key != "user_profile" else None
            st.rerun()


# ─── MAIN ──────────────────────────────────────────────────────────────────
if not st.session_state.logged_in:
    show_login()
else:
    show_sidebar()
    st.markdown(f"## 🏠 Inicio — Sistema de Autorizaciones")
    st.info(f"Bienvenido **{st.session_state.user_name}**. Usa el menú lateral para navegar.")

    profile = st.session_state.user_profile
    allowed = PAGE_ACCESS.get(profile, [])

    col1, col2, col3, col4 = st.columns(4)
    accesos = {
        "formulario":   ("📝", "Formulario",   col1),
        "dashboard":    ("📊", "Dashboard",    col2),
        "autorizante1": ("✅", "Autorizante 1", col3),
        "autorizante2": ("🔐", "Autorizante 2", col4),
    }
    for slug, (icon, label, col) in accesos.items():
        with col:
            if slug in allowed:
                st.success(f"{icon} **{label}**\n\nAcceso ✓")
            else:
                st.error(f"{icon} **{label}**\n\nSin acceso ✗")
