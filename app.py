import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

st.set_page_config(
    page_title="Racing Unit",
    page_icon="🏆",
    layout="wide"
)

# ==========================
# CSS TEMA BIRU
# ==========================
st.markdown("""
<style>
.stApp {background-color:#f4f8fc;}
.block-container{padding-top:1rem;padding-left:2rem;padding-right:2rem;}
section[data-testid="stSidebar"]{
    background:linear-gradient(180deg,#00529C,#003B73);
}
section[data-testid="stSidebar"] *{
    color:white !important;
}
.stButton>button{
    width:100%;
    border-radius:10px;
    background:transparent;
    color:white;
    border:none;
    text-align:left;
    font-weight:600;
}
.stButton>button:hover{
    background:rgba(255,255,255,0.15);
    border-left:4px solid #F37021;
}
div[data-testid="stMetric"]{
    background:white;
    border-left:5px solid #00529C;
    padding:10px;
    border-radius:10px;
    box-shadow:0 2px 8px rgba(0,0,0,.08);
}
</style>
""", unsafe_allow_html=True)

# ==========================
# FUNGSI PERHITUNGAN POIN MANTRI
# ==========================

def get_mantri_realisasi_poin(realisasi_pct):
    """Hitung poin Mantri berdasarkan realisasi (Maks. 50 Poin)"""
    if realisasi_pct >= 120:
        return 50
    elif realisasi_pct >= 110:
        return 45
    elif realisasi_pct >= 100:
        return 40
    elif realisasi_pct >= 90:
        return 30
    else:
        return 15

def get_mantri_quality_poin(quality_value):
    """Hitung poin Mantri berdasarkan perbaikan kualitas (Maks. 50 Poin)
    quality_value: nilai dari -10 hingga 10+ yang merepresentasikan perubahan kualitas
    Skala terbalik: nilai negatif/kecil = poin lebih tinggi, nilai positif/besar = poin lebih rendah
    """
    if quality_value <= -8:
        return 50
    elif quality_value <= -5:
        return 40
    elif quality_value <= -2:
        return 30
    elif quality_value <= 2:
        return 15
    else:
        return 0

# ==========================
# FUNGSI PERHITUNGAN POIN UNIT
# ==========================

def get_unit_growth_os_poin(growth_os_pct):
    """Hitung poin Unit berdasarkan pertumbuhan OS (Maks. 40 Poin)"""
    if growth_os_pct >= 15:
        return 40
    elif growth_os_pct >= 12:
        return 34
    elif growth_os_pct >= 10:
        return 28
    elif growth_os_pct >= 7:
        return 20
    else:
        return 10

def get_unit_quality_poin(quality_value):
    """Hitung poin Unit berdasarkan perbaikan kualitas (Maks. 35 Poin)
    quality_value: nilai dari -10 hingga 10+ yang merepresentasikan kondisi kualitas
    """
    if quality_value >= 8:
        return 35
    elif quality_value >= 5:
        return 28
    elif quality_value >= 2:
        return 20
    elif quality_value >= -2:
        return 10
    else:
        return 0

def get_unit_kupedes_poin(growth_kupedes_pct):
    """Hitung poin Unit berdasarkan growth Kupedes (Maks. 25 Poin)"""
    if growth_kupedes_pct >= 5:
        return 25
    elif growth_kupedes_pct >= 3:
        return 20
    elif growth_kupedes_pct >= 1:
        return 15
    elif growth_kupedes_pct >= 0:
        return 10
    else:
        return 0

def get_unit_category(poin_unit):
    """Tentukan kategori unit berdasarkan poin unit"""
    if poin_unit >= 90:
        return "🏆 Elite Racing Unit"
    elif poin_unit >= 80:
        return "🥇 Champion Racing Unit"
    elif poin_unit >= 70:
        return "🥈 Prime Racing Unit"
    elif poin_unit >= 60:
        return "🥉 Rising Racing Unit"
    else:
        return "📈 Growth Racing Unit"

# ==========================
# DATA PERFORMA MANTRI
# ==========================

mantri_data = pd.DataFrame({
    "Nama": ["Andi", "Budi", "Citra", "Dedi", "Eko", "Fitra", "Gita", "Hendra"],
    "Unit": ["Purwokerto Timur", "Purwokerto Timur", "Sokaraja", "Ajibarang", "Cilongok", "⭐ Unit Anda", "⭐ Unit Anda", "⭐ Unit Anda"],
    "Realisasi (%)": [118, 110, 105, 98, 92, 115, 108, 100],
    "Quality (%)": [9, 7, 6, 3, -1, 8, 5, 2]
})

