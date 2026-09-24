import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import time

# Cấu hình trang
st.set_page_config(
    page_title="Global Air Humidity",
    page_icon="💧",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS Custom
st.markdown("""
<style>
.main {
    background: #f5f7fb;
}
.block-container {
    padding-top: 1.5rem;
    max-width: 1500px;
}
.dashboard-title {
    font-size: 38px;
    font-weight: 800;
    color: #172033;
}
.dashboard-subtitle {
    color: #687386;
    font-size: 16px;
    margin-bottom: 20px;
}
.status {
    background: #e8f8f1;
    color: #16834b;
    padding: 8px 16px;
    border-radius: 20px;
    font-weight: 600;
}
.kpi {
    background: white;
    padding: 22px;
    border-radius: 16px;
    border: 1px solid #e8ebf1;
    box-shadow: 0 3px 12px rgba(0,0,0,0.04);
    min-height: 145px;
}
.kpi-title {
    color: #788398;
    font-size: 14px;
    font-weight: 600;
}
.kpi-value {
    color: #172033;
    font-size: 32px;
    font-weight: 800;
    margin-top: 8px;
}
.kpi-sub {
    color: #8490a3;
    font-size: 13px;
    margin-top: 5px;
}
.section-title {
    font-size: 22px;
    font-weight: 750;
    color: #172033;
    margin-top: 25px;
    margin-bottom: 12px;
}
[data-testid="stSidebar"] {
    background: #111827;
}
[data-testid="stSidebar"] * {
    color: white;
}
</style>
""", unsafe_allow_html=True)

# Danh sách thành phố
cities = {
    "Hà Nội": (21.0285, 105.8542),
    "TP. Hồ Chí Minh": (10.8231, 106.6297),
    "Đà Nẵng": (16.0544, 108.2022),
    "Tokyo": (35.6762, 139.6503),
    "Seoul": (37.5665, 126.9780),
    "Singapore": (1.3521, 103.8198),
    "Bangkok": (13.7563, 100.5018),
    "London": (51.5074, -0.1278),
    "Paris": (48.8566, 2.3522),
    "New York": (40.7128, -74.0060),
    "Los Angeles": (34.0522, -118.2437),
    "Sydney": (-33.8688, 151.2093),
    "Dubai": (25.2048, 55.2708),
    "Moscow": (55.7558, 37.6173),
    "Cairo": (30.0444, 31.2357),
    "São Paulo": (-23.5505, -46.6333),
    "Mexico City": (19.4326, -99.1332),
    "Toronto": (43.6532, -79.3832),
    "Madrid": (40.4168, -3.7038),
    "Berlin": (52.5200, 13.4050)
}

# Hàm lấy dữ liệu (được cache 60s)
@st.cache_data(ttl=60)
def get_weather():
    rows = []
    for city, (lat, lon) in cities.items():
        try:
            url = (
                "https://api.open-meteo.com/v1/forecast"
                f"?latitude={lat}"
                f"&longitude={lon}"
                "&current=temperature_2m,"
                "relative_humidity_2m,"
                "wind_speed_10m"
                "&timezone=auto"
            )
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                current = data["current"]
                rows.append({
                    "City": city,
                    "Latitude": lat,
                    "Longitude": lon,
                    "Humidity": current["relative_humidity_2m"],
                    "Temperature": current["temperature_2m"],
                    "Wind": current["wind_speed_10m"],
                    "Time": current["time"]
                })
        except Exception:
            continue
    return pd.DataFrame(rows)

df = get_weather()

if df.empty:
    st.error("Không thể kết nối dữ liệu thời tiết. Vui lòng kiểm tra kết nối mạng.")
    st.stop()

# ================= SIDEBAR =================
st.sidebar.markdown("<h1 style='font-size:26px;'>💧 Air Monitor</h1>", unsafe_allow_html=True)
st.sidebar.markdown("<p style='color:#9ca3af;'>Real-Time Global Humidity</p>", unsafe_allow_html=True)
st.sidebar.divider()

st.sidebar.markdown("### ⚙️ Dashboard Settings")
selected_city = st.sidebar.selectbox(
    "📍 Thành phố",
    ["Tất cả"] + list(cities.keys())
)

# Tùy chọn Auto Refresh
auto_refresh = st.sidebar.checkbox("Bật tự động làm mới", value=False)
if auto_refresh:
    refresh_rate = st.sidebar.selectbox("🔄 Refresh Rate (giây)", [30, 60, 120], index=1)
else:
    refresh_rate = None

st.sidebar.divider()
st.sidebar.markdown("### 📡 Data Source")
st.sidebar.success("LIVE API CONNECTED")
st.sidebar.markdown("""
**Provider:** Open-Meteo  
**Indicator:** Relative Humidity  
**Unit:** %  
**Mode:** Real-Time
""")

if st.sidebar.button("🔄 Làm mới dữ liệu ngay"):
    st.cache_data.clear()
    st.rerun()

# ================= MAIN DASHBOARD =================
st.markdown('<div class="dashboard-title">💧 Global Air Humidity Intelligence</div>', unsafe_allow_html=True)
st.markdown('<div class="dashboard-subtitle">Real-Time Atmospheric Humidity Monitoring System</div>', unsafe_allow_html=True)

last_update = datetime.now().strftime("%d/%m/%Y • %H:%M:%S")
st.markdown(f'<span class="status">● LIVE &nbsp; Last update: {last_update}</span>', unsafe_allow_html=True)
st.write("")

# Lọc dữ liệu
if selected_city != "Tất cả":
    selected_df = df[df["City"] == selected_city]
else:
    selected_df = df

# Tính toán KPI
avg_humidity = selected_df["Humidity"].mean()
max_humidity = selected_df["Humidity"].max()
min_humidity = selected_df["Humidity"].min()
humid_city = selected_df.loc[selected_df["Humidity"].idxmax(), "City"]
dry_city = selected_df.loc[selected_df["Humidity"].idxmin(), "City"]
avg_temp = selected_df["Temperature"].mean()

# Hiển thị KPI
c1, c2, c3, c4, c5 = st.columns(5)

with c1:
    st.markdown(f"""
        <div class="kpi">
            <div class="kpi-title">💧 AVERAGE HUMIDITY</div>
            <div class="kpi-value">{avg_humidity:.0f}%</div>
            <div class="kpi-sub">Global average</div>
        </div>
    """, unsafe_allow_html=True)

with c2:
    st.markdown(f"""
        <div class="kpi">
            <div class="kpi-title">💦 HIGHEST HUMIDITY</div>
            <div class="kpi-value">{max_humidity:.0f}%</div>
            <div class="kpi-sub">{humid_city}</div>
        </div>
    """, unsafe_allow_html=True)

with c3:
    st.markdown(f"""
        <div class="kpi">
            <div class="kpi-title">🏜️ LOWEST HUMIDITY</div>
            <div class="kpi-value">{min_humidity:.0f}%</div>
            <div class="kpi-sub">{dry_city}</div>
        </div>
    """, unsafe_allow_html=True)

with c4:
    st.markdown(f"""
        <div class="kpi">
            <div class="kpi-title">🌡️ AVG TEMPERATURE</div>
            <div class="kpi-value">{avg_temp:.1f}°C</div>
            <div class="kpi-sub">Current average</div>
        </div>
    """, unsafe_allow_html=True)

with c5:
    st.markdown(f"""
        <div class="kpi">
            <div class="kpi-title">🌎 LOCATIONS</div>
            <div class="kpi-value">{len(selected_df)}</div>
            <div class="kpi-sub">Cities monitored</div>
        </div>
    """, unsafe_allow_html=True)

# ================= BẢN ĐỒ & BIỂU ĐỒ =================
st.markdown('<div class="section-title">🌐 Global Humidity Map</div>', unsafe_allow_html=True)

map_fig = px.scatter_geo(
    df,
    lat="Latitude",
    lon="Longitude",
    color="Humidity",
    size="Humidity",
    hover_name="City",
    hover_data={"Humidity": ":.0f", "Temperature": ":.1f", "Wind": ":.1f", "Latitude": False, "Longitude": False},
    projection="natural earth",
    color_continuous_scale="Blues",
    size_max=30
)

map_fig.update_layout(
    height=550,
    margin=dict(l=0, r=0, t=0, b=0),
    geo=dict(showland=True, showcountries=True, showocean=True, showcoastlines=True)
)
st.plotly_chart(map_fig, use_container_width=True)

left, right = st.columns(2)

with left:
    st.markdown('<div class="section-title">💧 Humidity by City</div>', unsafe_allow_html=True)
    humidity_fig = px.bar(
        df.sort_values("Humidity"),
        x="Humidity",
        y="City",
        orientation="h",
        color="Humidity",
        color_continuous_scale="Blues",
        text="Humidity"
    )
    humidity_fig.update_traces(texttemplate="%{text:.0f}%", textposition="outside")
    humidity_fig.update_layout(height=600, margin=dict(l=0, r=30, t=10, b=0), coloraxis_showscale=False, xaxis_title="Relative Humidity (%)", yaxis_title="")
    st.plotly_chart(humidity_fig, use_container_width=True)

with right:
    st.markdown('<div class="section-title">🌡️ Temperature vs Humidity</div>', unsafe_allow_html=True)
    scatter_fig = px.scatter(
        df,
        x="Temperature",
        y="Humidity",
        size="Wind",
        color="Humidity",
        hover_name="City",
        text="City",
        color_continuous_scale="Blues"
    )
    scatter_fig.update_traces(textposition="top center")
    scatter_fig.update_layout(height=600, xaxis_title="Temperature (°C)", yaxis_title="Relative Humidity (%)")
    st.plotly_chart(scatter_fig, use_container_width=True)

# ================= BẢNG DỮ LIỆU =================
st.markdown('<div class="section-title">📊 Real-Time Humidity Data</div>', unsafe_allow_html=True)
table_df = df[["City", "Humidity", "Temperature", "Wind", "Time"]].copy()
table_df.columns = ["City", "Humidity (%)", "Temperature (°C)", "Wind Speed (km/h)", "Local Time"]

st.dataframe(
    table_df.style.format({
        "Humidity (%)": "{:.0f}",
        "Temperature (°C)": "{:.1f}",
        "Wind Speed (km/h)": "{:.1f}"
    }),
    use_container_width=True,
    height=500,
    hide_index=True
)

st.divider()

# Footer status
a, b, c = st.columns(3)
with a:
    st.metric("📡 Data Status", "LIVE")
with b:
    st.metric("🌍 Cities", len(df))
with c:
    st.metric("🔄 Refresh Mode", f"{refresh_rate}s" if auto_refresh else "Manual")

# Logic Auto-refresh (Khuyên dùng nút manual để không chặn UI)
if auto_refresh and refresh_rate:
    time.sleep(refresh_rate)
    st.cache_data.clear()
    st.rerun()
