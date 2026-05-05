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

css = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;700;800&family=DM+Sans:wght@300;400;500&display=swap');
html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
[data-testid="stAppViewContainer"] { background: linear-gradient(135deg, #0a0e1a 0%, #0f1729 50%, #0a0e1a 100%); }
[data-testid="stSidebar"] { background: #0d1220 !important; border-right: 1px solid #1e2d50; }
h1, h2, h3 { font-family: 'Syne', sans-serif !important; }
.mcard { background: linear-gradient(135deg, #111827, #1a2540); border: 1px solid #1e3a5f; border-radius: 16px; padding: 20px 24px; text-align: center; }
.mcard .lbl { color: #64748b; font-size: 0.78rem; letter-spacing: 0.08em; text-transform: uppercase; margin-bottom: 6px; }
.mcard .val { color: #e2e8f0; font-size: 1.8rem; font-weight: 700; }
.mcard .pos { color: #34d399; font-size: 0.85rem; }
.mcard .neg { color: #f87171; font-size: 0.85rem; }
.sec { font-family: 'Syne', sans-serif; font-size: 1.1rem; font-weight: 700; color: #93c5fd; border-left: 3px solid #3b82f6; padding-left: 12px; margin: 24px 0 16px; text-transform: uppercase; }
</style>
"""
st.markdown(css, unsafe_allow_html=True)


@st.cache_data
def load_and_clean():
    df = pd.read_excel(DATA_PATH)
    df["OKUL ADI"] = df["OKUL ADI"].ffill()
    df.columns = df.columns.str.strip()
    df["yeni"] = df[["2023", "2024"]].isna().all(axis=1)
    for c in ["2023", "2024", "2025", "25/23", "25/24", "24/23"]:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    df.loc[df["yeni"], ["25/23", "25/24", "24/23"]] = np.nan

    def tur(o):
        if "Meslek" in o:
            return "MYO"
        elif "Fakulte" in o or "Fakültesi" in o:
            return "Fakulte"
        return "Yuksekokul"

    def trend(row):
        if pd.isna(row["25/23"]):
            return "Yeni"
        elif row["25/23"] < -50000:
            return "Guclu Iyilesme"
        elif row["25/23"] < 0:
            return "Iyilesme"
        elif row["25/23"] < 50000:
            return "Stabil"
        return "Gerileme"

    df["TUR"] = df["OKUL ADI"].apply(tur)
    df["TREND"] = df.apply(trend, axis=1)
    return df


df = load_and_clean()

BASE = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(17,24,39,0.8)",
    font=dict(color="#e2e8f0", family="DM Sans"),
    margin=dict(t=60, b=30, l=20, r=20),
)

def layout(**kwargs):
    d = dict(BASE)
    d.update(kwargs)
    return d


with st.sidebar:
    st.markdown("### BAU Basari Analizi")
    st.markdown("2023 - 2025 YKS Siralamasi")
    st.markdown("---")
    okul_sec = st.selectbox("Okul", ["Tumu"] + sorted(df["OKUL ADI"].unique().tolist()))
    tur_sec = st.selectbox("Tur", ["Tumu"] + sorted(df["TUR"].unique().tolist()))
    trend_sec = st.selectbox("Trend", ["Tumu"] + sorted(df["TREND"].unique().tolist()))
    st.markdown("---")
    st.caption("Dusuk sira = daha basarili")

filt = df.copy()
if okul_sec != "Tumu":
    filt = filt[filt["OKUL ADI"] == okul_sec]
if tur_sec != "Tumu":
    filt = filt[filt["TUR"] == tur_sec]
if trend_sec != "Tumu":
    filt = filt[filt["TREND"] == trend_sec]

st.markdown("<h1 style='color:#e2e8f0; font-family:Syne,sans-serif;'>BAU Program Basari Istatistikleri</h1>", unsafe_allow_html=True)
st.markdown("<p style='color:#64748b;'>Balikesir Universitesi - 2023-2025 - YKS Basari Sirasi Analizi</p>", unsafe_allow_html=True)

iyilesen = filt[filt["TREND"].isin(["Iyilesme", "Guclu Iyilesme"])]
gerileyen = filt[filt["TREND"] == "Gerileme"]
pct = len(iyilesen) / max(len(filt[filt["TREND"] != "Yeni"]), 1) * 100
ort25 = filt["2025"].mean()
ort23 = filt["2023"].mean()
delta = (ort23 - ort25) if not pd.isna(ort23) else 0
en_iyi = filt.loc[filt["2025"].idxmin()] if len(filt) > 0 else None
en_iyi_ad = (en_iyi["PROGRAM ADI"][:20] + "...") if en_iyi is not None and len(str(en_iyi["PROGRAM ADI"])) > 20 else (en_iyi["PROGRAM ADI"] if en_iyi is not None else "")

c1, c2, c3, c4, c5 = st.columns(5)
c1.markdown(f'<div class="mcard"><div class="lbl">Toplam Program</div><div class="val">{len(filt)}</div><div class="pos">{filt["OKUL ADI"].nunique()} kurum</div></div>', unsafe_allow_html=True)
c2.markdown(f'<div class="mcard"><div class="lbl">Iyilesen</div><div class="val" style="color:#34d399">{len(iyilesen)}</div><div class="pos">%{pct:.0f}</div></div>', unsafe_allow_html=True)
c3.markdown(f'<div class="mcard"><div class="lbl">Gerileyen</div><div class="val" style="color:#f87171">{len(gerileyen)}</div><div class="neg">sira dustu</div></div>', unsafe_allow_html=True)
c4.markdown(f'<div class="mcard"><div class="lbl">Ort 2025 Sira</div><div class="val">{ort25:,.0f}</div><div class="{"pos" if delta>0 else "neg"}">{abs(delta):,.0f} fark</div></div>', unsafe_allow_html=True)
c5.markdown(f'<div class="mcard"><div class="lbl">En Iyi Sira</div><div class="val" style="color:#fbbf24">{int(filt["2025"].min()):,}</div><div class="pos">{en_iyi_ad}</div></div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)
st.markdown('<div class="sec">Trend ve Dagilim</div>', unsafe_allow_html=True)

ca, cb = st.columns([1, 1.4])

with ca:
    tc = filt["TREND"].value_counts().reset_index()
    tc.columns = ["Trend", "Sayi"]
    cmap = {"Guclu Iyilesme": "#059669", "Iyilesme": "#34d399", "Stabil": "#94a3b8", "Gerileme": "#f87171", "Yeni": "#818cf8"}
    f1 = px.pie(tc, names="Trend", values="Sayi", hole=0.55, color="Trend", color_discrete_map=cmap, title="Trend Dagilimi")
    f1.update_layout(**layout(title_font=dict(color="#93c5fd", family="Syne", size=14), legend=dict(font=dict(color="#94a3b8", size=11), bgcolor="rgba(0,0,0,0)")))
    st.plotly_chart(f1, use_container_width=True)

with cb:
    sc = filt[filt["TREND"] != "Yeni"].dropna(subset=["2023", "2025"])
    f2 = px.scatter(sc, x="2023", y="2025", color="TUR",
                    hover_data=["PROGRAM ADI", "OKUL ADI", "25/23"],
                    title="2023 vs 2025 Basari Sirasi",
                    labels={"2023": "Siralama 2023", "2025": "Siralama 2025"},
                    color_discrete_sequence=["#3b82f6", "#f59e0b", "#10b981"])
    mv = max(sc["2023"].max(), sc["2025"].max()) if len(sc) > 0 else 2000000
    f2.add_shape(type="line", x0=0, y0=0, x1=mv, y1=mv, line=dict(color="#334155", dash="dot", width=1.5))
    f2.update_layout(**layout(
        title_font=dict(color="#93c5fd", family="Syne", size=13),
        xaxis=dict(gridcolor="#1e2d50", color="#64748b"),
        yaxis=dict(gridcolor="#1e2d50", color="#64748b"),
        legend=dict(font=dict(size=11, color="#94a3b8"), bgcolor="rgba(0,0,0,0)"),
    ))
    st.plotly_chart(f2, use_container_width=True)

st.markdown('<div class="sec">Okul Bazli Performans</div>', unsafe_allow_html=True)

og = df.groupby("OKUL ADI").agg(
    y23=("2023", "mean"), y24=("2024", "mean"), y25=("2025", "mean")
).reset_index().dropna().sort_values("y25")

f3 = go.Figure()
f3.add_trace(go.Bar(name="2023", x=og["OKUL ADI"], y=og["y23"], marker_color="#1e3a5f"))
f3.add_trace(go.Bar(name="2024", x=og["OKUL ADI"], y=og["y24"], marker_color="#2563eb"))
f3.add_trace(go.Bar(name="2025", x=og["OKUL ADI"], y=og["y25"], marker_color="#3b82f6"))
f3.update_layout(**layout(
    barmode="group", height=420,
    title=dict(text="Okul Bazli Ort Basari Sirasi", font=dict(color="#93c5fd", family="Syne", size=14)),
    xaxis=dict(tickangle=-40, gridcolor="#1e2d50", color="#64748b", tickfont=dict(size=10)),
    yaxis=dict(gridcolor="#1e2d50", color="#64748b", title="Ort Siralama"),
    legend=dict(font=dict(size=11, color="#94a3b8"), bgcolor="rgba(0,0,0,0)"),
    margin=dict(t=60, b=120, l=20, r=20),
))
st.plotly_chart(f3, use_container_width=True)

st.markdown('<div class="sec">En Fazla Iyilesen ve Gerileyen</div>', unsafe_allow_html=True)

vdf = filt[filt["TREND"] != "Yeni"].dropna(subset=["25/23"])
cc, cd = st.columns(2)

with cc:
    ti = vdf.nsmallest(10, "25/23")[["PROGRAM ADI", "OKUL ADI", "25/23", "2025"]]
    f4 = px.bar(ti, x="25/23", y="PROGRAM ADI", orientation="h",
                color="25/23", color_continuous_scale=["#059669", "#34d399", "#a7f3d0"],
                title="En Fazla Iyilesen 10 Program", hover_data=["OKUL ADI", "2025"])
    f4.update_layout(**layout(
        title_font=dict(color="#34d399", family="Syne", size=13),
        xaxis=dict(gridcolor="#1e2d50", color="#64748b"),
        yaxis=dict(color="#94a3b8", tickfont=dict(size=10)),
        coloraxis_showscale=False, height=380,
    ))
    st.plotly_chart(f4, use_container_width=True)

with cd:
    tg = vdf.nlargest(10, "25/23")[["PROGRAM ADI", "OKUL ADI", "25/23", "2025"]]
    f5 = px.bar(tg, x="25/23", y="PROGRAM ADI", orientation="h",
                color="25/23", color_continuous_scale=["#dc2626", "#f87171", "#fca5a5"],
                title="En Fazla Gerileyen 10 Program", hover_data=["OKUL ADI", "2025"])
    f5.update_layout(**layout(
        title_font=dict(color="#f87171", family="Syne", size=13),
        xaxis=dict(gridcolor="#1e2d50", color="#64748b"),
        yaxis=dict(color="#94a3b8", tickfont=dict(size=10)),
        coloraxis_showscale=False, height=380,
    ))
    st.plotly_chart(f5, use_container_width=True)

st.markdown('<div class="sec">3 Yillik Trend</div>', unsafe_allow_html=True)

ld = df.groupby("OKUL ADI").agg(y23=("2023","mean"), y24=("2024","mean"), y25=("2025","mean")).reset_index().dropna()
f6 = go.Figure()
clrs = px.colors.qualitative.Set3
for i, (_, row) in enumerate(ld.iterrows()):
    f6.add_trace(go.Scatter(
        x=[2023, 2024, 2025], y=[row["y23"], row["y24"], row["y25"]],
        mode="lines+markers", name=row["OKUL ADI"],
        line=dict(color=clrs[i % len(clrs)], width=1.5), marker=dict(size=5),
    ))
f6.update_layout(**layout(
    title=dict(text="Okul Bazli Ort Siralama Trendi", font=dict(color="#93c5fd", family="Syne", size=14)),
    xaxis=dict(tickvals=[2023, 2024, 2025], gridcolor="#1e2d50", color="#64748b"),
    yaxis=dict(gridcolor="#1e2d50", color="#64748b", title="Ort Basari Sirasi", autorange="reversed"),
    legend=dict(font=dict(size=9, color="#94a3b8"), bgcolor="rgba(0,0,0,0)", orientation="v", x=1.01, y=0.5),
    height=500, margin=dict(t=60, b=30, l=20, r=220),
))
st.plotly_chart(f6, use_container_width=True)

st.markdown('<div class="sec">Ham Veri</div>', unsafe_allow_html=True)

disp = filt[["OKUL ADI", "PROGRAM ADI", "2023", "2024", "2025", "25/23", "25/24", "TREND", "TUR"]].copy()
for col in ["2023", "2024"]:
    disp[col] = disp[col].apply(lambda x: f"{x:,.0f}" if pd.notna(x) else "Yeni")
disp["2025"] = disp["2025"].apply(lambda x: f"{x:,.0f}" if pd.notna(x) else "-")
disp["25/23"] = disp["25/23"].apply(lambda x: f"{x:+,.0f}" if pd.notna(x) else "-")
disp["25/24"] = disp["25/24"].apply(lambda x: f"{x:+,.0f}" if pd.notna(x) else "-")
st.dataframe(disp.rename(columns={"OKUL ADI":"Okul","PROGRAM ADI":"Program","25/23":"D23-25","25/24":"D24-25","TUR":"Tur"}),
             use_container_width=True, hide_index=True, height=400)

st.caption("Balikesir Universitesi - YKS Program Basari Sirasi - Kaynak: OSYM")