mantri_data["Poin Realisasi"] = mantri_data["Realisasi (%)"].apply(get_mantri_realisasi_poin)
mantri_data["Poin Quality"] = mantri_data["Quality (%)"].apply(get_mantri_quality_poin)
mantri_data["Total Poin"] = (
    mantri_data["Poin Realisasi"] +
    mantri_data["Poin Quality"]
)
mantri_data["Rank"] = mantri_data["Total Poin"].rank(method="min", ascending=False).astype(int)

# ==========================
# DATA PERFORMA UNIT
# ==========================

unit_data = pd.DataFrame({
    "Rank": [1, 2, 3, 4, 5],
    "Unit": [
        "Purwokerto Timur",
        "Sokaraja",
        "Ajibarang",
        "⭐ Unit Anda",
        "Cilongok"
    ],
    "Growth OS (%)": [14, 16, 13, 11, 8],
    "Quality Unit (%)": [8, 7, 6, 4, -1],
    "Growth Kupedes (%)": [4.5, 5.2, 3.8, 2.1, 0.5],
    "Rank Change": [2, 1, 3, 2, -1]
})

# Hitung Rata-rata Poin Mantri per Unit
unit_mantri_avg = mantri_data.groupby("Unit")["Total Poin"].mean().reset_index()
unit_mantri_avg.columns = ["Unit", "Rata-rata Poin Mantri"]

# Merge dengan unit_data
unit_data = unit_data.merge(unit_mantri_avg, on="Unit", how="left")
unit_data["Rata-rata Poin Mantri"] = unit_data["Rata-rata Poin Mantri"].fillna(0)

# Hitung Poin Kinerja Unit
unit_data["Poin Growth OS"] = unit_data["Growth OS (%)"].apply(get_unit_growth_os_poin)
unit_data["Poin Quality Unit"] = unit_data["Quality Unit (%)"].apply(get_unit_quality_poin)
unit_data["Poin Kupedes"] = unit_data["Growth Kupedes (%)"].apply(get_unit_kupedes_poin)

# Total Poin Kinerja Unit (40 + 35 + 25 = 100)
unit_data["Total Poin Kinerja"] = (
    unit_data["Poin Growth OS"] +
    unit_data["Poin Quality Unit"] +
    unit_data["Poin Kupedes"]
)

# Normalisasi Poin Kinerja Unit ke skala 0-100
unit_data["Poin Kinerja Normalized"] = (unit_data["Total Poin Kinerja"] / 100) * 100

# Hitung Poin Unit: 70% Rata-rata Mantri + 30% Poin Kinerja Unit
unit_data["Poin Unit"] = (
    (unit_data["Rata-rata Poin Mantri"] / 100) * 70 +
    (unit_data["Poin Kinerja Normalized"] / 100) * 30
)

unit_data["Kategori"] = unit_data["Poin Unit"].apply(get_unit_category)

# Sort berdasarkan Poin Unit
unit_data = unit_data.sort_values("Poin Unit", ascending=False).reset_index(drop=True)
unit_data["Rank"] = range(1, len(unit_data) + 1)

# ==========================
# NAVIGASI
# ==========================
if "page" not in st.session_state:
    st.session_state.page = "Overview"

with st.sidebar:
    st.title("🏆 Racing Unit")
    st.caption("Performance Dashboard")
    st.divider()

    menus = [
        ("🏠 Overview", "Overview"),
        ("🏅 Leaderboard Racing Unit", "Leaderboard Racing Unit"),
        ("👨‍💼 Leaderboard Mantri", "Leaderboard Mantri"),
        ("📊 Breakdown Poin", "Breakdown Poin"),
        ("🔥 Top Performer", "Top Performer"),
    ]

    for label, value in menus:
        if st.button(label, use_container_width=True):
            st.session_state.page = value

    st.divider()
    st.info(f"Halaman Aktif:\n\n**{st.session_state.page}**")

# ==========================
# HEADER
# ==========================
h1, h2 = st.columns([5, 1])
with h1:
    st.markdown(
        "<h1 style='color:#71C5EB;margin-bottom:0'>Racing <span style='color:#0857C3'>Unit</span></h1>"
        "<p style='color:gray'>Performance & Leaderboard Dashboard | Point-Based System</p>",
        unsafe_allow_html=True
    )
