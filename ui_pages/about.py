import streamlit as st
from src.views import render_page

render_page("Responsible AI / About", st.session_state["_dashboard_data"])
