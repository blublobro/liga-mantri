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
# FUNGSI PERHITUNGAN POIN
# ==========================

def get_realisasi_poin(realisasi_pct):
    """Hitung poin berdasarkan persentase realisasi (Maks. 25 Poin)"""
    if realisasi_pct >= 120:
        return 25
    elif realisasi_pct >= 110:
        return 22
    elif realisasi_pct >= 100:
        return 19
    elif realisasi_pct >= 95:
        return 16
    elif realisasi_pct >= 90:
        return 12
    else:
        return 6

def get_growth_os_poin(growth_pct):
    """Hitung poin berdasarkan pertumbuhan Outstanding (Maks. 25 Poin)"""
    if growth_pct >= 15:
        return 25
    elif growth_pct >= 12:
        return 22
    elif growth_pct >= 10:
        return 19
    elif growth_pct >= 7:
        return 15
    elif growth_pct >= 5:
        return 10
    else:
        return 5

def get_growth_kupedes_poin(growth_kupedes_pct):
    """Hitung poin berdasarkan pertumbuhan rasio Kupedes (Maks. 15 Poin)"""
    if growth_kupedes_pct >= 15:
        return 15
    elif growth_kupedes_pct >= 12:
        return 13
    elif growth_kupedes_pct >= 10:
        return 11
    elif growth_kupedes_pct >= 7:
        return 8
    elif growth_kupedes_pct >= 5:
        return 5
    else:
        return 2

def get_quality_poin(quality_type, value):
    """
    Hitung poin perbaikan kualitas (Maks. 20 Poin)
    quality_type: 'improvement' atau 'sml'
    """
    if quality_type == 'improvement':
        if value > 10:
            return 20
        elif value >= 5:
            return 16
        elif value == 0:
            return 12
        elif value < 0 and value >= -5:
            return 8
        else:
            return 0
    elif quality_type == 'sml':
        if value == 0:  # Tidak ada SML baru
            return 16
        else:
            return 0

def get_akuisisi_poin(akuisisi_pct):
    """Hitung poin berdasarkan akuisisi nasabah (Maks. 15 Poin)"""
    if akuisisi_pct >= 120:
        return 15
    elif akuisisi_pct >= 110:
        return 13
    elif akuisisi_pct >= 100:
        return 11
    elif akuisisi_pct >= 90:
        return 8
    else:
        return 4

def get_category(total_poin):
    """Tentukan kategori unit berdasarkan total poin"""
    if total_poin >= 90:
        return "🏆 Elite Racing Unit"
    elif total_poin >= 80:
        return "🥇 Champion Racing Unit"
    elif total_poin >= 70:
        return "🥈 Prime Racing Unit"
    elif total_poin >= 60:
        return "🥉 Rising Racing Unit"
    else:
        return "📈 Growth Racing Unit"

# ==========================
# DATA PERFORMA UNIT
# ==========================

# Data dengan nilai aktual untuk perhitungan poin
unit_data = pd.DataFrame({
    "Rank": [1, 2, 3, 4, 5],
    "Unit": [
        "Purwokerto Timur",
        "Sokaraja",
        "Ajibarang",
        "⭐ Unit Anda",
        "Cilongok"
    ],
    "Realisasi (%)": [115, 105, 108, 98, 92],
    "Growth OS (%)": [14, 16, 13, 11, 8],
    "Growth Kupedes (%)": [12, 10, 11, 9, 6],
    "Quality Improvement (%)": [12, 8, 6, 4, -2],
    "Akuisisi (%)": [125, 115, 105, 100, 85],
    "Rank Change": [2, 1, 3, 2, -1]
})