with h2:
    st.metric("Periode", "Jun 2026")

st.divider()

# ==========================
# OVERVIEW
# ==========================
if st.session_state.page == "Overview":
    
    # Ambil data unit anda (rank 4)
    unit_anda = unit_data[unit_data["Unit"] == "⭐ Unit Anda"].iloc[0]
    top_unit = unit_data.iloc[0]
    
    # KPI Cards
    k1, k2, k3, k4, k5 = st.columns(5)
    with k1:
        st.metric("🏅 Ranking", f"#{int(unit_anda['Rank'])} / 23", f"+{int(unit_anda['Rank Change'])}")
    with k2:
        st.metric("💯 Performance", f"{unit_anda['Poin Unit']:.1f} Poin", f"/ 100")
    with k3:
        st.metric("💰 Growth OS", f"{unit_anda['Growth OS (%)']:.1f}%", f"({int(unit_anda['Poin Growth OS'])}/40)")
    with k4:
        st.metric("📊 Kualitas", f"{unit_anda['Quality Unit (%)']:.1f}%", f"({int(unit_anda['Poin Quality Unit'])}/35)")
    with k5:
        st.metric("📈 Kategori", unit_anda['Kategori'])

    st.divider()

    # Section 1: Leaderboard Racing Unit vs Breakdown Poin
    c1, c2 = st.columns([2, 1])

    with c1:
        st.subheader("🏅 Leaderboard Racing Unit (Berbasis Performance Point)")
        
        leaderboard_display = unit_data[["Rank", "Unit", "Poin Unit", "Kategori"]].copy()
        leaderboard_display.columns = ["#", "Racing Unit", "Performance Poin", "Kategori"]
        leaderboard_display["#"] = leaderboard_display["#"].astype(int)
        leaderboard_display["Performance Poin"] = leaderboard_display["Performance Poin"].round(1)
        
        st.dataframe(leaderboard_display, use_container_width=True, hide_index=True)
        
        # Visualisasi bar chart
        fig = px.bar(
            unit_data.sort_values("Poin Unit"),
            x="Poin Unit",
            y="Unit",
            orientation="h",
            text_auto=".1f",
            title="Total Performance Point per Racing Unit"
        )
        fig.update_traces(marker_color="#00529C")
        fig.update_layout(
            plot_bgcolor="white",
            paper_bgcolor="white",
            xaxis=dict(range=[0, 100]),
            showlegend=False
        )
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        st.subheader("📊 Breakdown Poin Unit Anda")
        
        breakdown = pd.DataFrame({
            "Indikator": ["Growth OS", "Kualitas Unit", "Kupedes"],
            "Poin": [
                int(unit_anda["Poin Growth OS"]),
                int(unit_anda["Poin Quality Unit"]),
                int(unit_anda["Poin Kupedes"])
            ],
            "Maksimal": [40, 35, 25]
        })
        
        fig_breakdown = px.bar(
            breakdown,
            x="Poin",
            y="Indikator",
            orientation="h",
            text="Poin",
            color="Poin",
            color_continuous_scale="Blues"
        )
        fig_breakdown.update_layout(
            plot_bgcolor="white",
            paper_bgcolor="white",
            showlegend=False
        )
        st.plotly_chart(fig_breakdown, use_container_width=True)

        st.info(f"""
**Total Poin Unit: {unit_anda['Poin Unit']:.1f} / 100**

Target Top 3: +{max(0, 70 - unit_anda['Poin Unit']):.1f} poin
        """)

    st.divider()

    # Section 2: Kontribusi Mantri & Top Performer
    a, b = st.columns([2, 1])

    with a:
        st.subheader("👨‍💼 Top Mantri di Unit Anda")
        
        # Filter mantri dari unit anda
        unit_anda_name = unit_anda["Unit"]
        mantri_unit_anda = mantri_data[mantri_data["Unit"] == unit_anda_name].sort_values("Total Poin", ascending=False)
        
        if len(mantri_unit_anda) > 0:
            fig3 = px.bar(
                mantri_unit_anda.sort_values("Total Poin"),
                x="Total Poin",
                y="Nama",
                orientation="h",
                text="Total Poin"
            )
            fig3.update_traces(marker_color="#F37021")
            fig3.update_layout(
                plot_bgcolor="white",
                paper_bgcolor="white",
                xaxis=dict(range=[0, 100])
            )
            st.plotly_chart(fig3, use_container_width=True)
        else:
            st.info("Tidak ada data mantri untuk unit ini.")

    with b:
        st.subheader("🔥 Top Performer (Mantri)")
        top_mantri_sorted = mantri_data.sort_values("Total Poin", ascending=False)
        
        for idx, row in top_mantri_sorted.head(3).iterrows():
            medals = ["🥇", "🥈", "🥉"]
            st.metric(
                f"{medals[min(idx, 2)]} {row['Nama']}",
                f"{int(row['Total Poin'])} Poin",
                f"({row['Unit']})"
            )

    st.divider()

    # Insight
    st.info(f"""
**📊 Insight Bulan Ini**

- ✅ Unit Anda berada di peringkat {int(unit_anda['Rank'])} dari 23.
- {'📈' if unit_anda['Rank Change'] > 0 else '📉'} Naik {abs(int(unit_anda['Rank Change']))} peringkat dibanding bulan lalu.
- 🎯 Performance: {unit_anda['Poin Unit']:.1f} / 100 Poin ({unit_anda['Kategori']})
- 💰 Growth OS: {unit_anda['Growth OS (%)']:.1f}% ({int(unit_anda['Poin Growth OS'])}/40 Poin)
- 🛡️ Kualitas Unit: {unit_anda['Quality Unit (%)']:.1f}% ({int(unit_anda['Poin Quality Unit'])}/35 Poin)
- 📊 Growth Kupedes: {unit_anda['Growth Kupedes (%)']:.1f}% ({int(unit_anda['Poin Kupedes'])}/25 Poin)
- 👥 Rata-rata Poin Mantri: {unit_anda['Rata-rata Poin Mantri']:.1f} / 100
- 🏆 **Dibutuhkan {max(0, top_unit['Poin Unit'] - unit_anda['Poin Unit']):.1f} poin lagi untuk masuk ranking 1.**
    """)

