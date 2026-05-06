import streamlit as st


def render_header():
    st.markdown("""
    <style>
    .big-title {
        font-size: 38px;
        font-weight: 800;
        margin-bottom: 5px;
    }
    .subtitle {
        font-size: 18px;
        color: #666;
        margin-bottom: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown(
        '<div class="big-title">🚗 Automação Completa Tracers + Mind7</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="subtitle">Fluxo automatizado: Tracers → Excel → Mind7 → CPF/CNPJ → Resultado Final</div>',
        unsafe_allow_html=True
    )

    st.divider()