# Hitung poin untuk setiap unit
unit_data["Poin Realisasi"] = unit_data["Realisasi (%)"].apply(get_realisasi_poin)
unit_data["Poin Growth OS"] = unit_data["Growth OS (%)"].apply(get_growth_os_poin)
unit_data["Poin Growth Kupedes"] = unit_data["Growth Kupedes (%)"].apply(get_growth_kupedes_poin)
unit_data["Poin Quality"] = unit_data["Quality Improvement (%)"].apply(
    lambda x: get_quality_poin('improvement', x)
)
unit_data["Poin Akuisisi"] = unit_data["Akuisisi (%)"].apply(get_akuisisi_poin)
unit_data["Total Poin"] = (
    unit_data["Poin Realisasi"] +
    unit_data["Poin Growth OS"] +
    unit_data["Poin Growth Kupedes"] +
    unit_data["Poin Quality"] +
    unit_data["Poin Akuisisi"]
)
unit_data["Kategori"] = unit_data["Total Poin"].apply(get_category)

# Sort berdasarkan total poin
unit_data = unit_data.sort_values("Total Poin", ascending=False).reset_index(drop=True)
unit_data["Rank"] = range(1, len(unit_data) + 1)

# Data untuk Mantri
mantri_data = pd.DataFrame({
    "Nama": ["Andi", "Budi", "Citra", "Dedi", "Eko"],
    "Unit": ["Purwokerto Timur", "Purwokerto Timur", "Sokaraja", "Ajibarang", "Cilongok"],
    "Realisasi (%)": [118, 110, 105, 98, 92],
    "Growth OS (%)": [15, 13, 14, 10, 7],
    "Growth Kupedes (%)": [13, 11, 12, 8, 5],
    "Quality (%)": [14, 10, 8, 5, 2],
    "Akuisisi (%)": [128, 120, 112, 98, 85]
})

mantri_data["Poin Realisasi"] = mantri_data["Realisasi (%)"].apply(get_realisasi_poin)
mantri_data["Poin Growth OS"] = mantri_data["Growth OS (%)"].apply(get_growth_os_poin)
mantri_data["Poin Growth Kupedes"] = mantri_data["Growth Kupedes (%)"].apply(get_growth_kupedes_poin)
mantri_data["Poin Quality"] = mantri_data["Quality (%)"].apply(
    lambda x: get_quality_poin('improvement', x)
)
mantri_data["Poin Akuisisi"] = mantri_data["Akuisisi (%)"].apply(get_akuisisi_poin)
mantri_data["Total Poin"] = (
    mantri_data["Poin Realisasi"] +
    mantri_data["Poin Growth OS"] +
    mantri_data["Poin Growth Kupedes"] +
    mantri_data["Poin Quality"] +
    mantri_data["Poin Akuisisi"]
)
mantri_data["Rank"] = range(1, len(mantri_data) + 1)

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
        "<h1 style='color:#00529C;margin-bottom:0'>Liga <span style='color:#F37021'>Mantri</span></h1>"
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
        st.metric("💯 Performance", f"{int(unit_anda['Total Poin'])} Poin", f"/ 100")
    with k3:
        st.metric("💰 Outstanding", "Rp18,2 G", f"+{unit_anda['Growth OS (%)']:.1f}%")
    with k4:
        st.metric("🎯 Realisasi", f"{unit_anda['Realisasi (%)']:.1f}%")
    with k5:
        st.metric("📈 Kategori", unit_anda['Kategori'])

    st.divider()

    # Section 1: Leaderboard Racing Unit vs Trend Ranking
    c1, c2 = st.columns([2, 1])

    with c1:
        st.subheader("🏅 Leaderboard Racing Unit (Berbasis Poin)")
        
        leaderboard_display = unit_data[["Rank", "Unit", "Total Poin", "Kategori"]].copy()
        leaderboard_display.columns = ["#", "Racing Unit", "Performance Poin", "Kategori"]
        leaderboard_display["#"] = leaderboard_display["#"].astype(int)
        leaderboard_display["Performance Poin"] = leaderboard_display["Performance Poin"].astype(int)
        
        st.dataframe(leaderboard_display, use_container_width=True, hide_index=True)
        
        # Visualisasi bar chart
        fig = px.bar(
            unit_data.sort_values("Total Poin"),
            x="Total Poin",
            y="Unit",
            orientation="h",
            text="Total Poin",
            title="Total Performance Point per Racing Unit"
        )
        fig.update_traces(marker_color="#00529C", text=[f"{int(x)}" for x in unit_data.sort_values("Total Poin")["Total Poin"]])
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
            "Indikator": ["Realisasi", "Growth OS", "Growth Kupedes", "Quality", "Akuisisi"],
            "Poin": [
                int(unit_anda["Poin Realisasi"]),
                int(unit_anda["Poin Growth OS"]),
                int(unit_anda["Poin Growth Kupedes"]),
                int(unit_anda["Poin Quality"]),
                int(unit_anda["Poin Akuisisi"])
            ],
            "Maksimal": [25, 25, 15, 20, 15]
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
**Total: {int(unit_anda['Total Poin'])} / 100 Poin**

