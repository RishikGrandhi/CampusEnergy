import streamlit as st
from src.views import render_page

render_page("24-Hour Forecast", st.session_state["_dashboard_data"])
