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

/* ── Temel font ── */
html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; color: #1E1A14; }

/* ── Ana sayfa zemin ── */
[data-testid="stAppViewContainer"] {
    background-color: #EDE8E0;
    background-image: radial-gradient(circle, rgba(160,140,110,0.22) 1px, transparent 1px);
    background-size: 22px 22px;
}

/* ── Icerik alani ── */
[data-testid="stAppViewBlockContainer"] {
    background: rgba(252,249,244,0.90);
    border-radius: 16px;
    padding: 2rem 2.5rem;
    box-shadow: 0 2px 24px rgba(100,80,50,0.08);
}

/* ════════════════════════════════════
   SIDEBAR - koyu zemin, krem yazi
   ════════════════════════════════════ */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #1C1610 0%, #251D14 100%) !important;
    border-right: 2px solid #3A2E1E !important;
}

/* Sidebar baslik ve aciklamalar */
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 { color: #F0E6D0 !important; font-family: 'Syne', sans-serif !important; }
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] .stMarkdown p { color: #C8B898 !important; }
[data-testid="stSidebar"] .stCaption { color: #8C7A5C !important; }

/* Selectbox etiket */
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] .stSelectbox label { color: #D4C4A0 !important; font-size: 0.82rem !important; letter-spacing: 0.04em; }

/* Selectbox kutu - koyu zemin, krem yazi */
[data-testid="stSidebar"] [data-baseweb="select"] > div:first-child {
    background-color: #2C2218 !important;
    border-color: #5A4A30 !important;
    border-radius: 8px !important;
}
[data-testid="stSidebar"] [data-baseweb="select"] span,
[data-testid="stSidebar"] [data-baseweb="select"] div { color: #E8D8B8 !important; }
[data-testid="stSidebar"] [data-baseweb="select"] svg { fill: #A89060 !important; }

/* Dropdown acilan liste */
[data-baseweb="popover"] [data-baseweb="menu"] {
    background-color: #2C2218 !important;
    border: 1px solid #5A4A30 !important;
    border-radius: 8px !important;
}
[data-baseweb="popover"] [role="option"] { color: #E8D8B8 !important; background-color: #2C2218 !important; }
[data-baseweb="popover"] [role="option"]:hover { background-color: #3A2E1E !important; color: #F5EAD0 !important; }
[data-baseweb="popover"] [aria-selected="true"] { background-color: #4A3820 !important; color: #F0DDB0 !important; }

/* Multiselect - ana sayfadaki */
[data-baseweb="select"] {
    background-color: #F8F4EE !important;
    border-color: #C0B090 !important;
    border-radius: 8px !important;
}
[data-baseweb="select"] span { color: #2A1F12 !important; }
[data-baseweb="input"] { background-color: #F8F4EE !important; }
.stMultiSelect [data-baseweb="tag"] { background-color: #D4C4A0 !important; color: #1E1A14 !important; }

/* ── Basliklar ── */
h1, h2, h3 { font-family: 'Syne', sans-serif !important; color: #1E1A14 !important; }

/* ── Metrik kartlar ── */
.mcard {
    background: linear-gradient(135deg, #FAF6EE, #F0E8D8);
    border: 1px solid #D0C4A8;
    border-top: 3px solid #A89060;
    border-radius: 12px;
    padding: 16px 18px;
    text-align: center;
    box-shadow: 0 2px 10px rgba(100,80,40,0.08);
}
.mcard .lbl { color: #7A6A52; font-size: 0.74rem; letter-spacing: 0.09em; text-transform: uppercase; margin-bottom: 5px; }
.mcard .val { color: #1E1A14; font-size: 1.65rem; font-weight: 700; font-family: 'Syne', sans-serif; }
.mcard .pos { color: #2E6B45; font-size: 0.83rem; font-weight: 600; }
.mcard .neg { color: #962828; font-size: 0.83rem; font-weight: 600; }

/* ── Bolum basliklari ── */
.sec {
    font-family: 'Syne', sans-serif;
    font-size: 1.0rem;
    font-weight: 700;
    color: #2A1F12;
    border-left: 4px solid #A89060;
    background: linear-gradient(90deg, rgba(168,144,96,0.12) 0%, transparent 70%);
    padding: 7px 0 7px 14px;
    margin: 26px 0 14px;
    text-transform: uppercase;
    letter-spacing: 0.07em;
    border-radius: 0 6px 6px 0;
}

/* ════════════════════════════════════
   DATAFRAME TABLOSU - koyu zemin
   ════════════════════════════════════ */
[data-testid="stDataFrame"] {
    border-radius: 12px;
    overflow: hidden;
    box-shadow: 0 2px 16px rgba(40,28,12,0.18);
}
/* Tablo ana sarici iframe override */
[data-testid="stDataFrame"] iframe { border-radius: 12px; }

/* Streamlit data editor / dataframe genel */
.dvn-scroller { background-color: #1C1610 !important; }
.stDataFrame div[data-testid="stDataFrameResizable"] { background: #1C1610 !important; }

/* Glide data grid hucreleri */
.dvn-stack { background-color: #1C1610 !important; }
canvas.dvn-canvas { background-color: #1C1610 !important; }

/* ── Genel metin ── */
.stMarkdown p, .stMarkdown span, .stCaption { color: #3A3020 !important; }

/* ── Expander baslik ve icerik ── */
[data-testid="stExpander"] summary p,
[data-testid="stExpander"] summary span,
[data-testid="stExpander"] summary div,
[data-testid="stExpander"] > details > summary { color: #2A1F12 !important; font-weight: 600; }
[data-testid="stExpander"] { border: 1px solid #C8B890 !important; border-radius: 10px !important; background: #F8F3EC !important; }
[data-testid="stExpander"] svg { fill: #6B5A3A !important; }
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

def render_table(df, height_px=420):
    """DataFrame'i koyu temali, tamamen okunabilir HTML tabloya donusturur."""
    cols = df.columns.tolist()
    header_cells = "".join(
        f"<th style='"
        "background:#2A1E12; color:#E8D0A0; font-family:Syne,sans-serif; "
        "font-size:0.78rem; font-weight:700; letter-spacing:0.07em; "
        "text-transform:uppercase; padding:10px 12px; border-bottom:2px solid #6A5030; "
        "white-space:nowrap;"
        f"'>{c}</th>"
        for c in cols
    )
    rows_html = ""
    for idx, row in enumerate(df.itertuples(index=False)):
        bg = "#1C1610" if idx % 2 == 0 else "#231A0E"
        cells = "".join(
            f"<td style='"
            "color:#D4BF98; font-size:0.82rem; padding:8px 12px; "
            f"border-bottom:1px solid #3A2A18; background:{bg}; white-space:nowrap;"
            f"'>{v}</td>"
            for v in row
        )
        rows_html += f"<tr>{cells}</tr>"

    table_html = f"""
    <div style='
        background:#1C1610;
        border-radius:12px;
        border:1px solid #4A3520;
        box-shadow:0 4px 20px rgba(10,6,2,0.30);
        overflow:hidden;
        margin-bottom:8px;
    '>
        <div style='overflow:auto; max-height:{height_px}px;'>
            <table style='width:100%; border-collapse:collapse;'>
                <thead><tr>{header_cells}</tr></thead>
                <tbody>{rows_html}</tbody>
            </table>
        </div>
    </div>
    """
    st.markdown(table_html, unsafe_allow_html=True)


BASE = dict(
    paper_bgcolor="rgba(252,249,244,0.0)",
    plot_bgcolor="rgba(248,244,238,0.85)",
    font=dict(color="#1E1A14", family="DM Sans"),
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

if len(filt) == 0:
    st.warning("Analiz edilecek veri bulunamadi. Lutfen farkli filtre secenekleri deneyin.")
else:
    st.markdown("<h1 style='color:#1E1A14; font-family:Syne,sans-serif; font-size:1.9rem;'>BAU Program Basari Istatistikleri</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color:#6B5C45; font-size:0.95rem;'>Balikesir Universitesi  -  2023-2025  -  YKS Basari Sirasi Analizi</p>", unsafe_allow_html=True)

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
    c2.markdown(f'<div class="mcard"><div class="lbl">Iyilesen</div><div class="val" style="color:#2E6B45">{len(iyilesen)}</div><div class="pos">%{pct:.0f}</div></div>', unsafe_allow_html=True)
    c3.markdown(f'<div class="mcard"><div class="lbl">Gerileyen</div><div class="val" style="color:#962828">{len(gerileyen)}</div><div class="neg">sira dustu</div></div>', unsafe_allow_html=True)
    c4.markdown(f'<div class="mcard"><div class="lbl">Ort 2025 Sira</div><div class="val">{ort25:,.0f}</div><div class="{"pos" if delta>0 else "neg"}">{abs(delta):,.0f} fark</div></div>', unsafe_allow_html=True)
    c5.markdown(f'<div class="mcard"><div class="lbl">En Iyi Sira</div><div class="val" style="color:#8B6914">{int(filt["2025"].min()):,}</div><div class="pos">{en_iyi_ad}</div></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="sec">Trend ve Dagilim</div>', unsafe_allow_html=True)

    ca, cb = st.columns([1, 1.4])

    with ca:
        tc = filt["TREND"].value_counts().reset_index()
        tc.columns = ["Trend", "Sayi"]
        cmap = {"Guclu Iyilesme": "#059669", "Iyilesme": "#34d399", "Stabil": "#94a3b8", "Gerileme": "#f87171", "Yeni": "#818cf8"}
        f1 = px.pie(tc, names="Trend", values="Sayi", hole=0.55, color="Trend", color_discrete_map=cmap, title="Trend Dagilimi")
        f1.update_layout(**layout(title_font=dict(color="#2A1F12", family="Syne", size=14), legend=dict(font=dict(color="#3A3020", size=11), bgcolor="rgba(0,0,0,0)")))
        st.plotly_chart(f1, use_container_width=True)

    with cb:
        sc = filt[filt["TREND"] != "Yeni"].dropna(subset=["2023", "2025"])
        f2 = px.scatter(sc, x="2023", y="2025", color="TUR",
                        hover_data=["PROGRAM ADI", "OKUL ADI", "25/23"],
                        title="2023 vs 2025 Basari Sirasi",
                        labels={"2023": "Siralama 2023", "2025": "Siralama 2025"},
                        color_discrete_sequence=["#3b82f6", "#f59e0b", "#10b981"])
        mv = max(sc["2023"].max(), sc["2025"].max()) if len(sc) > 0 else 2000000
        f2.add_shape(type="line", x0=0, y0=0, x1=mv, y1=mv, line=dict(color="#B8A882", dash="dot", width=1.5))
        f2.update_layout(**layout(
            title_font=dict(color="#2A1F12", family="Syne", size=13),
            xaxis=dict(gridcolor="#D8CFBE", color="#3A3020", tickfont=dict(color="#3A3020")),
            yaxis=dict(gridcolor="#D8CFBE", color="#3A3020", tickfont=dict(color="#3A3020")),
            legend=dict(font=dict(size=11, color="#2A1F12"), bgcolor="rgba(252,249,244,0.9)", bordercolor="#C8B890", borderwidth=1),
        ))
        st.plotly_chart(f2, use_container_width=True)

    st.markdown('<div class="sec">Okul Bazli Performans</div>', unsafe_allow_html=True)

    og = df.groupby("OKUL ADI").agg(
        y23=("2023", "mean"), y24=("2024", "mean"), y25=("2025", "mean")
    ).reset_index().dropna().sort_values("y25")

    f3 = go.Figure()

    # Pastel palet - akademik, sik, birbirinden net ayirt edilebilir
    PASTEL_2023 = "#A8C7E8"   # pastel celik mavisi
    PASTEL_2024 = "#F4B183"   # pastel seftali turuncu
    PASTEL_2025 = "#9DC19D"   # pastel adacayi yesili
    BORDER_2023 = "#6A9EC4"
    BORDER_2024 = "#D4845A"
    BORDER_2025 = "#6A9C6A"
    LABEL_2023  = "#3A6E9C"
    LABEL_2024  = "#A85A2A"
    LABEL_2025  = "#3A703A"

    f3.add_trace(go.Bar(
        name="2023",
        x=og["OKUL ADI"], y=og["y23"],
        marker=dict(
            color=PASTEL_2023,
            line=dict(color=BORDER_2023, width=1.2),
            opacity=0.88,
        ),
        text=og["y23"].apply(lambda v: f"{int(v):,}"),
        textposition="outside",
        textfont=dict(size=9, color=LABEL_2023, family="DM Sans"),
    ))

    f3.add_trace(go.Bar(
        name="2024",
        x=og["OKUL ADI"], y=og["y24"],
        marker=dict(
            color=PASTEL_2024,
            line=dict(color=BORDER_2024, width=1.2),
            opacity=0.88,
        ),
        text=og["y24"].apply(lambda v: f"{int(v):,}"),
        textposition="outside",
        textfont=dict(size=9, color=LABEL_2024, family="DM Sans"),
    ))

    f3.add_trace(go.Bar(
        name="2025",
        x=og["OKUL ADI"], y=og["y25"],
        marker=dict(
            color=PASTEL_2025,
            line=dict(color=BORDER_2025, width=1.2),
            opacity=0.88,
        ),
        text=og["y25"].apply(lambda v: f"{int(v):,}"),
        textposition="outside",
        textfont=dict(size=9, color=LABEL_2025, family="DM Sans"),
    ))

    f3.update_layout(**layout(
        barmode="group",
        height=500,
        bargap=0.22,
        bargroupgap=0.06,
        title=dict(
            text="Okul Bazli Ortalama Basari Sirasi  (2023 - 2024 - 2025)",
            font=dict(color="#CBD5E1", family="Syne", size=14),
        ),
        xaxis=dict(
            tickangle=-40,
            gridcolor="#1e2d50",
            color="#64748b",
            tickfont=dict(size=10, color="#94a3b8", family="DM Sans"),
            showline=True,
            linecolor="#2d3f5c",
        ),
        yaxis=dict(
            gridcolor="#1e2d50",
            color="#64748b",
            title=dict(text="Ortalama Basari Sirasi", font=dict(color="#94a3b8", size=11)),
            tickfont=dict(size=10, color="#94a3b8"),
            showline=True,
            linecolor="#2d3f5c",
        ),
        legend=dict(
            title=dict(text="Yil", font=dict(color="#CBD5E1", size=12, family="Syne")),
            font=dict(size=12, color="#CBD5E1", family="DM Sans"),
            bgcolor="rgba(17,24,39,0.9)",
            bordercolor="#2d3f5c",
            borderwidth=1,
            orientation="h",
            x=0, y=1.09,
            traceorder="normal",
        ),
        margin=dict(t=90, b=150, l=20, r=20),
        uniformtext=dict(mode="hide", minsize=7),
    ))
    st.plotly_chart(f3, use_container_width=True)

    st.markdown('<div class="sec">En Fazla Iyilesen ve Gerileyen</div>', unsafe_allow_html=True)

    vdf = filt[filt["TREND"] != "Yeni"].dropna(subset=["25/23"])
    cc, cd = st.columns(2)

    with cc:
        ti = vdf.nsmallest(10, "25/23")[["PROGRAM ADI", "OKUL ADI", "25/23", "2025"]]
        f4 = px.bar(ti, x="25/23", y="PROGRAM ADI", orientation="h",
                    color="25/23", color_continuous_scale=["#1A5C38", "#3A9E62", "#8ED4AA"],
                    title="En Fazla Iyilesen 10 Program", hover_data=["OKUL ADI", "2025"])
        f4.update_layout(**layout(
            title_font=dict(color="#1A5C38", family="Syne", size=13),
            xaxis=dict(gridcolor="#D8CFBE", color="#3A3020", tickfont=dict(color="#3A3020")),
            yaxis=dict(color="#3A3020", tickfont=dict(size=10, color="#2A1F12")),
            coloraxis_showscale=False, height=400,
        ))
        st.plotly_chart(f4, use_container_width=True)

    with cd:
        tg = vdf.nlargest(10, "25/23")[["PROGRAM ADI", "OKUL ADI", "25/23", "2025"]]
        f5 = px.bar(tg, x="25/23", y="PROGRAM ADI", orientation="h",
                    color="25/23", color_continuous_scale=["#7A1010", "#C43030", "#E89090"],
                    title="En Fazla Gerileyen 10 Program", hover_data=["OKUL ADI", "2025"])
        f5.update_layout(**layout(
            title_font=dict(color="#7A1010", family="Syne", size=13),
            xaxis=dict(gridcolor="#D8CFBE", color="#3A3020", tickfont=dict(color="#3A3020")),
            yaxis=dict(color="#3A3020", tickfont=dict(size=10, color="#2A1F12")),
            coloraxis_showscale=False, height=400,
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
        title=dict(text="Okul Bazli Ort Siralama Trendi", font=dict(color="#2A1F12", family="Syne", size=14)),
        xaxis=dict(tickvals=[2023, 2024, 2025], gridcolor="#D8CFBE", color="#3A3020", tickfont=dict(color="#3A3020")),
        yaxis=dict(gridcolor="#D8CFBE", color="#3A3020", title="Ort Basari Sirasi", autorange="reversed", tickfont=dict(color="#3A3020")),
        legend=dict(font=dict(size=9, color="#2A1F12"), bgcolor="rgba(252,249,244,0.92)", bordercolor="#C8B890", borderwidth=1, orientation="v", x=1.01, y=0.5),
        height=500, margin=dict(t=60, b=30, l=20, r=220),
    ))
    st.plotly_chart(f6, use_container_width=True)

    st.markdown('<div class="sec">Ham Veri Tablosu</div>', unsafe_allow_html=True)

    disp = filt[["OKUL ADI", "PROGRAM ADI", "2023", "2024", "2025", "25/23", "25/24", "TREND", "TUR"]].copy()
    for col in ["2023", "2024"]:
        disp[col] = disp[col].apply(lambda x: f"{x:,.0f}" if pd.notna(x) else "Yeni")
    disp["2025"] = disp["2025"].apply(lambda x: f"{x:,.0f}" if pd.notna(x) else "-")
    disp["25/23"] = disp["25/23"].apply(lambda x: f"{x:+,.0f}" if pd.notna(x) else "-")
    disp["25/24"] = disp["25/24"].apply(lambda x: f"{x:+,.0f}" if pd.notna(x) else "-")
    disp_rename = disp.rename(columns={"OKUL ADI":"Okul","PROGRAM ADI":"Program","25/23":"D23-25","25/24":"D24-25","TUR":"Tur"})

    render_table(disp_rename, height_px=420)

    st.markdown('<div class="sec">Yillara Gore Yerlesme Sirasi Degisimi</div>', unsafe_allow_html=True)

    st.markdown("<p style='color:#6B5840; font-size:0.9rem; margin-bottom:16px;'>Program secin — noktalar her yilin sirasini, cizgi ise trendi gosterir. Dusuk sira = daha basarili.</p>", unsafe_allow_html=True)

    col_prog1, col_prog2 = st.columns([2, 1])

    with col_prog1:
        program_listesi = sorted(df["PROGRAM ADI"].unique().tolist())
        secili_programlar = st.multiselect(
            "Program Sec (coklu secim yapabilirsiniz)",
            program_listesi,
            default=program_listesi[:5]
        )

    with col_prog2:
        okul_filtre = st.selectbox("Okul Filtresi", ["Tumu"] + sorted(df["OKUL ADI"].unique().tolist()), key="okul_puan")

    puan_df = df.copy()
    if okul_filtre != "Tumu":
        puan_df = puan_df[puan_df["OKUL ADI"] == okul_filtre]
    if secili_programlar:
        puan_df = puan_df[puan_df["PROGRAM ADI"].isin(secili_programlar)]

    if len(puan_df) == 0:
        st.warning("Secilen filtrelere gore veri bulunamadi.")
    else:
        long_df = puan_df.melt(
            id_vars=["OKUL ADI", "PROGRAM ADI"],
            value_vars=["2023", "2024", "2025"],
            var_name="Yil",
            value_name="Siralama"
        ).dropna(subset=["Siralama"])
        long_df["Yil"] = long_df["Yil"].astype(int)
        long_df["Etiket"] = long_df["PROGRAM ADI"] + " (" + long_df["OKUL ADI"].str[:20] + ")"

        # BAU kurumsal renk paleti - acik mavi slayt arkaplani icin kontrast optimize edilmis
        # Lacivert (#003366), altin (#C8A440) ve turkuaz tamamlayici renkler
        renkler = [
            "#003366",  # BAU lacivert
            "#C8A440",  # BAU altin
            "#005B99",  # koyu turkuaz mavi
            "#8B0000",  # koyu bordo
            "#1A6B3C",  # koyu yesil
            "#6B3FA0",  # koyu mor
            "#B84B00",  # koyu turuncu
            "#006B6B",  # koyu teal
            "#003D99",  # saks mavisi
            "#996600",  # koyu sari
            "#7B0057",  # koyu fusya
            "#004D00",  # koyu orman yesili
            "#8B4000",  # koyu kahverengi
            "#003355",  # gece mavisi
            "#5C0A0A",  # koyu kiremit
        ]

        # Pastel keten/krem - akademik, sicak, beyaz kagit degil
        SLIDE_BG    = "#F5F0E8"   # sicak keten krem
        PLOT_BG     = "#FAF7F2"   # cok acik krem - kagit gibi degil, sicak
        TITLE_COLOR = "#2C1F0E"   # espresso kahve - tam kontrast
        AXIS_COLOR  = "#4A3728"   # koyu kahve - eksen yazilari
        GRID_COLOR  = "#DDD0BC"   # kum bej - grid cizgileri
        DASH_COLOR  = "#C4A882"   # altin bej - dikey dashed cizgiler
        LEGEND_BG   = "rgba(245,240,232,0.94)"  # keten legend arka plani
        LEGEND_FG   = "#2C1F0E"   # legend yazi rengi

        f7 = go.Figure()

        # Dikey dashed cizgiler her yil icin
        for yil in [2023, 2024, 2025]:
            f7.add_shape(
                type="line",
                x0=yil, x1=yil, y0=0, y1=1,
                xref="x", yref="paper",
                line=dict(color=DASH_COLOR, dash="dash", width=1.5),
            )

        for i, (etiket, grp) in enumerate(long_df.groupby("Etiket")):
            renk = renkler[i % len(renkler)]
            grp_sorted = grp.sort_values("Yil")
            f7.add_trace(go.Scatter(
                x=grp_sorted["Yil"],
                y=grp_sorted["Siralama"],
                mode="lines+markers+text",
                name=etiket,
                line=dict(color=renk, width=3),
                marker=dict(
                    size=13,
                    color=renk,
                    line=dict(color="#FFFFFF", width=2),
                    symbol="circle",
                ),
                text=[f"{int(v):,}" for v in grp_sorted["Siralama"]],
                textposition="top center",
                textfont=dict(color=renk, size=12, family="DM Sans"),
                hovertemplate=(
                    "<b>%{fullData.name}</b><br>"
                    "Yil: %{x}<br>"
                    "Siralama: %{y:,.0f}<extra></extra>"
                ),
                cliponaxis=False,
            ))

        y_min = long_df["Siralama"].min()
        y_max = long_df["Siralama"].max()
        y_pad = (y_max - y_min) * 0.18

        # Grafik basligini okul seciminden dinamik uret
        if okul_filtre != "Tumu":
            grafik_baslik = "<b>" + okul_filtre + "</b><br><span style='font-size:13px;color:#336699'>YKS Yerlesme Sirasi Degisimi  2023 - 2024 - 2025</span>"
            yeksen_baslik = "YKS Basari Sirasi  |  " + okul_filtre
            xeksen_baslik = "Yil  |  " + okul_filtre
        else:
            grafik_baslik = "<b>Tum Kurumlar</b><br><span style='font-size:13px;color:#336699'>YKS Yerlesme Sirasi Degisimi  2023 - 2024 - 2025</span>"
            yeksen_baslik = "YKS Basari Sirasi"
            xeksen_baslik = "Yil"

        f7.update_layout(
            paper_bgcolor=SLIDE_BG,
            plot_bgcolor=PLOT_BG,
            font=dict(color=AXIS_COLOR, family="DM Sans"),
            title=dict(
                text=grafik_baslik,
                font=dict(color=TITLE_COLOR, family="Syne", size=17),
                x=0.0,
                pad=dict(l=10),
            ),
            xaxis=dict(
                tickvals=[2023, 2024, 2025],
                ticktext=["2023", "2024", "2025"],
                gridcolor="rgba(0,0,0,0)",
                linecolor=GRID_COLOR,
                color=AXIS_COLOR,
                tickfont=dict(size=15, color=AXIS_COLOR, family="Syne"),
                title=dict(text=xeksen_baslik, font=dict(color=AXIS_COLOR, size=12)),
                range=[2022.6, 2025.4],
            ),
            yaxis=dict(
                gridcolor=GRID_COLOR,
                linecolor=GRID_COLOR,
                color=AXIS_COLOR,
                title=dict(text=yeksen_baslik, font=dict(color=AXIS_COLOR, size=12)),
                tickfont=dict(size=12, color=AXIS_COLOR),
                autorange="reversed",
                range=[y_max + y_pad, y_min - y_pad],
            ),
            legend=dict(
                font=dict(size=11, color=LEGEND_FG, family="DM Sans"),
                bgcolor=LEGEND_BG,
                bordercolor="#7AAACE",
                borderwidth=1,
                orientation="h",
                x=0, y=-0.22,
            ),
            height=600,
            margin=dict(t=100, b=130, l=190, r=40),
            hovermode="x unified",
        )

        st.plotly_chart(f7, use_container_width=True)

        with st.expander("Tablo olarak goster"):
            tablo = puan_df[["OKUL ADI", "PROGRAM ADI", "2023", "2024", "2025", "25/23"]].copy()
            tablo["2023"] = tablo["2023"].apply(lambda x: f"{x:,.0f}" if pd.notna(x) else "Yeni")
            tablo["2024"] = tablo["2024"].apply(lambda x: f"{x:,.0f}" if pd.notna(x) else "Yeni")
            tablo["2025"] = tablo["2025"].apply(lambda x: f"{x:,.0f}" if pd.notna(x) else "-")
            tablo["25/23"] = tablo["25/23"].apply(lambda x: f"{x:+,.0f}" if pd.notna(x) else "-")
            render_table(tablo.rename(columns={"OKUL ADI":"Okul","PROGRAM ADI":"Program","25/23":"Degisim"}), height_px=340)

    st.markdown("<p style='color:#8C7B65; font-size:0.78rem; text-align:center; margin-top:20px;'>Balikesir Universitesi  -  YKS Program Basari Sirasi  -  Kaynak: OSYM</p>", unsafe_allow_html=True)
