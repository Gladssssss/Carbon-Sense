import streamlit as st
import pandas as pd
import plotly.express as px
import base64
st.set_page_config(page_title="Carbon Sense", layout="wide", page_icon="🌱")
def get_logo_base64(path="logo.png"):
    try:
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    except Exception:
        return None
logo_base64 = get_logo_base64()
if logo_base64:
    st.markdown(
        f"<img src='data:image/png;base64,{logo_base64}' width='140' style='display:block;margin:auto;'>",
        unsafe_allow_html=True
    )
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;700&display=swap');
        html, body, [class*="css"] {
            font-family: 'Montserrat', 'Segoe UI', sans-serif !important;
            background: #fff !important;
            color: #111 !important;
        }
        h1, h2, h3, h4, h5, h6, .stCaption, .stMarkdown, .stTextInput label, .stSidebar, .stButton button, .stAlert, .report-btn {
            font-family: 'Montserrat', 'Segoe UI', sans-serif !important;
            color: #111 !important;
        }
        section[data-testid="stSidebar"] h2 {color: #111 !important; font-weight: 700;}
        div[data-testid="stDataFrame"] table {border: 1px solid #B7E4C7; border-radius: 8px; background-color: white; color: black;}
        .info-tooltip {font-size:14px; color:#111; cursor:pointer;}
        [data-testid="stSidebar"] {background: #fff !important;}
    </style>
""", unsafe_allow_html=True)
st.title("🌿 Carbon Sense")
st.caption("Estimate and visualize CO₂ emissions for logistics and operations")

def executive_summary(total, optimized, reduction):
    if reduction > 40:
        msg = "Outstanding! Your optimizations yield significant reductions in carbon footprint."
    elif reduction > 20:
        msg = "Good progress. Consider further electrification and efficiency upgrades."
    else:
        msg = "There's room for improvement. Explore emission reduction strategies."
    return f"""
    <div style='background:#fff;border-radius:12px;padding:25px 24px;margin-bottom:14px;color:#111;font-family:Montserrat,sans-serif;'>
        <h3 style='color:#111;font-weight:700;margin-bottom:0;font-family:Montserrat,sans-serif;'>Executive Summary</h3>
        <p style='font-size:18px;margin:8px 0;font-family:Montserrat,sans-serif;'>Total Baseline Emissions: <strong>{total:.1f} tons CO₂e</strong></p>
        <p style='font-size:18px;margin:8px 0;font-family:Montserrat,sans-serif;'>Optimized Emissions: <strong>{optimized:.1f} tons CO₂e</strong></p>
        <p style='font-size:18px;font-family:Montserrat,sans-serif;'>Estimated Emission Reduction: <strong style='color:#111;'>{reduction:.1f}%</strong></p>
        <p style='margin-top:12px;font-size:15px;font-family:Montserrat,sans-serif;'>{msg}</p>
    </div>
    """
with st.sidebar:
    st.header("INPUTS: ACTIVITY DATA")
    cars_km = st.number_input("Cars - distance (km/year) ℹ️", 0, 1_000_000, 230000, help="Total annual km driven by fleet cars")
    ev_share = st.slider("EV Share (%) ℹ️", 0, 100, 30, help="Percent of cars that are electric vehicles")
    km_reduction = st.slider("KM Reduction (%) ℹ️", 0, 100, 10, help="Percent reduction in driving distance (e.g. by route optimization)")
    trucks_km = st.number_input("Trucks - distance (km/year) ℹ️", 0, 1_000_000, 150000, help="Total annual km driven by trucks")
    buses_km = st.number_input("Buses - distance (km/year) ℹ️", 0, 1_000_000, 80000, help="Total annual km by buses")
    forklift_hr = st.number_input("Forklifts - operating hours/year ℹ️", 0, 5000, 600, help="Total annual operating hours for forklifts")
    planes_hr = st.number_input("Cargo Planes - flight hours/year ℹ️", 0, 2000, 400, help="Total annual flight hours by cargo planes")
    load_factor = st.slider("Load Factor (%) ℹ️", 0, 100, 80, help="Average cargo load factor for planes")
    lighting_kwh = st.number_input("Office Lighting (kWh/year) ℹ️", 0, 50000, 12000, help="Annual kWh for lighting")
    heating_kwhth = st.number_input("Heating (kWh-th/year) ℹ️", 0, 50000, 10000, help="Annual thermal energy for heating")
    cooling_kwh = st.number_input("Cooling A/C (kWh/year) ℹ️", 0, 50000, 15000, help="Annual electricity for cooling")
    computing_kwh = st.number_input("Computing IT (kWh/year) ℹ️", 0, 50000, 18000, help="Annual electricity for IT/computing")

factors = {
    "Cars": 0.18,
    "Trucks": 0.90,
    "Buses": 1.10,
    "Forklifts": 4.0,
    "Cargo Planes": 9000,
    "Office Lighting": 0.42,
    "Heating": 0.20,
    "Cooling": 0.42,
    "Computing IT": 0.42
}
def calculate_emissions():
    cars_em = ((cars_km * factors["Cars"]) * (1 - 0.7 * ev_share / 100) * (1 - km_reduction / 100)) / 1000
    trucks_em = (trucks_km * factors["Trucks"]) / 1000
    buses_em = (buses_km * factors["Buses"]) / 1000
    forklifts_em = (forklift_hr * factors["Forklifts"]) / 1000
    planes_em = (planes_hr * factors["Cargo Planes"] * (load_factor / 100)) / 1000
    lighting_em = (lighting_kwh * factors["Office Lighting"]) / 1000
    heating_em = (heating_kwhth * factors["Heating"]) / 1000
    cooling_em = (cooling_kwh * factors["Cooling"]) / 1000
    computing_em = (computing_kwh * factors["Computing IT"]) / 1000

    total_baseline = sum([
        cars_em, trucks_em, buses_em, forklifts_em, planes_em,
        lighting_em, heating_em, cooling_em, computing_em
    ])
    optimized_values = {
        "Cars": cars_em * 0.75,
        "Trucks": trucks_em * 0.85,
        "Buses": buses_em * 0.9,
        "Forklifts": forklifts_em * 0.9,
        "Cargo Planes": planes_em * 0.8,
        "Office Lighting": lighting_em * 0.7,
        "Heating": heating_em * 0.8,
        "Cooling": cooling_em * 0.75,
        "Computing IT": computing_em * 0.8
    }
    total_optimized = sum(optimized_values.values())
    return {
        "baseline": {
            "Cars": cars_em, "Trucks": trucks_em, "Buses": buses_em, "Forklifts": forklifts_em,
            "Cargo Planes": planes_em, "Office Lighting": lighting_em, "Heating": heating_em,
            "Cooling": cooling_em, "Computing IT": computing_em
        },
        "optimized": optimized_values,
        "total_baseline": total_baseline,
        "total_optimized": total_optimized
    }
results = calculate_emissions()
reduction = (1 - results["total_optimized"] / results["total_baseline"]) * 100
st.markdown(executive_summary(results["total_baseline"], results["total_optimized"], reduction), unsafe_allow_html=True)

col1, col2 = st.columns([2, 1])

pie_colors = [
    "#003366",
    "#24445C",
    "#B8860B",
    "#B22222",
    "#4B0082",
    "#004953",
    "#8B008B",
    "#005F6B",
    "#333366"
]

with col1:
    df_pie = pd.DataFrame({
        "Category": list(results["optimized"].keys()),
        "Emission": list(results["optimized"].values())
    })

    biggest_idx = df_pie["Emission"].idxmax()
    pie_colors_ordered = pie_colors.copy()
    if biggest_idx != 0:
        pie_colors_ordered[biggest_idx], pie_colors_ordered[0] = pie_colors_ordered[0], pie_colors_ordered[biggest_idx]
    pie_fig = px.pie(
        df_pie,
        values="Emission",
        names="Category",
        title="Emission Share by Category (Post-Optimization)",
        color_discrete_sequence=pie_colors_ordered
    )
    pie_fig.update_traces(
        textinfo="none",
        marker=dict(line=dict(color="#fff", width=1.5)),
        pull=[0.08 if v == max(df_pie["Emission"]) else 0 for v in df_pie["Emission"]],
        hovertemplate="<b>%{label}</b><br>CO₂e: %{value:.2f} tons"
    )
    pie_fig.update_layout(
        title_font=dict(size=22, color="#111", family="Montserrat"),
        legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5, font=dict(size=12, color="#111", family="Montserrat")),
        paper_bgcolor="#fff",
        plot_bgcolor="#fff",
        font_color="#111",
        font_family="Montserrat",
        height=550
    )
    st.plotly_chart(pie_fig, use_container_width=True)

with col2:
    bar_fig = px.bar(
        x=["Baseline", "Optimized"],
        y=[results["total_baseline"], results["total_optimized"]],
        text=[f"{results['total_baseline']:.1f}", f"{results['total_optimized']:.1f}"],
        title="Total Emissions (tons CO₂e) — Baseline vs Optimized",
        color=["Baseline", "Optimized"],
        color_discrete_map={"Baseline": "#111", "Optimized": "#24445C"}
    )
    bar_fig.update_traces(
        textposition="outside",
        marker_line_color="#111",
        marker_line_width=1.2
    )
    bar_fig.update_layout(
        title_font=dict(size=20, color="#111", family="Montserrat"),
        yaxis_title="Tons of CO₂e",
        height=550,
        plot_bgcolor="#fff",
        paper_bgcolor="#fff",
        font_color="#111",
        font_family="Montserrat"
    )
    st.plotly_chart(bar_fig, use_container_width=True)

st.markdown("<h3 style='font-family:Montserrat,sans-serif;color:#111;'>📋 Emission Summary Table</h3>", unsafe_allow_html=True)
summary_df = pd.DataFrame({
    "Category": results["baseline"].keys(),
    "Baseline (tons CO₂e)": results["baseline"].values(),
    "Optimized (tons CO₂e)": results["optimized"].values()
})
st.dataframe(summary_df.style.format({
    "Baseline (tons CO₂e)": "{:.2f}",
    "Optimized (tons CO₂e)": "{:.2f}"
}).set_properties(**{
    "background-color": "#fff",
    "color": "#111",
    "font-family": "Montserrat"
}))

st.markdown(f"<h3 style='font-family:Montserrat,sans-serif;color:#111;'>Total Baseline Emissions: {results['total_baseline']:.1f} tons CO₂e</h3>", unsafe_allow_html=True)
st.markdown(f"<h3 style='font-family:Montserrat,sans-serif;color:#111;'>Total Optimized Emissions: {results['total_optimized']:.1f} tons CO₂e</h3>", unsafe_allow_html=True)
st.success(f"💡 Estimated Emission Reduction: **{reduction:.1f}%**")

tips = [
    "Increase EV share in fleet for dramatic CO₂ savings.",
    "Optimize truck/bus routes to reduce travel distance.",
    "Switch to LED lighting and smart controls.",
    "Invest in building insulation for heating/cooling efficiency.",
    "Utilize cloud-based IT for better energy management."
]
st.markdown("<hr>", unsafe_allow_html=True)
st.markdown("<h3 style='font-family:Montserrat,sans-serif;color:#111;'>🌟 Sustainability Recommendations</h3>", unsafe_allow_html=True)
for tip in tips:
    st.markdown(f"- {tip}")

st.caption("Developed by Team DPWPZ | Powered by Sustainable Tech 💚")

st.markdown("""
    <div style='color:#888;font-size:13px;text-align:center;margin-top:18px;font-family:Montserrat,sans-serif;'>
        © 2025 Carbon Sense 
    </div>
""", unsafe_allow_html=True)