Target Top 3: +{int(max(0, 70 - unit_anda['Total Poin']))} poin
        """)

    st.divider()

    # Section 2: Kontribusi Mantri & Top Performer
    a, b = st.columns([2, 1])

    with a:
        st.subheader("👨‍💼 Top Mantri di Unit Anda")
        
        top_mantri = mantri_data.sort_values("Total Poin", ascending=False).head(3)
        
        fig3 = px.bar(
            top_mantri.sort_values("Total Poin"),
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

    with b:
        st.subheader("🔥 Top Performer")
        top_mantri_sorted = mantri_data.sort_values("Total Poin", ascending=False)
        
        for idx, row in top_mantri_sorted.head(3).iterrows():
            medals = ["🥇", "🥈", "🥉"]
            st.metric(
                f"{medals[idx]} {row['Nama']}",
                f"{int(row['Total Poin'])} Poin",
                f"({row['Unit']})"
            )

    st.divider()

    # Insight
    st.info(f"""
**📊 Insight Bulan Ini**

- ✅ Unit Anda berada di peringkat {int(unit_anda['Rank'])} dari 23.
- {'📈' if unit_anda['Rank Change'] > 0 else '📉'} Naik {abs(int(unit_anda['Rank Change']))} peringkat dibanding bulan lalu.
- 🎯 Performance: {int(unit_anda['Total Poin'])} / 100 Poin ({unit_anda['Kategori']})
- 🚀 Realisasi: {unit_anda['Realisasi (%)']:.1f}% ({int(unit_anda['Poin Realisasi'])}/25 Poin)
- 💰 Growth OS: {unit_anda['Growth OS (%)']:.1f}% ({int(unit_anda['Poin Growth OS'])}/25 Poin)
- 📊 Growth Kupedes: {unit_anda['Growth Kupedes (%)']:.1f}% ({int(unit_anda['Poin Growth Kupedes'])}/15 Poin)
- 🛡️ Quality: +{unit_anda['Quality Improvement (%)']:.1f}% ({int(unit_anda['Poin Quality'])}/20 Poin)
- 👥 Akuisisi: {unit_anda['Akuisisi (%)']:.1f}% ({int(unit_anda['Poin Akuisisi'])}/15 Poin)
- 🏆 **Dibutuhkan {int(max(0, top_unit['Total Poin'] - unit_anda['Total Poin']))} poin lagi untuk masuk ranking 1.**
    """)

# ==========================
# LEADERBOARD RACING UNIT
# ==========================
elif st.session_state.page == "Leaderboard Racing Unit":

    st.header("🏅 Leaderboard Racing Unit - Berbasis Performance Point")
    
    display_df = unit_data[[
        "Rank", "Unit", "Realisasi (%)", "Growth OS (%)", "Growth Kupedes (%)",
        "Poin Realisasi", "Poin Growth OS", "Poin Growth Kupedes", "Poin Quality", 
        "Poin Akuisisi", "Total Poin", "Kategori"
    ]].copy()
    
    display_df["Rank"] = display_df["Rank"].astype(int)
    display_df["Poin Realisasi"] = display_df["Poin Realisasi"].astype(int)
    display_df["Poin Growth OS"] = display_df["Poin Growth OS"].astype(int)
    display_df["Poin Growth Kupedes"] = display_df["Poin Growth Kupedes"].astype(int)
    display_df["Poin Quality"] = display_df["Poin Quality"].astype(int)
    display_df["Poin Akuisisi"] = display_df["Poin Akuisisi"].astype(int)
    display_df["Total Poin"] = display_df["Total Poin"].astype(int)
    
    display_df.columns = [
        "#", "Racing Unit", "Realisasi %", "Growth OS %", "Growth Kupedes %",
        "Poin Real.", "Poin OS", "Poin Kupedes", "Poin Quality", "Poin Akuisisi",
        "Total Poin", "Kategori"
    ]
    
    st.dataframe(display_df, use_container_width=True, hide_index=True)

    # Chart Total Poin
    fig = px.bar(
        unit_data.sort_values("Total Poin"),
        x="Total Poin",
        y="Unit",
        orientation="h",
        text="Total Poin",
        color="Total Poin",
        color_continuous_scale="Blues",
        title="Total Performance Point per Racing Unit"
    )
    fig.update_traces(text=[f"{int(x)}" for x in unit_data.sort_values("Total Poin")["Total Poin"]])
    fig.update_layout(
        plot_bgcolor="white",
        paper_bgcolor="white",
        xaxis=dict(range=[0, 105]),
        showlegend=False,
        height=500
    )
    st.plotly_chart(fig, use_container_width=True)

    # Breakdown chart
    st.subheader("📊 Rincian Poin per Kategori")
    
    breakdown_all = unit_data[[
        "Unit", "Poin Realisasi", "Poin Growth OS", "Poin Growth Kupedes", "Poin Quality", "Poin Akuisisi"
    ]].sort_values("Poin Realisasi", ascending=True)
    
    fig_breakdown = px.bar(
        breakdown_all,
        x=["Poin Realisasi", "Poin Growth OS", "Poin Growth Kupedes", "Poin Quality", "Poin Akuisisi"],
        y="Unit",
        orientation="h",
        title="Breakdown Poin per Kategori Indikator",
        barmode="stack"
    )
    fig_breakdown.update_layout(
        plot_bgcolor="white",
        paper_bgcolor="white",
        height=500
    )
    st.plotly_chart(fig_breakdown, use_container_width=True)

# ==========================
# LEADERBOARD MANTRI
# ==========================
elif st.session_state.page == "Leaderboard Mantri":

    st.header("👨‍💼 Leaderboard Mantri - Berbasis Performance Point")

    display_mantri = mantri_data[[
        "Nama", "Unit", "Realisasi (%)", "Growth OS (%)", "Growth Kupedes (%)",
        "Poin Realisasi", "Poin Growth OS", "Poin Growth Kupedes", "Poin Quality", 
        "Poin Akuisisi", "Total Poin"
    ]].copy()
    
    display_mantri = display_mantri.sort_values("Total Poin", ascending=False)
    display_mantri.insert(0, "Rank", range(1, len(display_mantri) + 1))
    
    display_mantri["Rank"] = display_mantri["Rank"].astype(int)
    display_mantri["Poin Realisasi"] = display_mantri["Poin Realisasi"].astype(int)
    display_mantri["Poin Growth OS"] = display_mantri["Poin Growth OS"].astype(int)
    display_mantri["Poin Growth Kupedes"] = display_mantri["Poin Growth Kupedes"].astype(int)
    display_mantri["Poin Quality"] = display_mantri["Poin Quality"].astype(int)
    display_mantri["Poin Akuisisi"] = display_mantri["Poin Akuisisi"].astype(int)
    display_mantri["Total Poin"] = display_mantri["Total Poin"].astype(int)
    
    display_mantri.columns = [
        "#", "Nama", "Unit", "Realisasi %", "Growth OS %", "Growth Kupedes %",
        "Poin Real.", "Poin OS", "Poin Kupedes", "Poin Quality", "Poin Akuisisi", "Total Poin"
    ]
    
    st.dataframe(display_mantri, use_container_width=True, hide_index=True)

    # Chart
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

# ==========================
# BREAKDOWN POIN
# ==========================
elif st.session_state.page == "Breakdown Poin":

    st.header("📊 Breakdown Poin - Rincian Perhitungan")
    
    tab1, tab2 = st.tabs(["📋 Tabel Penilaian", "🧮 Kalkulasi Detail"])
    
    with tab1:
        st.subheader("🚀 Realisasi Keseluruhan (Maks. 25 Poin)")
        realisasi_table = pd.DataFrame({
            "Pencapaian": ["≥ 120%", "110% – 119,99%", "100% – 109,99%", "95% – 99,99%", "90% – 94,99%", "< 90%"],
            "Poin": [25, 22, 19, 16, 12, 6]
        })
        st.dataframe(realisasi_table, use_container_width=True, hide_index=True)

        st.subheader("💰 Pertumbuhan Outstanding (Maks. 25 Poin)")
        growth_table = pd.DataFrame({
            "Growth OS": ["≥ 15%", "12% – 14,99%", "10% – 11,99%", "7% – 9,99%", "5% – 6,99%", "< 5%"],
            "Poin": [25, 22, 19, 15, 10, 5]
        })
        st.dataframe(growth_table, use_container_width=True, hide_index=True)

        st.subheader("📊 Pertumbuhan Rasio Kupedes (Maks. 15 Poin)")
        kupedes_table = pd.DataFrame({
            "Growth Kupedes": ["≥ 15%", "12% – 14,99%", "10% – 11,99%", "7% – 9,99%", "5% – 6,99%", "< 5%"],
            "Poin": [15, 13, 11, 8, 5, 2]
        })
        st.dataframe(kupedes_table, use_container_width=True, hide_index=True)

        st.subheader("🛡️ Perbaikan Kualitas Portofolio (Maks. 20 Poin)")
        quality_table = pd.DataFrame({
            "Perbaikan Kualitas": [
                "Sangat Baik (perbaikan > 10%)",
                "Baik (5% – 10%)",
                "Stabil (0%)",
                "Sedikit Menurun (-5% – 0%)",
                "Memburuk (< -5%)"
            ],
            "Poin": [20, 16, 12, 8, 0]
        })
        st.dataframe(quality_table, use_container_width=True, hide_index=True)

        st.subheader("👥 Akuisisi Nasabah Baru (Maks. 15 Poin)")
        akuisisi_table = pd.DataFrame({
            "Achievement Akuisisi": ["≥ 120%", "110% – 119,99%", "100% – 109,99%", "90% – 99,99%", "< 90%"],
            "Poin": [15, 13, 11, 8, 4]
        })
        st.dataframe(akuisisi_table, use_container_width=True, hide_index=True)

        st.subheader("📊 Total Performance Point")
        total_table = pd.DataFrame({
            "Indikator": ["🚀 Realisasi Keseluruhan", "💰 Pertumbuhan OS", "📊 Pertumbuhan Rasio Kupedes", "🛡️ Perbaikan Kualitas Portofolio", "👥 Akuisisi Nasabah Baru"],
            "Maksimum Poin": [25, 25, 15, 20, 15],
            "Tujuan": [
                "Menjaga pencapaian target bisnis secara umum.",
                "Mendorong pertumbuhan portofolio yang berkelanjutan.",
                "Meningkatkan kontribusi Kupedes terhadap total portofolio.",
                "Menjaga dan memperbaiki kualitas kredit serta mengendalikan SML/NPL.",
                "Memperluas basis nasabah dan menciptakan sumber pertumbuhan baru."
            ]
        })
        total_row = pd.DataFrame({
            "Indikator": ["TOTAL"],
            "Maksimum Poin": [100],
            "Tujuan": [""]
        })
        st.dataframe(pd.concat([total_table, total_row], ignore_index=True), use_container_width=True, hide_index=True)

        st.divider()
        st.subheader("🏆 Kategori Racing Unit Berdasarkan Poin")
        category_table = pd.DataFrame({
            "Total Poin": ["≥ 90", "80 – 89", "70 – 79", "60 – 69", "< 60"],
            "Kategori": ["🏆 Elite Racing Unit", "🥇 Champion Racing Unit", "🥈 Prime Racing Unit", "🥉 Rising Racing Unit", "📈 Growth Racing Unit"]
        })
        st.dataframe(category_table, use_container_width=True, hide_index=True)

    with tab2:
        st.subheader("🧮 Kalkulasi Detail Unit Anda")
        
        unit_anda = unit_data[unit_data["Unit"] == "⭐ Unit Anda"].iloc[0]
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("🚀 Realisasi", f"{unit_anda['Realisasi (%)']:.1f}%")
            st.caption(f"Poin: **{int(unit_anda['Poin Realisasi'])} / 25**")
            
            st.metric("💰 Growth OS", f"{unit_anda['Growth OS (%)']:.1f}%")
            st.caption(f"Poin: **{int(unit_anda['Poin Growth OS'])} / 25**")
            
            st.metric("📊 Growth Kupedes", f"{unit_anda['Growth Kupedes (%)']:.1f}%")
            st.caption(f"Poin: **{int(unit_anda['Poin Growth Kupedes'])} / 15**")
        
        with col2:
            st.metric("🛡️ Quality", f"+{unit_anda['Quality Improvement (%)']:.1f}%")
            st.caption(f"Poin: **{int(unit_anda['Poin Quality'])} / 20**")
            
            st.metric("👥 Akuisisi", f"{unit_anda['Akuisisi (%)']:.1f}%")
            st.caption(f"Poin: **{int(unit_anda['Poin Akuisisi'])} / 15**")
        
        st.divider()
        
        st.success(f"""
