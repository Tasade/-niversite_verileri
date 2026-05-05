import subprocess, sys
subprocess.run([sys.executable, "-m", "pip", "install", "plotly", "openpyxl", "-q"], check=True)

import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path

DATA_PATH = Path(__file__).parent / "son_3_yil_program_basari_istatistigi.xlsx"

st.set_page_config(
    page_title="BAU Program Basari Analizi",
    page_icon="U+1F393",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;700;800&family=DM+Sans:wght@300;400;500&display=swap');
html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
.main { background: #0a0e1a; }
[data-testid="stAppViewContainer"] { background: linear-gradient(135deg, #0a0e1a 0%, #0f1729 50%, #0a0e1a 100%); }
[data-testid="stSidebar"] { background: #0d1220 !important; border-right: 1px solid #1e2d50; }
h1, h2, h3 { font-family: 'Syne', sans-serif !important; }
.metric-card {
    background: linear-gradient(135deg, #111827 0%, #1a2540 100%);
    border: 1px solid #1e3a5f;
    border-radius: 16px;
    padding: 20px 24px;
    text-align: center;
}
.metric-card .label { color: #64748b; font-size: 0.78rem; letter-spacing: 0.08em; text-transform: uppercase; margin-bottom: 6px; }
.metric-card .value { color: #e2e8f0; font-size: 1.8rem; font-weight: 700; font-family: 'Syne', sans-serif; }
.metric-card .delta-pos { color: #34d399; font-size: 0.85rem; }
.metric-card .delta-neg { color: #f87171; font-size: 0.85rem; }
.section-title {
    font-family: 'Syne', sans-serif;
    font-size: 1.15rem;
    font-weight: 700;
    color: #93c5fd;
    border-left: 3px solid #3b82f6;
    padding-left: 12px;
    margin: 24px 0 16px;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}
</style>
""", unsafe_allow_html=True)


@st.cache_data
def load_and_clean():
    df = pd.read_excel(DATA_PATH)
    df["OKUL ADI"] = df["OKUL ADI"].ffill()
    df.columns = df.columns.str.strip()
    df["yeni_program"] = df[["2023", "2024"]].isna().all(axis=1)
    for c in ["2023", "2024", "2025", "25/23", "25/24", "24/23"]:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    df.loc[df["yeni_program"], ["25/23", "25/24", "24/23"]] = np.nan

    def kategorize(okul):
        if "Meslek" in okul:
            return "Meslek Yuksekokulu"
        elif "Fakulte" in okul or "Fakültesi" in okul or "Fakültesi" in okul:
            return "Fakulte"
        elif "Yuksekokul" in okul or "Yüksekokulu" in okul:
            return "Yuksekokul"
        return "Diger"

    df["OKUL TURU"] = df["OKUL ADI"].apply(kategorize)

    def trend(row):
        if pd.isna(row["25/23"]):
            return "Yeni Program"
        elif row["25/23"] < -50000:
            return "Guclu Iyilesme"
        elif row["25/23"] < 0:
            return "Iyilesme"
        elif row["25/23"] < 50000:
            return "Stabil"
        else:
            return "Gerileme"

    df["TREND"] = df.apply(trend, axis=1)
    return df


df = load_and_clean()

PLOT_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(17,24,39,0.8)",
    font=dict(color="#e2e8f0", family="DM Sans"),
    xaxis=dict(gridcolor="#1e2d50", color="#64748b"),
    yaxis=dict(gridcolor="#1e2d50", color="#64748b"),
    legend=dict(font=dict(size=11, color="#94a3b8"), bgcolor="rgba(0,0,0,0)"),
    margin=dict(t=60, b=30, l=20, r=20),
)

# Sidebar
with st.sidebar:
    st.markdown("### BAU Basari Analizi")
    st.markdown("**2023 - 2025 Program Siralamalari**")
    st.markdown("---")
    okul_listesi = ["Tumu"] + sorted(df["OKUL ADI"].unique().tolist())
    secili_okul = st.selectbox("Okul / Fakulte", okul_listesi)
    tur_listesi = ["Tumu"] + sorted(df["OKUL TURU"].unique().tolist())
    secili_tur = st.selectbox("Kurum Turu", tur_listesi)
    trend_listesi = ["Tumu"] + sorted(df["TREND"].unique().tolist())
    secili_trend = st.selectbox("Trend Filtresi", trend_listesi)
    st.markdown("---")
    st.markdown("**Not:** Sira degeri dusuk = basari daha yuksek")

# Filter
filtered = df.copy()
if secili_okul != "Tumu":
    filtered = filtered[filtered["OKUL ADI"] == secili_okul]
if secili_tur != "Tumu":
    filtered = filtered[filtered["OKUL TURU"] == secili_tur]
if secili_trend != "Tumu":
    filtered = filtered[filtered["TREND"] == secili_trend]

# Header
st.markdown("""
<h1 style='font-family:Syne,sans-serif; color:#e2e8f0; font-size:2.2rem; font-weight:800; margin-bottom:4px;'>
BAU Program Basari Istatistikleri
</h1>
<p style='color:#64748b; font-size:0.95rem; margin-bottom:28px;'>
Balikesir Universitesi - 2023-2025 - YKS Basari Sirasi Analizi
</p>
""", unsafe_allow_html=True)

# KPIs
iyilesen = filtered[filtered["TREND"].isin(["Iyilesme", "Guclu Iyilesme"])]
gerileyen = filtered[filtered["TREND"] == "Gerileme"]
pct_iyilesen = len(iyilesen) / max(len(filtered[filtered["TREND"] != "Yeni Program"]), 1) * 100
ortalama_2025 = filtered["2025"].mean()
ortalama_2023 = filtered["2023"].mean()
en_iyi = filtered.loc[filtered["2025"].idxmin()] if len(filtered) > 0 else None

col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    st.markdown(f'<div class="metric-card"><div class="label">Toplam Program</div><div class="value">{len(filtered)}</div><div class="delta-pos">{filtered["OKUL ADI"].nunique()} kurum</div></div>', unsafe_allow_html=True)
with col2:
    st.markdown(f'<div class="metric-card"><div class="label">Iyilesen Program</div><div class="value" style="color:#34d399">{len(iyilesen)}</div><div class="delta-pos">%{pct_iyilesen:.0f} oran</div></div>', unsafe_allow_html=True)
with col3:
    st.markdown(f'<div class="metric-card"><div class="label">Gerileyen Program</div><div class="value" style="color:#f87171">{len(gerileyen)}</div><div class="delta-neg">siralama dustu</div></div>', unsafe_allow_html=True)
with col4:
    ort_delta = (ortalama_2023 - ortalama_2025) if not pd.isna(ortalama_2023) else 0
    delta_cls = "delta-pos" if ort_delta > 0 else "delta-neg"
    st.markdown(f'<div class="metric-card"><div class="label">Ort. 2025 Sirasi</div><div class="value">{ortalama_2025:,.0f}</div><div class="{delta_cls}">{abs(ort_delta):,.0f} (2023 farki)</div></div>', unsafe_allow_html=True)
with col5:
    en_iyi_ad = en_iyi["PROGRAM ADI"][:20] + "..." if en_iyi is not None and len(en_iyi["PROGRAM ADI"]) > 20 else (en_iyi["PROGRAM ADI"] if en_iyi is not None else "")
    st.markdown(f'<div class="metric-card"><div class="label">En Iyi Sira 2025</div><div class="value" style="color:#fbbf24">{int(filtered["2025"].min()):,}</div><div class="delta-pos">{en_iyi_ad}</div></div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Donut + Scatter
st.markdown('<div class="section-title">Trend ve Dagilim Analizi</div>', unsafe_allow_html=True)
col_a, col_b = st.columns([1, 1.4])

with col_a:
    trend_counts = filtered["TREND"].value_counts().reset_index()
    trend_counts.columns = ["Trend", "Sayi"]
    color_map = {"Guclu Iyilesme": "#059669", "Iyilesme": "#34d399", "Stabil": "#94a3b8", "Gerileme": "#f87171", "Yeni Program": "#818cf8"}
    fig = px.pie(trend_counts, names="Trend", values="Sayi", hole=0.55, color="Trend", color_discrete_map=color_map, title="Program Trend Dagilimi")
    fig.update_layout(**{k: v for k, v in PLOT_LAYOUT.items() if k not in ["xaxis","yaxis"]}, title_font=dict(color="#93c5fd", family="Syne", size=14))
    fig.update_traces(textfont_color="#0a0e1a")
    st.plotly_chart(fig, use_container_width=True)

with col_b:
    sc = filtered[filtered["TREND"] != "Yeni Program"].dropna(subset=["2023", "2025"])
    fig2 = px.scatter(sc, x="2023", y="2025", color="OKUL TURU",
                      hover_data=["PROGRAM ADI", "OKUL ADI", "25/23"],
                      title="2023 vs 2025 Basari Sirasi",
                      labels={"2023": "Siralama 2023", "2025": "Siralama 2025"},
                      color_discrete_sequence=["#3b82f6", "#f59e0b", "#10b981", "#e879f9"])
    max_val = max(sc["2023"].max(), sc["2025"].max()) if len(sc) > 0 else 2000000
    fig2.add_shape(type="line", x0=0, y0=0, x1=max_val, y1=max_val, line=dict(color="#334155", dash="dot", width=1.5))
    fig2.update_layout(**PLOT_LAYOUT, title_font=dict(color="#93c5fd", family="Syne", size=13))
    st.plotly_chart(fig2, use_container_width=True)

# Bar chart - okul bazli
st.markdown('<div class="section-title">Okul Bazli Performans</div>', unsafe_allow_html=True)
okul_grp = df.groupby("OKUL ADI").agg(Ort_2023=("2023","mean"), Ort_2024=("2024","mean"), Ort_2025=("2025","mean")).reset_index().dropna().sort_values("Ort_2025")
fig3 = go.Figure()
fig3.add_trace(go.Bar(name="2023", x=okul_grp["OKUL ADI"], y=okul_grp["Ort_2023"], marker_color="#1e3a5f"))
fig3.add_trace(go.Bar(name="2024", x=okul_grp["OKUL ADI"], y=okul_grp["Ort_2024"], marker_color="#2563eb"))
fig3.add_trace(go.Bar(name="2025", x=okul_grp["OKUL ADI"], y=okul_grp["Ort_2025"], marker_color="#3b82f6"))
_l3 = {k: v for k, v in PLOT_LAYOUT.items() if k not in ["xaxis","yaxis","margin"]}
fig3.update_layout(**_l3, barmode="group", height=420,
                   title=dict(text="Okul Bazli Ortalama Basari Sirasi (2023-2025)", font=dict(color="#93c5fd", family="Syne", size=14)),
                   xaxis=dict(tickangle=-40, gridcolor="#1e2d50", color="#64748b", tickfont=dict(size=10)),
                   yaxis=dict(gridcolor="#1e2d50", color="#64748b", title="Ort. Siralama"),
                   margin=dict(t=60, b=120, l=20, r=20))
st.plotly_chart(fig3, use_container_width=True)

# Top iyilesen / gerileyen
st.markdown('<div class="section-title">En Fazla Iyilesen ve Gerileyen Programlar</div>', unsafe_allow_html=True)
valid_df = filtered[filtered["TREND"] != "Yeni Program"].dropna(subset=["25/23"])
col_c, col_d = st.columns(2)

with col_c:
    top_i = valid_df.nsmallest(10, "25/23")[["PROGRAM ADI","OKUL ADI","25/23","2025"]]
    fig4 = px.bar(top_i, x="25/23", y="PROGRAM ADI", orientation="h",
                  color="25/23", color_continuous_scale=["#059669","#34d399","#a7f3d0"],
                  title="En Fazla Iyilesen 10 Program", hover_data=["OKUL ADI","2025"])
    _l4 = {k: v for k, v in PLOT_LAYOUT.items() if k not in ["yaxis"]}
    fig4.update_layout(**_l4, title_font=dict(color="#34d399", family="Syne", size=13),
                       yaxis=dict(color="#94a3b8", tickfont=dict(size=10)), coloraxis_showscale=False, height=380)
    st.plotly_chart(fig4, use_container_width=True)

with col_d:
    top_g = valid_df.nlargest(10, "25/23")[["PROGRAM ADI","OKUL ADI","25/23","2025"]]
    fig5 = px.bar(top_g, x="25/23", y="PROGRAM ADI", orientation="h",
                  color="25/23", color_continuous_scale=["#dc2626","#f87171","#fca5a5"],
                  title="En Fazla Gerileyen 10 Program", hover_data=["OKUL ADI","2025"])
    _l5 = {k: v for k, v in PLOT_LAYOUT.items() if k not in ["yaxis"]}
    fig5.update_layout(**_l5, title_font=dict(color="#f87171", family="Syne", size=13),
                       yaxis=dict(color="#94a3b8", tickfont=dict(size=10)), coloraxis_showscale=False, height=380)
    st.plotly_chart(fig5, use_container_width=True)

# Line chart
st.markdown('<div class="section-title">3 Yillik Siralama Trendi</div>', unsafe_allow_html=True)
line_data = df.groupby("OKUL ADI").agg(y2023=("2023","mean"), y2024=("2024","mean"), y2025=("2025","mean")).reset_index().dropna()
fig6 = go.Figure()
colors = px.colors.qualitative.Set3
for i, (_, row) in enumerate(line_data.iterrows()):
    fig6.add_trace(go.Scatter(
        x=[2023, 2024, 2025], y=[row["y2023"], row["y2024"], row["y2025"]],
        mode="lines+markers", name=row["OKUL ADI"],
        line=dict(color=colors[i % len(colors)], width=1.5), marker=dict(size=5),
        hovertemplate=f"<b>{row['OKUL ADI']}</b><br>Yil: %{{x}}<br>Ort. Sira: %{{y:,.0f}}<extra></extra>"
    ))
_l6 = {k: v for k, v in PLOT_LAYOUT.items() if k not in ["xaxis","yaxis","legend","margin"]}
fig6.update_layout(**_l6,
    title=dict(text="Her Okul Icin Ortalama Basari Sirasinin Yillara Gore Degisimi", font=dict(color="#93c5fd", family="Syne", size=14)),
    xaxis=dict(tickvals=[2023,2024,2025], gridcolor="#1e2d50", color="#64748b"),
    yaxis=dict(gridcolor="#1e2d50", color="#64748b", title="Ort. Basari Sirasi", autorange="reversed"),
    legend=dict(font=dict(size=9, color="#94a3b8"), bgcolor="rgba(0,0,0,0)", orientation="v", x=1.01, y=0.5),
    height=500, margin=dict(t=60, b=30, l=20, r=220))
st.plotly_chart(fig6, use_container_width=True)

# Data table
st.markdown('<div class="section-title">Ham Veri Tablosu</div>', unsafe_allow_html=True)
display_df = filtered[["OKUL ADI","PROGRAM ADI","2023","2024","2025","25/23","25/24","TREND","OKUL TURU"]].copy()
display_df["2023"] = display_df["2023"].apply(lambda x: f"{x:,.0f}" if pd.notna(x) else "Yeni")
display_df["2024"] = display_df["2024"].apply(lambda x: f"{x:,.0f}" if pd.notna(x) else "Yeni")
display_df["2025"] = display_df["2025"].apply(lambda x: f"{x:,.0f}" if pd.notna(x) else "-")
display_df["25/23"] = display_df["25/23"].apply(lambda x: f"{x:+,.0f}" if pd.notna(x) else "-")
display_df["25/24"] = display_df["25/24"].apply(lambda x: f"{x:+,.0f}" if pd.notna(x) else "-")
st.dataframe(display_df.rename(columns={"OKUL ADI":"Okul","PROGRAM ADI":"Program","25/23":"D 23-25","25/24":"D 24-25","OKUL TURU":"Tur"}),
             use_container_width=True, hide_index=True, height=420)

st.markdown("<p style='color:#334155; font-size:0.8rem; text-align:center; margin-top:24px;'>Balikesir Universitesi - YKS Program Basari Sirasi - Veri Kaynagi: OSYM</p>", unsafe_allow_html=True).metric-card .delta-pos { color: #34d399; font-size: 0.85rem; }
.metric-card .delta-neg { color: #f87171; font-size: 0.85rem; }
.section-title {
    font-family: 'Syne', sans-serif;
    font-size: 1.15rem;
    font-weight: 700;
    color: #93c5fd;
    border-left: 3px solid #3b82f6;
    padding-left: 12px;
    margin: 24px 0 16px;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}
</style>
""", unsafe_allow_html=True)


@st.cache_data
def load_and_clean():
    df = pd.read_excel(DATA_PATH)
    df["OKUL ADI"] = df["OKUL ADI"].ffill()
    df.columns = df.columns.str.strip()
    df["yeni_program"] = df[["2023", "2024"]].isna().all(axis=1)
    for c in ["2023", "2024", "2025", "25/23", "25/24", "24/23"]:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    df.loc[df["yeni_program"], ["25/23", "25/24", "24/23"]] = np.nan

    def kategorize(okul):
        if "Meslek" in okul:
            return "Meslek Yuksekokulu"
        elif "Fakulte" in okul or "Fakültesi" in okul or "Fakültesi" in okul:
            return "Fakulte"
        elif "Yuksekokul" in okul or "Yüksekokulu" in okul:
            return "Yuksekokul"
        return "Diger"

    df["OKUL TURU"] = df["OKUL ADI"].apply(kategorize)

    def trend(row):
        if pd.isna(row["25/23"]):
            return "Yeni Program"
        elif row["25/23"] < -50000:
            return "Guclu Iyilesme"
        elif row["25/23"] < 0:
            return "Iyilesme"
        elif row["25/23"] < 50000:
            return "Stabil"
        else:
            return "Gerileme"

    df["TREND"] = df.apply(trend, axis=1)
    return df


df = load_and_clean()

PLOT_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(17,24,39,0.8)",
    font=dict(color="#e2e8f0", family="DM Sans"),
    xaxis=dict(gridcolor="#1e2d50", color="#64748b"),
    yaxis=dict(gridcolor="#1e2d50", color="#64748b"),
    legend=dict(font=dict(size=11, color="#94a3b8"), bgcolor="rgba(0,0,0,0)"),
    margin=dict(t=60, b=30, l=20, r=20),
)

# Sidebar
with st.sidebar:
    st.markdown("### BAU Basari Analizi")
    st.markdown("**2023 - 2025 Program Siralamalari**")
    st.markdown("---")
    okul_listesi = ["Tumu"] + sorted(df["OKUL ADI"].unique().tolist())
    secili_okul = st.selectbox("Okul / Fakulte", okul_listesi)
    tur_listesi = ["Tumu"] + sorted(df["OKUL TURU"].unique().tolist())
    secili_tur = st.selectbox("Kurum Turu", tur_listesi)
    trend_listesi = ["Tumu"] + sorted(df["TREND"].unique().tolist())
    secili_trend = st.selectbox("Trend Filtresi", trend_listesi)
    st.markdown("---")
    st.markdown("**Not:** Sira degeri dusuk = basari daha yuksek")

# Filter
filtered = df.copy()
if secili_okul != "Tumu":
    filtered = filtered[filtered["OKUL ADI"] == secili_okul]
if secili_tur != "Tumu":
    filtered = filtered[filtered["OKUL TURU"] == secili_tur]
if secili_trend != "Tumu":
    filtered = filtered[filtered["TREND"] == secili_trend]

# Header
st.markdown("""
<h1 style='font-family:Syne,sans-serif; color:#e2e8f0; font-size:2.2rem; font-weight:800; margin-bottom:4px;'>
BAU Program Basari Istatistikleri
</h1>
<p style='color:#64748b; font-size:0.95rem; margin-bottom:28px;'>
Balikesir Universitesi - 2023-2025 - YKS Basari Sirasi Analizi
</p>
""", unsafe_allow_html=True)

# KPIs
iyilesen = filtered[filtered["TREND"].isin(["Iyilesme", "Guclu Iyilesme"])]
gerileyen = filtered[filtered["TREND"] == "Gerileme"]
pct_iyilesen = len(iyilesen) / max(len(filtered[filtered["TREND"] != "Yeni Program"]), 1) * 100
ortalama_2025 = filtered["2025"].mean()
ortalama_2023 = filtered["2023"].mean()
en_iyi = filtered.loc[filtered["2025"].idxmin()] if len(filtered) > 0 else None

col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    st.markdown(f'<div class="metric-card"><div class="label">Toplam Program</div><div class="value">{len(filtered)}</div><div class="delta-pos">{filtered["OKUL ADI"].nunique()} kurum</div></div>', unsafe_allow_html=True)
with col2:
    st.markdown(f'<div class="metric-card"><div class="label">Iyilesen Program</div><div class="value" style="color:#34d399">{len(iyilesen)}</div><div class="delta-pos">%{pct_iyilesen:.0f} oran</div></div>', unsafe_allow_html=True)
with col3:
    st.markdown(f'<div class="metric-card"><div class="label">Gerileyen Program</div><div class="value" style="color:#f87171">{len(gerileyen)}</div><div class="delta-neg">siralama dustu</div></div>', unsafe_allow_html=True)
with col4:
    ort_delta = (ortalama_2023 - ortalama_2025) if not pd.isna(ortalama_2023) else 0
    delta_cls = "delta-pos" if ort_delta > 0 else "delta-neg"
    st.markdown(f'<div class="metric-card"><div class="label">Ort. 2025 Sirasi</div><div class="value">{ortalama_2025:,.0f}</div><div class="{delta_cls}">{abs(ort_delta):,.0f} (2023 farki)</div></div>', unsafe_allow_html=True)
with col5:
    en_iyi_ad = en_iyi["PROGRAM ADI"][:20] + "..." if en_iyi is not None and len(en_iyi["PROGRAM ADI"]) > 20 else (en_iyi["PROGRAM ADI"] if en_iyi is not None else "")
    st.markdown(f'<div class="metric-card"><div class="label">En Iyi Sira 2025</div><div class="value" style="color:#fbbf24">{int(filtered["2025"].min()):,}</div><div class="delta-pos">{en_iyi_ad}</div></div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Donut + Scatter
st.markdown('<div class="section-title">Trend ve Dagilim Analizi</div>', unsafe_allow_html=True)
col_a, col_b = st.columns([1, 1.4])

with col_a:
    trend_counts = filtered["TREND"].value_counts().reset_index()
    trend_counts.columns = ["Trend", "Sayi"]
    color_map = {"Guclu Iyilesme": "#059669", "Iyilesme": "#34d399", "Stabil": "#94a3b8", "Gerileme": "#f87171", "Yeni Program": "#818cf8"}
    fig = px.pie(trend_counts, names="Trend", values="Sayi", hole=0.55, color="Trend", color_discrete_map=color_map, title="Program Trend Dagilimi")
    fig.update_layout(**{k: v for k, v in PLOT_LAYOUT.items() if k not in ["xaxis","yaxis"]}, title_font=dict(color="#93c5fd", family="Syne", size=14))
    fig.update_traces(textfont_color="#0a0e1a")
    st.plotly_chart(fig, use_container_width=True)

with col_b:
    sc = filtered[filtered["TREND"] != "Yeni Program"].dropna(subset=["2023", "2025"])
    fig2 = px.scatter(sc, x="2023", y="2025", color="OKUL TURU",
                      hover_data=["PROGRAM ADI", "OKUL ADI", "25/23"],
                      title="2023 vs 2025 Basari Sirasi",
                      labels={"2023": "Siralama 2023", "2025": "Siralama 2025"},
                      color_discrete_sequence=["#3b82f6", "#f59e0b", "#10b981", "#e879f9"])
    max_val = max(sc["2023"].max(), sc["2025"].max()) if len(sc) > 0 else 2000000
    fig2.add_shape(type="line", x0=0, y0=0, x1=max_val, y1=max_val, line=dict(color="#334155", dash="dot", width=1.5))
    fig2.update_layout(**PLOT_LAYOUT, title_font=dict(color="#93c5fd", family="Syne", size=13))
    st.plotly_chart(fig2, use_container_width=True)

# Bar chart - okul bazli
st.markdown('<div class="section-title">Okul Bazli Performans</div>', unsafe_allow_html=True)
okul_grp = df.groupby("OKUL ADI").agg(Ort_2023=("2023","mean"), Ort_2024=("2024","mean"), Ort_2025=("2025","mean")).reset_index().dropna().sort_values("Ort_2025")
fig3 = go.Figure()
fig3.add_trace(go.Bar(name="2023", x=okul_grp["OKUL ADI"], y=okul_grp["Ort_2023"], marker_color="#1e3a5f"))
fig3.add_trace(go.Bar(name="2024", x=okul_grp["OKUL ADI"], y=okul_grp["Ort_2024"], marker_color="#2563eb"))
fig3.add_trace(go.Bar(name="2025", x=okul_grp["OKUL ADI"], y=okul_grp["Ort_2025"], marker_color="#3b82f6"))
fig3.update_layout(**PLOT_LAYOUT, barmode="group", height=420,
                   title=dict(text="Okul Bazli Ortalama Basari Sirasi (2023-2025)", font=dict(color="#93c5fd", family="Syne", size=14)),
                   xaxis=dict(tickangle=-40, gridcolor="#1e2d50", color="#64748b", tickfont=dict(size=10)),
                   yaxis=dict(gridcolor="#1e2d50", color="#64748b", title="Ort. Siralama"),
                   margin=dict(t=60, b=120, l=20, r=20))
st.plotly_chart(fig3, use_container_width=True)

# Top iyilesen / gerileyen
st.markdown('<div class="section-title">En Fazla Iyilesen ve Gerileyen Programlar</div>', unsafe_allow_html=True)
valid_df = filtered[filtered["TREND"] != "Yeni Program"].dropna(subset=["25/23"])
col_c, col_d = st.columns(2)

with col_c:
    top_i = valid_df.nsmallest(10, "25/23")[["PROGRAM ADI","OKUL ADI","25/23","2025"]]
    fig4 = px.bar(top_i, x="25/23", y="PROGRAM ADI", orientation="h",
                  color="25/23", color_continuous_scale=["#059669","#34d399","#a7f3d0"],
                  title="En Fazla Iyilesen 10 Program", hover_data=["OKUL ADI","2025"])
    fig4.update_layout(**PLOT_LAYOUT, title_font=dict(color="#34d399", family="Syne", size=13),
                       yaxis=dict(color="#94a3b8", tickfont=dict(size=10)), coloraxis_showscale=False, height=380)
    st.plotly_chart(fig4, use_container_width=True)

with col_d:
    top_g = valid_df.nlargest(10, "25/23")[["PROGRAM ADI","OKUL ADI","25/23","2025"]]
    fig5 = px.bar(top_g, x="25/23", y="PROGRAM ADI", orientation="h",
                  color="25/23", color_continuous_scale=["#dc2626","#f87171","#fca5a5"],
                  title="En Fazla Gerileyen 10 Program", hover_data=["OKUL ADI","2025"])
    fig5.update_layout(**PLOT_LAYOUT, title_font=dict(color="#f87171", family="Syne", size=13),
                       yaxis=dict(color="#94a3b8", tickfont=dict(size=10)), coloraxis_showscale=False, height=380)
    st.plotly_chart(fig5, use_container_width=True)

# Line chart
st.markdown('<div class="section-title">3 Yillik Siralama Trendi</div>', unsafe_allow_html=True)
line_data = df.groupby("OKUL ADI").agg(y2023=("2023","mean"), y2024=("2024","mean"), y2025=("2025","mean")).reset_index().dropna()
fig6 = go.Figure()
colors = px.colors.qualitative.Set3
for i, (_, row) in enumerate(line_data.iterrows()):
    fig6.add_trace(go.Scatter(
        x=[2023, 2024, 2025], y=[row["y2023"], row["y2024"], row["y2025"]],
        mode="lines+markers", name=row["OKUL ADI"],
        line=dict(color=colors[i % len(colors)], width=1.5), marker=dict(size=5),
        hovertemplate=f"<b>{row['OKUL ADI']}</b><br>Yil: %{{x}}<br>Ort. Sira: %{{y:,.0f}}<extra></extra>"
    ))
fig6.update_layout(**PLOT_LAYOUT,
    title=dict(text="Her Okul Icin Ortalama Basari Sirasinin Yillara Gore Degisimi", font=dict(color="#93c5fd", family="Syne", size=14)),
    xaxis=dict(tickvals=[2023,2024,2025], gridcolor="#1e2d50", color="#64748b"),
    yaxis=dict(gridcolor="#1e2d50", color="#64748b", title="Ort. Basari Sirasi", autorange="reversed"),
    legend=dict(font=dict(size=9, color="#94a3b8"), bgcolor="rgba(0,0,0,0)", orientation="v", x=1.01, y=0.5),
    height=500, margin=dict(t=60, b=30, l=20, r=220))
st.plotly_chart(fig6, use_container_width=True)

# Data table
st.markdown('<div class="section-title">Ham Veri Tablosu</div>', unsafe_allow_html=True)
display_df = filtered[["OKUL ADI","PROGRAM ADI","2023","2024","2025","25/23","25/24","TREND","OKUL TURU"]].copy()
display_df["2023"] = display_df["2023"].apply(lambda x: f"{x:,.0f}" if pd.notna(x) else "Yeni")
display_df["2024"] = display_df["2024"].apply(lambda x: f"{x:,.0f}" if pd.notna(x) else "Yeni")
display_df["2025"] = display_df["2025"].apply(lambda x: f"{x:,.0f}" if pd.notna(x) else "-")
display_df["25/23"] = display_df["25/23"].apply(lambda x: f"{x:+,.0f}" if pd.notna(x) else "-")
display_df["25/24"] = display_df["25/24"].apply(lambda x: f"{x:+,.0f}" if pd.notna(x) else "-")
st.dataframe(display_df.rename(columns={"OKUL ADI":"Okul","PROGRAM ADI":"Program","25/23":"D 23-25","25/24":"D 24-25","OKUL TURU":"Tur"}),
             use_container_width=True, hide_index=True, height=420)

st.markdown("<p style='color:#334155; font-size:0.8rem; text-align:center; margin-top:24px;'>Balikesir Universitesi - YKS Program Basari Sirasi - Veri Kaynagi: OSYM</p>", unsafe_allow_html=True)