# ==========================
# LEADERBOARD RACING UNIT
# ==========================
elif st.session_state.page == "Leaderboard Racing Unit":

    st.header("🏅 Leaderboard Racing Unit - Berbasis Performance Point")
    
    display_df = unit_data[[
        "Rank", "Unit", "Growth OS (%)", "Quality Unit (%)", "Growth Kupedes (%)",
        "Poin Growth OS", "Poin Quality Unit", "Poin Kupedes",
        "Rata-rata Poin Mantri", "Poin Unit", "Kategori"
    ]].copy()
    
    display_df["Rank"] = display_df["Rank"].astype(int)
    display_df["Poin Growth OS"] = display_df["Poin Growth OS"].astype(int)
    display_df["Poin Quality Unit"] = display_df["Poin Quality Unit"].astype(int)
    display_df["Poin Kupedes"] = display_df["Poin Kupedes"].astype(int)
    display_df["Rata-rata Poin Mantri"] = display_df["Rata-rata Poin Mantri"].round(1)
    display_df["Poin Unit"] = display_df["Poin Unit"].round(1)
    
    display_df.columns = [
        "#", "Racing Unit", "Growth OS %", "Kualitas %", "Growth Kupedes %",
        "Poin OS", "Poin Kualitas", "Poin Kupedes",
        "Avg Mantri Poin", "Total Poin Unit", "Kategori"
    ]
    
    st.dataframe(display_df, use_container_width=True, hide_index=True)

    # Chart Total Poin Unit
    fig = px.bar(
        unit_data.sort_values("Poin Unit"),
        x="Poin Unit",
        y="Unit",
        orientation="h",
        text_auto=".1f",
        color="Poin Unit",
        color_continuous_scale="Blues",
        title="Total Performance Point per Racing Unit"
    )
    fig.update_layout(
        plot_bgcolor="white",
        paper_bgcolor="white",
        xaxis=dict(range=[0, 105]),
        showlegend=False,
        height=500
    )
    st.plotly_chart(fig, use_container_width=True)

    # Breakdown chart
    st.subheader("📊 Rincian Komponen Poin Kinerja Unit")
    
    breakdown_all = unit_data[[
        "Unit", "Poin Growth OS", "Poin Quality Unit", "Poin Kupedes"
    ]].sort_values("Poin Growth OS", ascending=True)
    
    fig_breakdown = px.bar(
        breakdown_all,
        x=["Poin Growth OS", "Poin Quality Unit", "Poin Kupedes"],
        y="Unit",
        orientation="h",
        title="Breakdown Komponen Poin Kinerja Unit (Growth OS + Kualitas + Kupedes)",
        barmode="stack"
    )
    fig_breakdown.update_layout(
        plot_bgcolor="white",
        paper_bgcolor="white",
        height=500
    )
    st.plotly_chart(fig_breakdown, use_container_width=True)

    # Kontribusi Mantri vs Kinerja Unit
    st.subheader("📈 Komposisi Poin Unit (70% Mantri + 30% Kinerja)")
    
    composition_data = unit_data[[
        "Unit", "Rata-rata Poin Mantri", "Poin Kinerja Normalized"
    ]].copy()
    composition_data["Kontribusi Mantri (70%)"] = (composition_data["Rata-rata Poin Mantri"] / 100) * 70
    composition_data["Kontribusi Kinerja (30%)"] = (composition_data["Poin Kinerja Normalized"] / 100) * 30
    composition_data = composition_data[["Unit", "Kontribusi Mantri (70%)", "Kontribusi Kinerja (30%)"]].sort_values("Kontribusi Mantri (70%)")
    
    fig_comp = px.bar(
        composition_data,
        x=["Kontribusi Mantri (70%)", "Kontribusi Kinerja (30%)"],
        y="Unit",
        orientation="h",
        barmode="stack",
        title="Komposisi Poin Unit: Kontribusi Mantri vs Kinerja Unit"
    )
    fig_comp.update_layout(
        plot_bgcolor="white",
        paper_bgcolor="white",
        height=500
    )
    st.plotly_chart(fig_comp, use_container_width=True)