**Total Performance Point Unit Anda:**

{int(unit_anda['Poin Realisasi'])} + {int(unit_anda['Poin Growth OS'])} + {int(unit_anda['Poin Growth Kupedes'])} + {int(unit_anda['Poin Quality'])} + {int(unit_anda['Poin Akuisisi'])} = **{int(unit_anda['Total Poin'])} / 100 Poin**

Kategori: **{unit_anda['Kategori']}**
        """)

# ==========================
# TOP PERFORMER
# ==========================
elif st.session_state.page == "Top Performer":

    st.header("🔥 Top Performer - Bulan Juni 2026")

    # Top Racing Unit
    st.subheader("🏆 Top Racing Unit")
    
    top_unit_display = unit_data.head(3)[["Rank", "Unit", "Total Poin", "Kategori"]].copy()
    top_unit_display["Rank"] = top_unit_display["Rank"].astype(int)
    top_unit_display["Total Poin"] = top_unit_display["Total Poin"].astype(int)
    top_unit_display.columns = ["#", "Racing Unit", "Performance Poin", "Kategori"]
    
    st.dataframe(top_unit_display, use_container_width=True, hide_index=True)

    col1, col2, col3 = st.columns(3)
    
    top_units = unit_data.head(3)
    
    with col1:
        top1 = top_units.iloc[0]
        st.success(f"""
**🥇 Rank 1**

{top1['Unit']}

**{int(top1['Total Poin'])} / 100 Poin**

{top1['Kategori']}
        """)
    
    with col2:
        top2 = top_units.iloc[1]
        st.info(f"""
**🥈 Rank 2**

{top2['Unit']}

**{int(top2['Total Poin'])} / 100 Poin**

{top2['Kategori']}
        """)
    
    with col3:
        top3 = top_units.iloc[2]
        st.warning(f"""
**🥉 Rank 3**

{top3['Unit']}

**{int(top3['Total Poin'])} / 100 Poin**

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
    "<small>100 Point Scale: Realisasi (25) + Growth OS (25) + Growth Kupedes (15) + Quality (20) + Akuisisi (15)</small>"
    "</div>",
    unsafe_allow_html=True
)
