"""Map rendering with a graceful fallback when streamlit-folium is unavailable."""
import streamlit as st
import folium
from folium import GeoJson


def show_farm_map(farm, height=420):
    boundary = farm.get("boundary_geojson")
    lat, lon = farm.get("latitude"), farm.get("longitude")
    if lat is None or lon is None:
        st.info("No farm coordinates available to map.")
        return
    m = folium.Map(location=[lat, lon], zoom_start=14, control_scale=True, tiles="CartoDB positron")
    if boundary:
        GeoJson(boundary, name="Farm boundary", tooltip=farm.get("name", "Farm")).add_to(m)
        try:
            bounds = folium.GeoJson(boundary).get_bounds()
            m.fit_bounds(bounds)
        except Exception:
            pass
    folium.Marker([lat, lon], tooltip=farm.get("name", "Farm"), popup=farm.get("project_identifier", "")).add_to(m)
    try:
        from streamlit_folium import st_folium
        st_folium(m, height=height, use_container_width=True, returned_objects=[])
    except ImportError:
        st.map({"lat": [lat], "lon": [lon]})
        st.caption("Install streamlit-folium for interactive farm-boundary maps.")