# ==========================
# LEADERBOARD MANTRI
# ==========================
elif st.session_state.page == "Leaderboard Mantri":

    st.header("👨‍💼 Leaderboard Mantri - Berbasis Performance Point")

    display_mantri = mantri_data[[
        "Nama", "Unit", "Realisasi (%)", "Quality (%)",
        "Poin Realisasi", "Poin Quality", "Total Poin"
    ]].copy()
    
    display_mantri = display_mantri.sort_values("Total Poin", ascending=False)
    display_mantri.insert(0, "Rank", range(1, len(display_mantri) + 1))
    
    display_mantri["Rank"] = display_mantri["Rank"].astype(int)
    display_mantri["Poin Realisasi"] = display_mantri["Poin Realisasi"].astype(int)
    display_mantri["Poin Quality"] = display_mantri["Poin Quality"].astype(int)
    display_mantri["Total Poin"] = display_mantri["Total Poin"].astype(int)
    
    display_mantri.columns = [
        "#", "Nama", "Unit", "Realisasi %", "Quality %",
        "Poin Realisasi", "Poin Quality", "Total Poin"
    ]
    
    st.dataframe(display_mantri, use_container_width=True, hide_index=True)

    # Chart Total Poin Mantri
    mantri_sorted = mantri_data.sort_values("Total Poin")
    fig = px.bar(
        mantri_sorted,
        x="Total Poin",
        y="Nama",
        orientation="h",
        text="Total Poin",
        color="Total Poin",
        color_continuous_scale="Reds",
        title="Total Performance Point per Mantri"
    )
    fig.update_traces(text=[f"{int(x)}" for x in mantri_sorted["Total Poin"]])
    fig.update_layout(
        plot_bgcolor="white",
        paper_bgcolor="white",
        xaxis=dict(range=[0, 100]),
        showlegend=False,
        height=400
    )
    st.plotly_chart(fig, use_container_width=True)

    # Breakdown Mantri
    st.subheader("📊 Breakdown Poin per Mantri")
    
    breakdown_mantri = mantri_data[[
        "Nama", "Poin Realisasi", "Poin Quality"
    ]].sort_values("Poin Realisasi")
    
    fig_breakdown_mantri = px.bar(
        breakdown_mantri,
        x=["Poin Realisasi", "Poin Quality"],
        y="Nama",
        orientation="h",
        barmode="stack",
        title="Breakdown Poin Mantri: Realisasi + Kualitas"
    )
    fig_breakdown_mantri.update_layout(
        plot_bgcolor="white",
        paper_bgcolor="white",
        height=400
    )
    st.plotly_chart(fig_breakdown_mantri, use_container_width=True)

