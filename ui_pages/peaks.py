import streamlit as st
from src.views import render_page

render_page("Peak Insights", st.session_state["_dashboard_data"])
