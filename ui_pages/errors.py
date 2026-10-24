import streamlit as st
from src.views import render_page

render_page("Error Analysis", st.session_state["_dashboard_data"])