# ==========================
# BREAKDOWN POIN
# ==========================
elif st.session_state.page == "Breakdown Poin":

    st.header("📊 Breakdown Poin - Rincian Perhitungan")
    
    tab1, tab2, tab3 = st.tabs(["📋 Tabel Penilaian Mantri", "📊 Tabel Penilaian Unit", "🧮 Kalkulasi Detail"])
    
    with tab1:
        st.subheader("👨‍💼 Penilaian Mantri (Total 100 Poin)")
        
        st.markdown("### 1. Realisasi Keseluruhan (50 Poin)")
        realisasi_table = pd.DataFrame({
            "Achievement Realisasi": ["≥ 120%", "110% – 119,99%", "100% – 109,99%", "90% – 99,99%", "< 90%"],
            "Poin": [50, 45, 40, 30, 15]
        })
        st.dataframe(realisasi_table, use_container_width=True, hide_index=True)

        st.markdown("### 2. Perbaikan Kualitas Portofolio (50 Poin)")
        quality_table = pd.DataFrame({
            "Kondisi": ["Sangat Baik (≤ -8%)", "Baik (≤ -5%)", "Stabil (≤ -2%)", "Sedikit Memburuk (≤ 2%)", "Memburuk (> 2%)"],
            "Poin": [50, 40, 30, 15, 0]
        })
        st.dataframe(quality_table, use_container_width=True, hide_index=True)

        st.markdown("### 📊 Total Poin Mantri")
        total_mantri_table = pd.DataFrame({
            "Indikator": ["🚀 Realisasi Keseluruhan", "🛡️ Perbaikan Kualitas Portofolio"],
            "Maksimum Poin": [50, 50],
            "Tujuan": [
                "Mendorong pencapaian target bisnis secara optimal.",
                "Mendorong pengelolaan kredit yang sehat dan meminimalkan pembentukan kredit bermasalah."
            ]
        })
        total_row_m = pd.DataFrame({
            "Indikator": ["TOTAL"],
            "Maksimum Poin": [100],
            "Tujuan": [""]
        })
        st.dataframe(pd.concat([total_mantri_table, total_row_m], ignore_index=True), use_container_width=True, hide_index=True)

    with tab2:
        st.subheader("🏢 Penilaian Unit (Poin Kinerja Unit = 100 Poin)")
        
        st.markdown("### Komponen Poin Kinerja Unit")
        
        st.markdown("#### 1. Pertumbuhan Outstanding (OS) Unit (40 Poin)")
        os_table = pd.DataFrame({
            "Growth OS Unit": ["≥ 15%", "12% – 14,99%", "10% – 11,99%", "7% – 9,99%", "< 7%"],
            "Poin": [40, 34, 28, 20, 10]
        })
        st.dataframe(os_table, use_container_width=True, hide_index=True)

        st.markdown("#### 2. Perbaikan Kualitas Unit (35 Poin)")
        unit_quality_table = pd.DataFrame({
            "Kondisi Kualitas": ["Sangat Baik (≥ 8%)", "Baik (5% – 7,99%)", "Stabil (2% – 4,99%)", "Sedikit Memburuk (-2% – 1,99%)", "Memburuk (< -2%)"],
            "Poin": [35, 28, 20, 10, 0]
        })
        st.dataframe(unit_quality_table, use_container_width=True, hide_index=True)

        st.markdown("#### 3. Growth Kupedes (25 Poin)")
        kupedes_table = pd.DataFrame({
            "Growth Kupedes": ["≥ 5%", "3% – 4,99%", "1% – 2,99%", "0% – 0,99%", "Negatif"],
            "Poin": [25, 20, 15, 10, 0]
        })
        st.dataframe(kupedes_table, use_container_width=True, hide_index=True)

        st.markdown("### 📊 Total Poin Kinerja Unit")
        total_unit_table = pd.DataFrame({
            "Indikator": ["📈 Pertumbuhan Outstanding (OS)", "🛡️ Perbaikan Kualitas Unit", "📊 Growth Kupedes"],
            "Maksimum Poin": [40, 35, 25],
            "Tujuan": [
                "Mendorong pertumbuhan portofolio unit.",
                "Menjaga dan memperbaiki kualitas klaster unit.",
                "Meningkatkan kontribusi portofolio Kupedes terhadap total portofolio mikro."
            ]
        })
        total_row_u = pd.DataFrame({
            "Indikator": ["TOTAL KINERJA UNIT"],
            "Maksimum Poin": [100],
            "Tujuan": [""]
        })
        st.dataframe(pd.concat([total_unit_table, total_row_u], ignore_index=True), use_container_width=True, hide_index=True)

        st.markdown("### 🏆 Formula Poin Unit")
        st.info("""
**Poin Unit = (70% × Rata-rata Poin Mantri) + (30% × Poin Kinerja Unit)**

- **70% Rata-rata Poin Mantri**: Kontribusi performa individual Mantri dalam unit
- **30% Poin Kinerja Unit**: Kontribusi kinerja unit secara kolektif (Growth OS + Kualitas + Kupedes)
        """)

        st.markdown("### 🏆 Kategori Racing Unit Berdasarkan Poin Unit")
        category_table = pd.DataFrame({
            "Total Poin Unit": ["≥ 90", "80 – 89", "70 – 79", "60 – 69", "< 60"],
            "Kategori": ["🏆 Elite Racing Unit", "🥇 Champion Racing Unit", "🥈 Prime Racing Unit", "🥉 Rising Racing Unit", "📈 Growth Racing Unit"]
        })
        st.dataframe(category_table, use_container_width=True, hide_index=True)

    with tab3:
        st.subheader("🧮 Kalkulasi Detail Unit Anda")
        
        unit_anda = unit_data[unit_data["Unit"] == "⭐ Unit Anda"].iloc[0]
        
        # Kalkulasi Mantri
        st.markdown("### 📊 Kontribusi Mantri Unit Anda (70%)")
        
        unit_anda_name = unit_anda["Unit"]
        mantri_unit_anda = mantri_data[mantri_data["Unit"] == unit_anda_name]
        
        if len(mantri_unit_anda) > 0:
            col1, col2 = st.columns(2)
            
            with col1:
                for idx, row in mantri_unit_anda.iterrows():
                    st.markdown(f"**{row['Nama']}**")
                    st.caption(f"Realisasi: {row['Realisasi (%)']:.1f}% → {int(row['Poin Realisasi'])}/50 poin")
                    st.caption(f"Kualitas: {row['Quality (%)']:.1f}% → {int(row['Poin Quality'])}/50 poin")
                    st.metric("Total", f"{int(row['Total Poin'])} poin")
                    st.divider()
            
            with col2:
                st.info(f"""
**Rata-rata Poin Mantri: {unit_anda['Rata-rata Poin Mantri']:.1f} / 100**

Kontribusi ke Poin Unit:
{unit_anda['Rata-rata Poin Mantri']:.1f} × 70% = **{(unit_anda['Rata-rata Poin Mantri'] / 100) * 70:.1f}**
                """)
        
        st.divider()
        
        # Kalkulasi Kinerja Unit
        st.markdown("### 📈 Komponen Kinerja Unit Anda (30%)")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("Growth OS", f"{unit_anda['Growth OS (%)']:.1f}%")
            st.caption(f"Poin: **{int(unit_anda['Poin Growth OS'])} / 40**")
            
            st.metric("Kualitas Unit", f"{unit_anda['Quality Unit (%)']:.1f}%")
            st.caption(f"Poin: **{int(unit_anda['Poin Quality Unit'])} / 35**")
            
            st.metric("Growth Kupedes", f"{unit_anda['Growth Kupedes (%)']:.1f}%")
            st.caption(f"Poin: **{int(unit_anda['Poin Kupedes'])} / 25**")
        
        with col2:
            st.info(f"""
**Total Poin Kinerja: {int(unit_anda['Total Poin Kinerja'])} / 100**

Normalized: {unit_anda['Poin Kinerja Normalized']:.1f}

Kontribusi ke Poin Unit:
{unit_anda['Poin Kinerja Normalized']:.1f} × 30% = **{(unit_anda['Poin Kinerja Normalized'] / 100) * 30:.1f}**
            """)
        
        st.divider()
        
        # Total Poin Unit
        st.markdown("### 🏆 Total Poin Unit Anda")
        
        kontribusi_mantri = (unit_anda['Rata-rata Poin Mantri'] / 100) * 70
        kontribusi_kinerja = (unit_anda['Poin Kinerja Normalized'] / 100) * 30
        
        st.success(f"""
**Kalkulasi:**

({unit_anda['Rata-rata Poin Mantri']:.1f} ÷ 100) × 70 = {kontribusi_mantri:.1f}
+ ({unit_anda['Poin Kinerja Normalized']:.1f} ÷ 100) × 30 = {kontribusi_kinerja:.1f}

**= {unit_anda['Poin Unit']:.1f} / 100 Poin**

**Kategori: {unit_anda['Kategori']}**
        """)

