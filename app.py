"""CampusEnergy AI entrypoint: cache canonical artifacts and route real pages."""
import streamlit as st
from src.app_support import load_dashboard_artifacts
from src.config import ARTIFACTS, OUTPUTS
from src.dashboard import PAGES, apply_style

st.set_page_config(page_title="CampusEnergy AI", page_icon="⚡", layout="wide", initial_sidebar_state="auto")
apply_style()


@st.cache_resource(show_spinner="Loading verified forecast…")
def cached_artifacts(signature):
    return load_dashboard_artifacts()


try:
    paths = [ARTIFACTS/"metrics.json", ARTIFACTS/"model_bundle.joblib", ARTIFACTS/"feature_importance.csv",
             OUTPUTS/"future_24h_forecast.csv", OUTPUTS/"test_predictions.csv"]
    signature = tuple((str(p), p.stat().st_mtime_ns, p.stat().st_size) for p in paths)
    data = cached_artifacts(signature)
except (FileNotFoundError, ValueError, KeyError, OSError) as exc:
    st.title("CampusEnergy AI")
    st.error("The verified forecast package could not be loaded. Restore the canonical Phase 1 artifacts before opening the dashboard.")
    with st.expander("Technical detail"):
        st.code(str(exc))
    st.stop()

st.session_state["_dashboard_data"] = data
forecast = data["forecast"]
slugs = ["overview", "forecast", "performance", "peaks", "errors", "about"]
# Keep page scripts outside Streamlit's auto-discovered legacy `pages` folder.
# Every cold/deep-link session must execute this entrypoint before its page.
pages = [st.Page(f"ui_pages/{slug}.py", title=title, url_path=slug, default=(slug == "overview"))
         for slug, title in zip(slugs, PAGES)]
current = st.navigation(pages, position="hidden")
with st.sidebar:
    st.markdown('<div class="eyebrow">CAMPUS / ENERGY INTELLIGENCE</div>', unsafe_allow_html=True)
    st.markdown("## CampusEnergy AI")
    st.caption("Forecast demand. Detect peaks. Support smarter energy decisions.")
    st.divider()
    for target in pages:
        st.page_link(target)
    st.divider()
    st.markdown("**Forecast window**")
    st.write(f"{forecast.timestamp.min():%d %B %Y}")
    st.caption(f"{forecast.timestamp.min():%H:%M} – {forecast.timestamp.max():%H:%M} · {len(forecast)} hourly intervals")
    st.markdown('<span class="badge">Synthetic prototype data</span>', unsafe_allow_html=True)
    st.caption("Single building · No live meter connection")
    st.caption("AI forecast → manager verification → human decision")
current.run()
