import streamlit as st

from backend.constants.ui import APP_SUBTITLE, APP_TITLE


def render_header() -> None:
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
        f'<div class="big-title">{APP_TITLE}</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        f'<div class="subtitle">{APP_SUBTITLE}</div>',
        unsafe_allow_html=True,
    )

    st.divider()