# ==========================
# TOP PERFORMER
# ==========================
elif st.session_state.page == "Top Performer":

    st.header("🔥 Top Performer - Bulan Juni 2026")

    # Top Racing Unit
    st.subheader("🏆 Top Racing Unit")
    
    top_unit_display = unit_data.head(3)[["Rank", "Unit", "Poin Unit", "Kategori"]].copy()
    top_unit_display["Rank"] = top_unit_display["Rank"].astype(int)
    top_unit_display["Poin Unit"] = top_unit_display["Poin Unit"].round(1)
    top_unit_display.columns = ["#", "Racing Unit", "Performance Poin", "Kategori"]
    
    st.dataframe(top_unit_display, use_container_width=True, hide_index=True)

    col1, col2, col3 = st.columns(3)
    
    top_units = unit_data.head(3)
    
    with col1:
        top1 = top_units.iloc[0]
        st.success(f"""
**🥇 Rank 1**

{top1['Unit']}

**{top1['Poin Unit']:.1f} / 100 Poin**

{top1['Kategori']}
        """)
    
    with col2:
        top2 = top_units.iloc[1]
        st.info(f"""
**🥈 Rank 2**

{top2['Unit']}

**{top2['Poin Unit']:.1f} / 100 Poin**

{top2['Kategori']}
        """)
    
    with col3:
        top3 = top_units.iloc[2]
        st.warning(f"""
**🥉 Rank 3**

{top3['Unit']}

**{top3['Poin Unit']:.1f} / 100 Poin**

{top3['Kategori']}
        """)

    st.divider()

    # Top Mantri
    st.subheader("🔥 Top Mantri")
    
    top_mantri_display = mantri_data.sort_values("Total Poin", ascending=False).head(3)
    top_mantri_display = top_mantri_display.reset_index(drop=True)
    top_mantri_display.insert(0, "Rank", range(1, len(top_mantri_display) + 1))
    top_mantri_display["Rank"] = top_mantri_display["Rank"].astype(int)
    top_mantri_display["Total Poin"] = top_mantri_display["Total Poin"].astype(int)
    top_mantri_display = top_mantri_display[["Rank", "Nama", "Unit", "Total Poin"]]
    top_mantri_display.columns = ["#", "Nama", "Unit", "Performance Poin"]
    
    st.dataframe(top_mantri_display, use_container_width=True, hide_index=True)

    col1, col2, col3 = st.columns(3)
    
    top_mantris = mantri_data.sort_values("Total Poin", ascending=False)
    
    with col1:
        top1_m = top_mantris.iloc[0]
        st.success(f"""
**🥇 {top1_m['Nama']}**

Unit: {top1_m['Unit']}

**{int(top1_m['Total Poin'])} / 100 Poin**
        """)
    
    with col2:
        top2_m = top_mantris.iloc[1]
        st.info(f"""
**🥈 {top2_m['Nama']}**

Unit: {top2_m['Unit']}

**{int(top2_m['Total Poin'])} / 100 Poin**
        """)
    
    with col3:
        top3_m = top_mantris.iloc[2]
        st.warning(f"""
**🥉 {top3_m['Nama']}**

Unit: {top3_m['Unit']}

**{int(top3_m['Total Poin'])} / 100 Poin**
        """)

# ==========================
# FOOTER
# ==========================
st.markdown("---")
st.markdown(
    "<div style='background:#00529C;color:white;padding:10px;border-radius:10px;text-align:center'>"
    "<b>Racing Unit Dashboard</b><br>"
    "Performance Monitoring & Leaderboard (Point-Based System)<br>"
    "<small>Mantri: Realisasi (50) + Kualitas (50) | Unit: (70% Mantri) + (30% Kinerja Unit: OS 40 + Kualitas 35 + Kupedes 25)</small>"
    "</div>",
    unsafe_allow_html=True
)
