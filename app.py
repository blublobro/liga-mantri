import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import random

# ==========================
# KONFIGURASI HALAMAN
# ==========================
st.set_page_config(page_title="MELESAT Dashboard", page_icon="🚀", layout="wide")

st.markdown("""
<style>
.stApp {background-color:#f0f4f8;}
.block-container{padding-top:1rem;padding-left:2rem;padding-right:2rem;}
section[data-testid="stSidebar"]{background:linear-gradient(180deg,#00529C,#003B73);}
section[data-testid="stSidebar"] *{color:white !important;}

/* Fix warna teks & background selectbox di sidebar */
section[data-testid="stSidebar"] .stSelectbox div[data-baseweb="select"] > div {
    background-color: rgba(255,255,255,0.12) !important;
    border: 1px solid rgba(255,255,255,0.3) !important;
    border-radius: 8px !important;
}
section[data-testid="stSidebar"] .stSelectbox div[data-baseweb="select"] span,
section[data-testid="stSidebar"] .stSelectbox div[data-baseweb="select"] div,
section[data-testid="stSidebar"] .stSelectbox [data-testid="stMarkdownContainer"] p {
    color: white !important;
}
section[data-testid="stSidebar"] .stSelectbox svg {
    fill: white !important;
}
/* Dropdown list yang muncul */
[data-baseweb="popover"] ul li {
    color: #1a1a2e !important;
    background-color: white !important;
}
[data-baseweb="popover"] ul li:hover {
    background-color: #e8f0fe !important;
}

.stButton>button{width:100%;border-radius:10px;background:transparent;color:white;border:none;text-align:left;font-weight:600;padding:8px 12px;}
.stButton>button:hover{background:rgba(255,255,255,0.15);border-left:4px solid #F37021;}
div[data-testid="stMetric"]{background:white;border-left:5px solid #00529C;padding:10px;border-radius:10px;box-shadow:0 2px 8px rgba(0,0,0,.08);}
.top20-badge{background:linear-gradient(135deg,#FFD700,#FFA500);color:#7B3F00;font-weight:bold;padding:6px 14px;border-radius:20px;display:inline-block;font-size:13px;}
.status-hijau{background:#d4edda;color:#155724;padding:4px 10px;border-radius:8px;font-weight:bold;}
.status-kuning{background:#fff3cd;color:#856404;padding:4px 10px;border-radius:8px;font-weight:bold;}
.status-merah{background:#f8d7da;color:#721c24;padding:4px 10px;border-radius:8px;font-weight:bold;}
.card-info{background:white;border-radius:12px;padding:16px;box-shadow:0 2px 8px rgba(0,0,0,.08);margin-bottom:10px;}
.tip-box{background:#e8f4fd;border-left:4px solid #00529C;border-radius:8px;padding:12px 16px;margin-bottom:8px;}
.tip-box-warn{background:#fff8e1;border-left:4px solid #F37021;border-radius:8px;padding:12px 16px;margin-bottom:8px;}
.komponen-card{background:white;border-radius:10px;padding:14px;box-shadow:0 2px 6px rgba(0,0,0,.07);margin-bottom:8px;cursor:help;}
.komponen-card:hover{box-shadow:0 4px 12px rgba(0,82,156,.18);border-left:4px solid #00529C;}
.progress-bar-wrap{background:#e9ecef;border-radius:8px;height:16px;margin-top:4px;}
.progress-bar-fill{height:16px;border-radius:8px;}
</style>
""", unsafe_allow_html=True)

# ==========================
# DEFINISI PERIODE
# ==========================
PERIODE_LIST = ["Januari 2026","Februari 2026","Maret 2026","April 2026","Mei 2026","Juni 2026"]
PERIODE_SEED = {p: i*7 for i, p in enumerate(PERIODE_LIST)}

# ==========================
# FUNGSI GENERATE DATA PER PERIODE
# ==========================
def generate_data(seed_offset=0):
    random.seed(42 + seed_offset)
    np.random.seed(42 + seed_offset)

    wilayah_list = ["Jakarta", "Surabaya", "Bandung", "Medan", "Makassar", "Semarang", "Palembang", "Balikpapan"]
    unit_map = {
        "Jakarta": ["Jakarta Pusat", "Jakarta Selatan", "Jakarta Barat", "Jakarta Timur"],
        "Surabaya": ["Surabaya Utara", "Surabaya Selatan", "Gresik", "Sidoarjo"],
        "Bandung": ["Bandung Kota", "Bandung Barat", "Cimahi", "Garut"],
        "Medan": ["Medan Kota", "Medan Barat", "Deli Serdang", "Binjai"],
        "Makassar": ["Makassar Kota", "Gowa", "Maros", "Bone"],
        "Semarang": ["Semarang Kota", "Semarang Barat", "Kendal", "Salatiga"],
        "Palembang": ["Palembang Kota", "Palembang Barat", "Ogan Ilir", "Prabumulih"],
        "Balikpapan": ["Balikpapan Kota", "Balikpapan Selatan", "Samarinda", "Bontang"],
    }
    nama_depan = ["Andi","Budi","Citra","Dedi","Eka","Fitra","Gita","Hendra","Indra","Joko",
                   "Kiki","Lina","Made","Nanda","Oscar","Putri","Rama","Sari","Tono","Umar",
                   "Vina","Wati","Yoga","Zaki","Agus","Bayu","Cici","Dian","Erna","Fajar",
                   "Galih","Hani","Ivan","Jeni","Kartika","Lukman","Maya","Niko","Oky","Pipit",
                   "Qori","Rendi","Sinta","Taufik","Ulfa","Vero","Wendi","Xena","Yudi","Zahra"]
    nama_belakang = ["Santoso","Wijaya","Pratama","Kusuma","Rahayu","Setiawan","Cahyono","Hartono",
                      "Nugroho","Permata","Dewi","Susanto","Lestari","Purnama","Saputra","Wahyudi",
                      "Hidayat","Andriani","Mukti","Suryadi"]

    N = 80
    # Nama dikunci agar konsisten antar periode
    random_name = random.Random(42)
    names = [f"{random_name.choice(nama_depan)} {random_name.choice(nama_belakang)}" for _ in range(N)]
    random_wil = random.Random(42)
    wilayah_assigned = [random_wil.choice(wilayah_list) for _ in range(N)]
    unit_assigned = [random.choice(unit_map[w]) for w in wilayah_assigned]
    agent_ids = [f"AGT{1000+i}" for i in range(N)]

    sales_volume = np.random.randint(50, 500, N) * 1_000_000
    jumlah_transaksi = np.random.randint(50, 800, N)
    hari_aktif = np.random.randint(15, 30, N)
    produk_digunakan = np.random.randint(1, 6, N)
    growth_mom = np.random.uniform(-10, 40, N)
    fee_income = (sales_volume * np.random.uniform(0.005, 0.015, N)).astype(int)

    baseline_trx = (jumlah_transaksi * np.random.uniform(0.6, 0.95, N)).astype(int)
    baseline_vol = (sales_volume * np.random.uniform(0.6, 0.95, N)).astype(int)
    incremental_trx_pct = ((jumlah_transaksi - baseline_trx) / baseline_trx * 100).round(1)
    incremental_vol_pct = ((sales_volume - baseline_vol) / baseline_vol * 100).round(1)

    # MELESAT Score = 70% Transaksi + 30% Volume
    trx_norm = (jumlah_transaksi - jumlah_transaksi.min()) / (jumlah_transaksi.max() - jumlah_transaksi.min()) * 100
    vol_norm = (sales_volume - sales_volume.min()) / (sales_volume.max() - sales_volume.min()) * 100
    melesat_score = (0.70 * trx_norm + 0.30 * vol_norm).round(1)

    # Health Score — TANPA customer baru
    # Bobot baru: Frekuensi 35%, Nominal 25%, Produk 20%, Hari Aktif 10%, Growth 10%
    freq_norm = (jumlah_transaksi / jumlah_transaksi.max() * 100)
    nom_norm   = (sales_volume / sales_volume.max() * 100)
    prod_norm  = (produk_digunakan / produk_digunakan.max() * 100)
    hari_norm  = (hari_aktif / hari_aktif.max() * 100)
    grow_norm  = ((growth_mom - growth_mom.min()) / (growth_mom.max() - growth_mom.min()) * 100)

    health_score = (
        0.35 * freq_norm +
        0.25 * nom_norm  +
        0.20 * prod_norm +
        0.10 * hari_norm +
        0.10 * grow_norm
    ).round(1)

    def health_status(s):
        if s >= 65: return "🟢 Hijau"
        elif s >= 40: return "🟡 Kuning"
        else: return "🔴 Merah"

    def segment(s, v):
        if s >= 65 and v >= 300_000_000: return "⭐ Champion"
        elif s >= 65: return "🚀 High Potential"
        elif v >= 300_000_000: return "💰 Low Value"
        else: return "💤 Dormant"

    agent_df = pd.DataFrame({
        "Agent ID": agent_ids,
        "Nama Agent": names,
        "Wilayah": wilayah_assigned,
        "Unit": unit_assigned,
        "Sales Volume (Rp)": sales_volume,
        "Jumlah Transaksi": jumlah_transaksi,
        "Hari Aktif": hari_aktif,
        "Produk Digunakan": produk_digunakan,
        "Growth MoM (%)": growth_mom.round(1),
        "Fee Income (Rp)": fee_income,
        "Incremental Trx (%)": incremental_trx_pct,
        "Incremental Vol (%)": incremental_vol_pct,
        "MELESAT Score": melesat_score,
        "Health Score": health_score,
        "_trx_norm": trx_norm,
        "_vol_norm": vol_norm,
        "_freq_norm": freq_norm,
        "_nom_norm": nom_norm,
        "_prod_norm": prod_norm,
        "_hari_norm": hari_norm,
        "_grow_norm": grow_norm,
    })

    agent_df["Status"] = agent_df["Health Score"].apply(health_status)
    agent_df["Segmen"] = agent_df.apply(lambda r: segment(r["Health Score"], r["Sales Volume (Rp)"]), axis=1)
    agent_df = agent_df.sort_values("MELESAT Score", ascending=False).reset_index(drop=True)
    agent_df["Rank"] = range(1, len(agent_df) + 1)
    agent_df["Top 20"] = agent_df["Rank"] <= 20

    return agent_df, N, wilayah_list, unit_map

# ==========================
# SESSION STATE
# ==========================
if "view" not in st.session_state:
    st.session_state.view = "agent"
if "page" not in st.session_state:
    st.session_state.page = "Beranda"
if "selected_agent_id" not in st.session_state:
    st.session_state.selected_agent_id = "AGT1000"
if "periode" not in st.session_state:
    st.session_state.periode = "Juni 2026"
if "kanpus_wilayah" not in st.session_state:
    st.session_state.kanpus_wilayah = "Semua"

# ==========================
# LOAD DATA BERDASARKAN PERIODE
# ==========================
periode_selected = st.session_state.periode
seed_off = PERIODE_SEED.get(periode_selected, 0)
agent_df, N, wilayah_list, unit_map = generate_data(seed_off)

# Pastikan selected agent masih valid
if st.session_state.selected_agent_id not in agent_df["Agent ID"].values:
    st.session_state.selected_agent_id = agent_df["Agent ID"].iloc[0]

TOP20    = agent_df[agent_df["Top 20"]].copy()
merah_df = agent_df[agent_df["Status"] == "🔴 Merah"].copy()

# ==========================
# SIDEBAR
# ==========================
with st.sidebar:
    st.markdown("<h2 style='color:white;margin-bottom:0'>🚀 MELESAT</h2>", unsafe_allow_html=True)
    st.markdown("<p style='color:#acd4f5;font-size:12px'>Merchant & Agent Leveraging for<br>Enhanced Sales & Active Transactions</p>", unsafe_allow_html=True)
    st.divider()

    # ---- PILIH PERIODE ----
    st.markdown("<b style='color:#acd4f5;font-size:12px'>📅 PILIH PERIODE</b>", unsafe_allow_html=True)
    new_periode = st.selectbox(
        "", PERIODE_LIST,
        index=PERIODE_LIST.index(st.session_state.periode),
        label_visibility="collapsed"
    )
    if new_periode != st.session_state.periode:
        st.session_state.periode = new_periode
        st.rerun()

    st.divider()

    st.markdown("<b style='color:#acd4f5;font-size:12px'>MODE TAMPILAN</b>", unsafe_allow_html=True)
    col_v1, col_v2 = st.columns(2)
    with col_v1:
        if st.button("👤 Agent", use_container_width=True):
            st.session_state.view = "agent"
            st.session_state.page = "Beranda"
    with col_v2:
        if st.button("🏢 Kanpus", use_container_width=True):
            st.session_state.view = "kanpus"
            st.session_state.page = "Overview"

    st.divider()

    if st.session_state.view == "agent":
        st.markdown("<b style='color:#acd4f5;font-size:12px'>MENU AGENT</b>", unsafe_allow_html=True)
        agent_menus = [
            ("🏠 Beranda", "Beranda"),
            ("🏅 Top 20 Leaderboard", "Top 20 Leaderboard"),
            ("📊 Performa Saya", "Performa Saya"),
            ("🎯 Target & Progress", "Target & Progress"),
        ]
        for label, val in agent_menus:
            if st.button(label, use_container_width=True):
                st.session_state.page = val

        st.divider()
        st.markdown("<b style='color:#acd4f5;font-size:12px'>PILIH AGENT (DEMO)</b>", unsafe_allow_html=True)
        selected_name = st.selectbox(
            "", agent_df["Nama Agent"].tolist(), label_visibility="collapsed",
            index=int(agent_df[agent_df["Agent ID"] == st.session_state.selected_agent_id].index[0])
        )
        st.session_state.selected_agent_id = agent_df[agent_df["Nama Agent"] == selected_name]["Agent ID"].iloc[0]

    else:
        st.markdown("<b style='color:#acd4f5;font-size:12px'>MENU KANTOR PUSAT</b>", unsafe_allow_html=True)
        kanpus_menus = [
            ("📊 Overview Nasional", "Overview"),
            ("🏅 Top 20 Penerima Hadiah", "Top 20 Penerima Hadiah"),
            ("🗺️ Breakdown Wilayah", "Breakdown Wilayah"),
            ("🔴 Early Warning", "Early Warning"),
        ]
        for label, val in kanpus_menus:
            if st.button(label, use_container_width=True):
                st.session_state.page = val

        st.divider()
        # Filter wilayah global untuk kanpus
        st.markdown("<b style='color:#acd4f5;font-size:12px'>🗺️ FILTER WILAYAH</b>", unsafe_allow_html=True)
        new_wil = st.selectbox(
            "", ["Semua"] + wilayah_list,
            index=(["Semua"] + wilayah_list).index(st.session_state.kanpus_wilayah),
            label_visibility="collapsed"
        )
        if new_wil != st.session_state.kanpus_wilayah:
            st.session_state.kanpus_wilayah = new_wil
            st.rerun()

    st.divider()
    st.markdown(f"<small style='color:#acd4f5'>Mode: {'👤 Agent PNM' if st.session_state.view=='agent' else '🏢 Kantor Pusat'}</small>", unsafe_allow_html=True)
    st.markdown(f"<small style='color:#acd4f5'>Periode: {periode_selected}</small>", unsafe_allow_html=True)

# ==========================
# HEADER
# ==========================
h1, h2, h3 = st.columns([4, 1, 1])
with h1:
    mode_label = "👤 Agent PNM View" if st.session_state.view == "agent" else "🏢 Kantor Pusat View"
    wil_label  = f" — {st.session_state.kanpus_wilayah}" if st.session_state.view == "kanpus" and st.session_state.kanpus_wilayah != "Semua" else ""
    st.markdown(
        f"<h1 style='color:#00529C;margin-bottom:0'>MELESAT <span style='color:#F37021;font-size:18px'>{mode_label}{wil_label}</span></h1>"
        "<p style='color:gray;font-size:13px'>More Active Agents, More Valuable Transactions | Program MELESAT – PNM Holding BRI</p>",
        unsafe_allow_html=True
    )
with h2:
    st.metric("Periode", periode_selected.split()[0])
with h3:
    st.metric("Total Agent", f"{N} Agent")

st.divider()

def color_for_pct(pct):
    if pct >= 80: return "#198754"
    elif pct >= 50: return "#F37021"
    else: return "#dc3545"

# ==========================
# HEALTH KOMPONEN INFO
# ==========================
HEALTH_KOMPONEN_INFO = {
    "Frekuensi Transaksi (35%)": {
        "icon": "🔁",
        "label": "Frekuensi Transaksi",
        "bobot": "35%",
        "penjelasan": "Seberapa sering kamu melakukan transaksi dalam sebulan. Semakin banyak transaksi, semakin tinggi skormu. Ini komponen paling penting dalam Health Score.",
        "tips": "Coba lakukan minimal 20–30 transaksi setiap hari. Setiap transaksi kecil pun dihitung!",
        "key": "_freq_norm",
        "bobot_float": 0.35
    },
    "Nominal Transaksi (25%)": {
        "icon": "💰",
        "label": "Nominal Transaksi",
        "bobot": "25%",
        "penjelasan": "Total nilai rupiah dari semua transaksimu. Transaksi bernilai besar seperti angsuran atau pajak sangat membantu menaikkan skor ini.",
        "tips": "Dorong nasabah bayar angsuran, BPJS, listrik lewat kamu. Nilai besar = skor tinggi.",
        "key": "_nom_norm",
        "bobot_float": 0.25
    },
    "Produk yang Digunakan (20%)": {
        "icon": "🛒",
        "label": "Produk Digunakan",
        "bobot": "20%",
        "penjelasan": "Berapa jenis produk yang kamu tawarkan ke nasabah (transfer, top up, pulsa, listrik, angsuran, dll). Makin banyak jenis produk, makin baik.",
        "tips": "Jangan hanya jualan 1 jenis produk. Coba tawarkan semua layanan yang tersedia di aplikasimu.",
        "key": "_prod_norm",
        "bobot_float": 0.20
    },
    "Hari Aktif (10%)": {
        "icon": "📅",
        "label": "Hari Aktif",
        "bobot": "10%",
        "penjelasan": "Berapa hari dalam sebulan kamu aktif melakukan transaksi. Ideal: aktif hampir setiap hari kerja.",
        "tips": "Usahakan buka aplikasi dan lakukan minimal 1 transaksi setiap hari kerja.",
        "key": "_hari_norm",
        "bobot_float": 0.10
    },
    "Pertumbuhan (10%)": {
        "icon": "📈",
        "label": "Pertumbuhan MoM",
        "bobot": "10%",
        "penjelasan": "Seberapa besar peningkatan transaksimu dibanding bulan lalu. Nilai positif berarti kamu makin aktif.",
        "tips": "Bandingkan performa bulanmu ini dengan bulan lalu. Terus tingkatkan agar tetap tumbuh.",
        "key": "_grow_norm",
        "bobot_float": 0.10
    },
}

# ==========================
# ========== AGENT VIEW ==========
# ==========================
if st.session_state.view == "agent":

    me = agent_df[agent_df["Agent ID"] == st.session_state.selected_agent_id].iloc[0]
    my_idx = int(agent_df[agent_df["Agent ID"] == st.session_state.selected_agent_id].index[0])

    # ---- BERANDA ----
    if st.session_state.page == "Beranda":
        st.subheader(f"Selamat Datang, {me['Nama Agent']} 👋")
        st.caption(f"Periode: {periode_selected} | Wilayah: {me['Wilayah']} – {me['Unit']}")

        in_top20 = me["Top 20"]
        if in_top20:
            st.markdown(f"<div class='top20-badge'>🎉 SELAMAT! Kamu masuk TOP 20 penerima hadiah MELESAT! (Rank #{int(me['Rank'])})</div><br>", unsafe_allow_html=True)
        else:
            gap = agent_df.iloc[19]["MELESAT Score"] - me["MELESAT Score"]
            st.warning(f"⚠️ Kamu belum masuk Top 20. Butuh **+{gap:.1f} poin MELESAT** lagi untuk dapat hadiah!")

        # ---- RINGKASAN CEPAT ----
        k1,k2,k3,k4 = st.columns(4)
        with k1:
            st.metric("🏅 Posisi Kamu", f"#{int(me['Rank'])} dari {N}")
        with k2:
            st.metric("⭐ Skor MELESAT", f"{me['MELESAT Score']:.1f} poin")
        with k3:
            color_h = "normal" if me["Health Score"] >= 65 else ("off" if me["Health Score"] >= 40 else "inverse")
            st.metric("💚 Health Score", f"{me['Health Score']:.1f}", me["Status"])
        with k4:
            st.metric("🔁 Total Transaksi", f"{int(me['Jumlah Transaksi'])} kali")

        st.divider()

        # ---- APA ITU MELESAT SCORE? ----
        with st.expander("ℹ️ Apa itu MELESAT Score dan bagaimana cara menaikkannya?", expanded=False):
            st.markdown("""
**MELESAT Score** adalah nilai yang menentukan siapa 20 agent terbaik yang dapat **hadiah** setiap bulannya.

**Cara hitungnya:**
- 🔁 **70%** dari Jumlah Transaksi kamu (dibanding semua agent)
- 💰 **30%** dari Sales Volume / Nilai Transaksi kamu (dibanding semua agent)

**Tips singkat naik skor:**
1. Perbanyak transaksi setiap hari → ini paling berpengaruh!
2. Dorong nasabah bayar nominal besar (angsuran, BPJS, pajak)
3. Aktif setiap hari kerja tanpa skip
            """)

        # ---- GRAFIK POSISI ----
        c1, c2 = st.columns([1.2, 1])
        with c1:
            st.markdown("#### 📊 Posisimu di Antara Top 20")
            top20_scores = agent_df.head(20)["MELESAT Score"].tolist()
            labels = [f"Rank {i+1}" for i in range(20)]
            colors = ["#F37021" if agent_df.iloc[i]["Agent ID"] == me["Agent ID"] else "#00529C" for i in range(20)]
            is_me = [agent_df.iloc[i]["Agent ID"] == me["Agent ID"] for i in range(20)]

            fig = go.Figure(go.Bar(
                x=labels, y=top20_scores,
                marker_color=colors,
                text=[f"{'👉 KAMU' if m else s:.1f}" if m else f"{s:.1f}" for s, m in zip(top20_scores, is_me)],
                textposition="outside"
            ))
            fig.update_layout(
                plot_bgcolor="white", paper_bgcolor="white",
                yaxis=dict(range=[0, 115]),
                height=320, margin=dict(t=20, b=20),
                annotations=[dict(
                    text="🟠 = Posisi Kamu",
                    showarrow=False, x=0.01, y=1.05,
                    xref="paper", yref="paper", font=dict(size=12)
                )]
            )
            st.plotly_chart(fig, use_container_width=True)

        with c2:
            st.markdown("#### 🧩 Dari Mana Skormu Berasal?")
            trx_contrib = round(0.70 * float(me["_trx_norm"]), 1)
            vol_contrib = round(0.30 * float(me["_vol_norm"]), 1)
            fig2 = go.Figure(go.Pie(
                labels=["🔁 Transaksi (70%)", "💰 Volume (30%)"],
                values=[trx_contrib, vol_contrib],
                hole=0.5,
                marker_colors=["#00529C", "#F37021"]
            ))
            fig2.update_layout(height=220, margin=dict(t=10, b=10), showlegend=True)
            st.plotly_chart(fig2, use_container_width=True)
            st.info(f"""
**Detail Skor:**
- 🔁 Dari Transaksi: **{trx_contrib:.1f} poin**
- 💰 Dari Volume: **{vol_contrib:.1f} poin**
- ⭐ **Total: {me['MELESAT Score']:.1f} poin**
            """)

        st.divider()

        # ---- HEALTH SCORE BREAKDOWN (dengan tooltip/penjelasan) ----
        st.markdown("#### 💚 Health Score Kamu — Apa yang Perlu Ditingkatkan?")
        st.caption("Health Score mengukur seberapa 'sehat' aktivitas transaksimu. Klik tiap komponen untuk tahu cara meningkatkannya.")

        comp_cols = st.columns(len(HEALTH_KOMPONEN_INFO))
        for col, (nama_komp, info) in zip(comp_cols, HEALTH_KOMPONEN_INFO.items()):
            raw_val = float(me[info["key"]])
            kontribusi = round(info["bobot_float"] * raw_val, 1)
            pct_display = round(raw_val, 1)
            bar_color = color_for_pct(pct_display)
            bar_width = min(100, max(0, pct_display))
            card_html = (
                f"<div class='komponen-card' title='{info['penjelasan']}'>"
                f"<div style='font-size:22px;text-align:center'>{info['icon']}</div>"
                f"<div style='font-size:11px;font-weight:bold;text-align:center;color:#00529C;margin-top:4px'>{info['label']}</div>"
                f"<div style='font-size:10px;color:gray;text-align:center'>Bobot {info['bobot']}</div>"
                f"<div style='font-size:18px;font-weight:bold;text-align:center;color:{bar_color};margin:6px 0'>{pct_display:.0f}/100</div>"
                f"<div class='progress-bar-wrap'>"
                f"<div class='progress-bar-fill' style='width:{bar_width}%;background:{bar_color};'></div>"
                f"</div>"
                f"<div style='font-size:10px;color:#555;text-align:center;margin-top:4px'>+{kontribusi:.1f} poin</div>"
                f"</div>"
            )
            with col:
                st.markdown(card_html, unsafe_allow_html=True)

        # Expandable detail per komponen
        st.markdown("##### 💡 Detail & Tips Tiap Komponen (klik untuk buka):")
        for nama_komp, info in HEALTH_KOMPONEN_INFO.items():
            raw_val = float(me[info["key"]])
            pct_display = round(raw_val, 1)
            bar_color = color_for_pct(pct_display)
            status_label = "✅ Bagus!" if pct_display >= 70 else ("⚠️ Perlu Ditingkatkan" if pct_display >= 40 else "🔴 Kurang, Perlu Aksi Segera")
            with st.expander(f"{info['icon']} {info['label']} — Nilaimu: {pct_display:.0f}/100 {status_label}"):
                st.markdown(f"**Apa ini?** {info['penjelasan']}")
                st.markdown(f"**💡 Tips:** {info['tips']}")
                st.progress(int(pct_display))

        st.divider()

        # ---- REKOMENDASI MUDAH DIPAHAMI ----
        st.markdown("#### 🎯 Yang Perlu Kamu Lakukan Sekarang:")
        actions_found = False
        for nama_komp, info in HEALTH_KOMPONEN_INFO.items():
            raw_val = float(me[info["key"]])
            if raw_val < 50:
                st.markdown(f"""
<div class='tip-box-warn'>
{info['icon']} <b>{info['label']}</b> kamu masih rendah ({raw_val:.0f}/100)<br>
→ {info['tips']}
</div>""", unsafe_allow_html=True)
                actions_found = True

        if not actions_found:
            st.success("🎉 Semua komponen Health Score kamu sudah bagus! Pertahankan dan terus tingkatkan!")

    # ---- TOP 20 LEADERBOARD ----
    elif st.session_state.page == "Top 20 Leaderboard":
        st.subheader(f"🏅 Top 20 Penerima Hadiah MELESAT – {periode_selected}")

        my_rank = int(me["Rank"])
        if my_rank <= 20:
            st.success(f"✅ Kamu ada di posisi #{my_rank} — Selamat, kamu termasuk penerima hadiah!")
        else:
            gap = agent_df.iloc[19]["MELESAT Score"] - me["MELESAT Score"]
            st.warning(f"Posisimu: #{my_rank}. Butuh **+{gap:.1f} poin** untuk masuk Top 20.")

        display = TOP20[["Rank","Nama Agent","Wilayah","Unit","MELESAT Score","Jumlah Transaksi","Sales Volume (Rp)","Health Score","Status","Segmen"]].copy()
        display["Sales Volume (Rp)"] = display["Sales Volume (Rp)"].apply(lambda x: f"Rp {x/1e6:.0f} Jt")
        display["MELESAT Score"] = display["MELESAT Score"].round(1)
        display["Health Score"] = display["Health Score"].round(1)
        display.columns = ["#","Nama Agent","Wilayah","Unit","MELESAT Score","Transaksi","Sales Vol","Health","Status","Segmen"]

        def highlight_me(row):
            if row["Nama Agent"] == me["Nama Agent"]:
                return ["background-color: #fff3cd"] * len(row)
            return [""] * len(row)

        st.dataframe(display.style.apply(highlight_me, axis=1), use_container_width=True, hide_index=True)

        st.divider()
        fig = px.bar(
            TOP20.sort_values("MELESAT Score"),
            x="MELESAT Score", y="Nama Agent", orientation="h",
            text="MELESAT Score",
            color="MELESAT Score", color_continuous_scale="Blues",
            title=f"MELESAT Score – Top 20 Agent ({periode_selected})"
        )
        fig.update_layout(plot_bgcolor="white", paper_bgcolor="white", height=600, xaxis=dict(range=[0,110]))
        st.plotly_chart(fig, use_container_width=True)

    # ---- PERFORMA SAYA ----
    elif st.session_state.page == "Performa Saya":
        st.subheader(f"📊 Performa Saya – {me['Nama Agent']} | {periode_selected}")

        k1,k2,k3,k4 = st.columns(4)
        with k1: st.metric("Sales Volume", f"Rp {me['Sales Volume (Rp)']/1e6:.0f} Jt", f"+{me['Incremental Vol (%)']:.1f}% vs bulan lalu")
        with k2: st.metric("Jumlah Transaksi", f"{int(me['Jumlah Transaksi'])} Trx", f"+{me['Incremental Trx (%)']:.1f}% vs bulan lalu")
        with k3: st.metric("Fee Income", f"Rp {me['Fee Income (Rp)']/1e6:.2f} Jt")
        with k4: st.metric("Hari Aktif", f"{int(me['Hari Aktif'])} / 30 hari")

        st.divider()

        days = list(range(1, 31))
        random.seed(42 + seed_off + hash(me["Agent ID"]) % 100)
        trx_daily = [random.randint(int(me["Jumlah Transaksi"]*0.02), int(me["Jumlah Transaksi"]*0.06)) for _ in days]
        vol_daily = [random.randint(int(me["Sales Volume (Rp)"]*0.02), int(me["Sales Volume (Rp)"]*0.06)) for _ in days]

        c1, c2 = st.columns(2)
        with c1:
            df_trx = pd.DataFrame({"Hari": days, "Transaksi": trx_daily})
            fig = px.area(df_trx, x="Hari", y="Transaksi", title="Transaksi Harian (Simulasi)")
            fig.update_traces(line_color="#00529C", fillcolor="rgba(0,82,156,0.15)")
            fig.update_layout(plot_bgcolor="white", paper_bgcolor="white", height=280)
            st.plotly_chart(fig, use_container_width=True)

        with c2:
            df_vol = pd.DataFrame({"Hari": days, "Volume (Juta)": [v/1e6 for v in vol_daily]})
            fig2 = px.area(df_vol, x="Hari", y="Volume (Juta)", title="Sales Volume Harian (Simulasi)")
            fig2.update_traces(line_color="#F37021", fillcolor="rgba(243,112,33,0.15)")
            fig2.update_layout(plot_bgcolor="white", paper_bgcolor="white", height=280)
            st.plotly_chart(fig2, use_container_width=True)

        st.divider()
        st.markdown("#### 🛒 Distribusi Transaksi per Jenis")
        random.seed(seed_off + my_idx)
        trx_types = pd.DataFrame({
            "Jenis": ["Transfer", "Top Up", "Pulsa", "Listrik/BPJS", "Angsuran", "Lainnya"],
            "Transaksi": [random.randint(10,100) for _ in range(6)]
        })
        fig3 = px.pie(trx_types, names="Jenis", values="Transaksi", hole=0.4,
                      color_discrete_sequence=px.colors.qualitative.Set2)
        fig3.update_layout(height=320)
        st.plotly_chart(fig3, use_container_width=True)

    # ---- TARGET & PROGRESS ----
    elif st.session_state.page == "Target & Progress":
        st.subheader(f"🎯 Target & Progress – {me['Nama Agent']} | {periode_selected}")

        target_trx = 600
        target_vol = 400_000_000
        target_health = 65.0
        target_rank = 20

        p1,p2,p3,p4 = st.columns(4)
        pct_trx = min(100, me["Jumlah Transaksi"] / target_trx * 100)
        pct_vol = min(100, me["Sales Volume (Rp)"] / target_vol * 100)
        pct_health = min(100, me["Health Score"] / target_health * 100)

        with p1: st.metric("Transaksi", f"{int(me['Jumlah Transaksi'])} / {target_trx}", f"{pct_trx:.0f}% tercapai")
        with p2: st.metric("Sales Volume", f"Rp {me['Sales Volume (Rp)']/1e6:.0f} / 400 Jt", f"{pct_vol:.0f}% tercapai")
        with p3: st.metric("Health Score", f"{me['Health Score']:.1f} / {target_health}", f"{pct_health:.0f}% tercapai")
        with p4: st.metric("Target Rank", f"#{int(me['Rank'])} → Top {target_rank}", "✅ Masuk!" if me["Rank"] <= target_rank else "❌ Belum")

        st.divider()

        indicators = ["Transaksi", "Sales Volume", "Health Score"]
        pct_values = [pct_trx, pct_vol, pct_health]
        colors_bar = [color_for_pct(p) for p in pct_values]

        fig = go.Figure()
        for ind, pct, col in zip(indicators, pct_values, colors_bar):
            fig.add_trace(go.Bar(
                x=[pct], y=[ind], orientation="h",
                marker_color=col, text=[f"{pct:.0f}%"], textposition="outside",
                showlegend=False
            ))
        fig.update_layout(
            plot_bgcolor="white", paper_bgcolor="white",
            xaxis=dict(range=[0,115], title="% Pencapaian"),
            height=300, title="Progress Menuju Target",
            barmode="overlay"
        )
        st.plotly_chart(fig, use_container_width=True)

        st.divider()
        st.markdown("#### 💡 Yang Perlu Kamu Lakukan:")
        if pct_trx < 100:
            sisa = target_trx - int(me["Jumlah Transaksi"])
            per_hari = max(1, sisa // max(1, 30 - int(me["Hari Aktif"])))
            st.warning(f"🔁 Tambah **{sisa} transaksi** lagi. Coba lakukan **{per_hari} transaksi/hari** di sisa hari ini.")
        if pct_vol < 100:
            sisa_vol = (target_vol - me["Sales Volume (Rp)"]) / 1e6
            st.warning(f"💰 Tambah nilai transaksi **Rp {sisa_vol:.0f} Jt** lagi. Dorong nasabah bayar angsuran atau nilai besar.")
        if me["Health Score"] < target_health:
            st.info(f"💚 Naikkan Health Score dari {me['Health Score']:.1f} → {target_health}. Fokus: gunakan lebih banyak jenis produk.")
        if me["Rank"] <= target_rank:
            st.success("🎉 Kamu sudah masuk Top 20! Pertahankan posisimu!")
        else:
            gap_score = agent_df.iloc[19]["MELESAT Score"] - me["MELESAT Score"]
            st.error(f"🔴 Butuh tambah **{gap_score:.1f} poin MELESAT** lagi. Cara tercepat: perbanyak transaksi harian!")

# ==========================
# ========== KANTOR PUSAT VIEW ==========
# ==========================
else:
    # Terapkan filter wilayah global
    kanpus_wil = st.session_state.kanpus_wilayah
    if kanpus_wil == "Semua":
        df_view = agent_df.copy()
        top20_view = TOP20.copy()
        merah_view = merah_df.copy()
    else:
        df_view = agent_df[agent_df["Wilayah"] == kanpus_wil].copy()
        top20_view = df_view[df_view["Top 20"]].copy()
        merah_view = df_view[df_view["Status"] == "🔴 Merah"].copy()

    wil_badge = f" — Wilayah: {kanpus_wil}" if kanpus_wil != "Semua" else ""

    # ---- OVERVIEW ----
    if st.session_state.page == "Overview":
        st.subheader(f"📊 Overview Nasional MELESAT – {periode_selected}{wil_badge}")

        total_hijau = (df_view["Status"] == "🟢 Hijau").sum()
        total_kuning = (df_view["Status"] == "🟡 Kuning").sum()
        total_merah = (df_view["Status"] == "🔴 Merah").sum()
        total_vol = df_view["Sales Volume (Rp)"].sum()
        total_trx = df_view["Jumlah Transaksi"].sum()
        total_fee = df_view["Fee Income (Rp)"].sum()
        n_view = len(df_view)

        k1,k2,k3,k4,k5,k6 = st.columns(6)
        with k1: st.metric("Total Agent", f"{n_view}")
        with k2: st.metric("🟢 Aktif (Hijau)", f"{total_hijau}", f"{total_hijau/max(n_view,1)*100:.0f}%")
        with k3: st.metric("🟡 Waspada", f"{total_kuning}", f"{total_kuning/max(n_view,1)*100:.0f}%")
        with k4: st.metric("🔴 Butuh Intervensi", f"{total_merah}", f"{total_merah/max(n_view,1)*100:.0f}%")
        with k5: st.metric("Total Sales Vol", f"Rp {total_vol/1e9:.1f} M")
        with k6: st.metric("Total Fee Income", f"Rp {total_fee/1e9:.2f} M")

        st.divider()

        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown("#### Distribusi Status Agent")
            fig_s = px.pie(
                names=["🟢 Hijau", "🟡 Kuning", "🔴 Merah"],
                values=[total_hijau, total_kuning, total_merah],
                color_discrete_sequence=["#198754","#ffc107","#dc3545"],
                hole=0.5
            )
            fig_s.update_layout(height=280, margin=dict(t=10,b=10))
            st.plotly_chart(fig_s, use_container_width=True)

        with c2:
            st.markdown("#### Distribusi Segmen Agent")
            seg_counts = df_view["Segmen"].value_counts().reset_index()
            seg_counts.columns = ["Segmen","Jumlah"]
            fig_sg = px.bar(seg_counts, x="Segmen", y="Jumlah",
                            color="Segmen", color_discrete_sequence=["#00529C","#F37021","#198754","#6f42c1"])
            fig_sg.update_layout(plot_bgcolor="white", paper_bgcolor="white", height=280, showlegend=False)
            st.plotly_chart(fig_sg, use_container_width=True)

        with c3:
            st.markdown("#### Health Score Distribusi")
            fig_h = px.histogram(df_view, x="Health Score", nbins=20,
                                 color_discrete_sequence=["#00529C"])
            fig_h.update_layout(plot_bgcolor="white", paper_bgcolor="white", height=280)
            st.plotly_chart(fig_h, use_container_width=True)

        st.divider()
        st.markdown(f"#### 🗺️ Sales Volume & Transaksi per {'Unit' if kanpus_wil != 'Semua' else 'Wilayah'}")

        group_col = "Unit" if kanpus_wil != "Semua" else "Wilayah"
        wilayah_summary = df_view.groupby(group_col).agg(
            Total_Vol=("Sales Volume (Rp)","sum"),
            Total_Trx=("Jumlah Transaksi","sum"),
            Avg_Health=("Health Score","mean"),
            Total_Agent=("Agent ID","count"),
            Agent_Merah=("Status", lambda x: (x=="🔴 Merah").sum())
        ).reset_index()
        wilayah_summary["Total_Vol_M"] = (wilayah_summary["Total_Vol"]/1e6).round(1)

        c4, c5 = st.columns(2)
        with c4:
            fig_w = px.bar(wilayah_summary.sort_values("Total_Vol"), x="Total_Vol_M", y=group_col,
                           orientation="h", text_auto=".0f", color="Total_Vol_M",
                           color_continuous_scale="Blues", title=f"Sales Volume per {group_col} (Juta Rp)")
            fig_w.update_layout(plot_bgcolor="white", paper_bgcolor="white", height=380)
            st.plotly_chart(fig_w, use_container_width=True)
        with c5:
            fig_w2 = px.bar(wilayah_summary.sort_values("Total_Trx"), x="Total_Trx", y=group_col,
                            orientation="h", text_auto="d", color="Total_Trx",
                            color_continuous_scale="Oranges", title=f"Jumlah Transaksi per {group_col}")
            fig_w2.update_layout(plot_bgcolor="white", paper_bgcolor="white", height=380)
            st.plotly_chart(fig_w2, use_container_width=True)

    # ---- TOP 20 PENERIMA HADIAH ----
    elif st.session_state.page == "Top 20 Penerima Hadiah":
        st.subheader(f"🏅 Top 20 Penerima Hadiah MELESAT – {periode_selected}{wil_badge}")
        st.caption("Formula: MELESAT Score = 70% Jumlah Transaksi (normalized) + 30% Sales Volume (normalized)")

        if len(top20_view) >= 3:
            m1,m2,m3 = st.columns(3)
            with m1: st.metric("🥇 Rank 1", top20_view.iloc[0]["Nama Agent"], f"{top20_view.iloc[0]['MELESAT Score']:.1f} poin")
            with m2: st.metric("🥈 Rank 2", top20_view.iloc[1]["Nama Agent"], f"{top20_view.iloc[1]['MELESAT Score']:.1f} poin")
            with m3: st.metric("🥉 Rank 3", top20_view.iloc[2]["Nama Agent"], f"{top20_view.iloc[2]['MELESAT Score']:.1f} poin")
        elif len(top20_view) > 0:
            st.info(f"Terdapat {len(top20_view)} agent top di wilayah ini.")

        st.divider()

        if len(top20_view) > 0:
            display_top = top20_view[[
                "Rank","Nama Agent","Wilayah","Unit","MELESAT Score",
                "Jumlah Transaksi","Sales Volume (Rp)","Health Score","Status","Segmen","Fee Income (Rp)"
            ]].copy()
            display_top["Sales Volume (Rp)"] = display_top["Sales Volume (Rp)"].apply(lambda x: f"Rp {x/1e6:.0f} Jt")
            display_top["Fee Income (Rp)"] = display_top["Fee Income (Rp)"].apply(lambda x: f"Rp {x/1e6:.2f} Jt")
            display_top.columns = ["#","Nama","Wilayah","Unit","MELESAT Score","Trx","Sales Vol","Health","Status","Segmen","Fee Income"]
            st.dataframe(display_top, use_container_width=True, hide_index=True)

            st.divider()

            c1, c2 = st.columns(2)
            with c1:
                fig = px.bar(
                    top20_view.sort_values("MELESAT Score"),
                    x="MELESAT Score", y="Nama Agent", orientation="h",
                    text="MELESAT Score", color="MELESAT Score",
                    color_continuous_scale="Blues", title="MELESAT Score Top 20 Agent"
                )
                fig.update_layout(plot_bgcolor="white", paper_bgcolor="white", height=600, xaxis=dict(range=[0,110]))
                st.plotly_chart(fig, use_container_width=True)

            with c2:
                st.markdown("#### Distribusi Wilayah Top 20")
                top20_wil = top20_view["Wilayah"].value_counts().reset_index()
                top20_wil.columns = ["Wilayah","Jumlah"]
                fig2 = px.pie(top20_wil, names="Wilayah", values="Jumlah", hole=0.4)
                fig2.update_layout(height=300)
                st.plotly_chart(fig2, use_container_width=True)

                st.markdown("#### Segmen Top 20")
                top20_seg = top20_view["Segmen"].value_counts().reset_index()
                top20_seg.columns = ["Segmen","Jumlah"]
                fig3 = px.bar(top20_seg, x="Segmen", y="Jumlah", color="Segmen")
                fig3.update_layout(plot_bgcolor="white", paper_bgcolor="white", height=280, showlegend=False)
                st.plotly_chart(fig3, use_container_width=True)
        else:
            st.info("Tidak ada data Top 20 untuk filter yang dipilih.")

    # ---- BREAKDOWN WILAYAH ----
    elif st.session_state.page == "Breakdown Wilayah":
        st.subheader(f"🗺️ Breakdown per Wilayah & Unit – {periode_selected}{wil_badge}")

        # Pilih wilayah (override sidebar filter untuk page ini)
        selected_wil_local = st.selectbox("Pilih Wilayah Detail", ["Semua"] + wilayah_list,
                                           index=(["Semua"] + wilayah_list).index(kanpus_wil))

        if selected_wil_local == "Semua":
            filtered = agent_df.copy()
        else:
            filtered = agent_df[agent_df["Wilayah"] == selected_wil_local]

        wil_summary = filtered.groupby("Wilayah").agg(
            Jumlah_Agent=("Agent ID","count"),
            Avg_PRIMA=("MELESAT Score","mean"),
            Avg_Health=("Health Score","mean"),
            Total_Vol=("Sales Volume (Rp)","sum"),
            Total_Trx=("Jumlah Transaksi","sum"),
            Total_Fee=("Fee Income (Rp)","sum"),
            Merah=("Status", lambda x: (x=="🔴 Merah").sum()),
            Hijau=("Status", lambda x: (x=="🟢 Hijau").sum()),
            Top20=("Top 20", lambda x: x.sum()),
        ).reset_index()
        wil_summary["Total_Vol_M"] = (wil_summary["Total_Vol"]/1e6).round(1)
        wil_summary["Total_Fee_M"] = (wil_summary["Total_Fee"]/1e6).round(2)
        wil_summary["Avg_PRIMA"] = wil_summary["Avg_PRIMA"].round(1)
        wil_summary["Avg_Health"] = wil_summary["Avg_Health"].round(1)

        display_wil = wil_summary[["Wilayah","Jumlah_Agent","Avg_PRIMA","Avg_Health",
                                    "Total_Vol_M","Total_Trx","Total_Fee_M","Merah","Hijau","Top20"]]
        display_wil.columns = ["Wilayah","Agent","Avg MELESAT","Avg Health","Vol (Jt)","Trx","Fee (Jt)","🔴 Merah","🟢 Hijau","Top 20"]
        st.dataframe(display_wil, use_container_width=True, hide_index=True)

        st.divider()

        if selected_wil_local != "Semua":
            st.markdown(f"#### Detail Unit di {selected_wil_local}")
            unit_summary = filtered.groupby("Unit").agg(
                Jumlah_Agent=("Agent ID","count"),
                Avg_PRIMA=("MELESAT Score","mean"),
                Avg_Health=("Health Score","mean"),
                Total_Vol=("Sales Volume (Rp)","sum"),
                Total_Trx=("Jumlah Transaksi","sum"),
                Merah=("Status", lambda x: (x=="🔴 Merah").sum()),
                Top20=("Top 20", lambda x: x.sum()),
            ).reset_index()
            unit_summary["Total_Vol_M"] = (unit_summary["Total_Vol"]/1e6).round(1)
            unit_summary["Avg_PRIMA"] = unit_summary["Avg_PRIMA"].round(1)
            unit_summary["Avg_Health"] = unit_summary["Avg_Health"].round(1)

            d_unit = unit_summary[["Unit","Jumlah_Agent","Avg_PRIMA","Avg_Health","Total_Vol_M","Total_Trx","Merah","Top20"]]
            d_unit.columns = ["Unit","Agent","Avg MELESAT","Avg Health","Vol (Jt)","Trx","🔴 Merah","Top 20"]
            st.dataframe(d_unit, use_container_width=True, hide_index=True)

            st.divider()
            st.markdown("#### Scatter: Health Score vs MELESAT Score")
            fig_sc = px.scatter(
                filtered, x="Health Score", y="MELESAT Score",
                color="Status", hover_data=["Nama Agent","Unit","Jumlah Transaksi","Sales Volume (Rp)"],
                color_discrete_map={"🟢 Hijau":"#198754","🟡 Kuning":"#ffc107","🔴 Merah":"#dc3545"},
                size="Jumlah Transaksi", title=f"Health vs MELESAT Score – {selected_wil_local}"
            )
            fig_sc.update_layout(plot_bgcolor="white", paper_bgcolor="white", height=450)
            st.plotly_chart(fig_sc, use_container_width=True)
        else:
            c1, c2 = st.columns(2)
            with c1:
                fig_a = px.bar(wil_summary.sort_values("Avg_PRIMA"), x="Avg_PRIMA", y="Wilayah",
                               orientation="h", text_auto=".1f", color="Avg_PRIMA",
                               color_continuous_scale="Blues", title="Rata-rata MELESAT Score per Wilayah")
                fig_a.update_layout(plot_bgcolor="white", paper_bgcolor="white", height=380)
                st.plotly_chart(fig_a, use_container_width=True)
            with c2:
                fig_m = px.bar(wil_summary.sort_values("Merah", ascending=False), x="Merah", y="Wilayah",
                               orientation="h", text_auto="d", color="Merah",
                               color_continuous_scale="Reds", title="Jumlah Agent Merah per Wilayah")
                fig_m.update_layout(plot_bgcolor="white", paper_bgcolor="white", height=380)
                st.plotly_chart(fig_m, use_container_width=True)

    # ---- EARLY WARNING ----
    elif st.session_state.page == "Early Warning":
        st.subheader(f"🔴 Early Warning – Agent Butuh Intervensi | {periode_selected}{wil_badge}")

        total_merah_v = len(merah_view)
        if total_merah_v == 0:
            st.success("✅ Tidak ada agent merah untuk filter yang dipilih.")
        else:
            st.error(f"⚠️ Terdapat **{total_merah_v} agent berstatus MERAH** yang membutuhkan intervensi segera.")

            m1,m2,m3,m4 = st.columns(4)
            with m1: st.metric("Agent Merah", f"{total_merah_v}")
            with m2: st.metric("Avg Health Score", f"{merah_view['Health Score'].mean():.1f}")
            with m3: st.metric("Avg Transaksi", f"{merah_view['Jumlah Transaksi'].mean():.0f} Trx")
            with m4: st.metric("Loss Fee Potential", f"Rp {(agent_df['Fee Income (Rp)'].mean() - merah_view['Fee Income (Rp)'].mean()) * total_merah_v / 1e6:.1f} Jt")

            st.divider()

            display_merah = merah_view[[
                "Rank","Nama Agent","Wilayah","Unit","Health Score","MELESAT Score",
                "Jumlah Transaksi","Sales Volume (Rp)","Hari Aktif","Growth MoM (%)","Segmen"
            ]].copy()
            display_merah["Sales Volume (Rp)"] = display_merah["Sales Volume (Rp)"].apply(lambda x: f"Rp {x/1e6:.0f} Jt")
            display_merah["Growth MoM (%)"] = display_merah["Growth MoM (%)"].round(1)
            display_merah.columns = ["Rank","Nama Agent","Wilayah","Unit","Health","MELESAT Score",
                                       "Trx","Sales Vol","Hari Aktif","Growth %","Segmen"]
            st.dataframe(display_merah.sort_values("Health").reset_index(drop=True), use_container_width=True, hide_index=True)

            st.divider()

            c1, c2 = st.columns(2)
            with c1:
                merah_wil = merah_view.groupby("Wilayah").size().reset_index(name="Jumlah")
                fig_ew = px.bar(merah_wil.sort_values("Jumlah", ascending=False),
                                x="Wilayah", y="Jumlah", text_auto="d",
                                color="Jumlah", color_continuous_scale="Reds",
                                title="Distribusi Agent Merah per Wilayah")
                fig_ew.update_layout(plot_bgcolor="white", paper_bgcolor="white", height=320)
                st.plotly_chart(fig_ew, use_container_width=True)

            with c2:
                merah_seg = merah_view.groupby("Segmen").size().reset_index(name="Jumlah")
                fig_es = px.pie(merah_seg, names="Segmen", values="Jumlah", hole=0.45,
                                title="Segmen Agent Merah")
                fig_es.update_layout(height=320)
                st.plotly_chart(fig_es, use_container_width=True)

            st.divider()
            st.markdown("#### 📋 Rekomendasi Intervensi per Segmen")
            intervensi = {
                "💤 Dormant": "Lakukan reactivation call, kunjungan mantri, dan edukasi ulang aplikasi. Target: minimal 5 trx/hari.",
                "💰 Low Value": "Dorong transaksi bernilai tinggi: angsuran, pajak, BPJS. Berikan insentif berbasis kenaikan nominal.",
                "🚀 High Potential": "Berikan coaching intensif dan akses produk baru. Potensi naik ke Champion jika dikelola baik.",
                "⭐ Champion": "Monitor & pertahankan. Jadikan role model untuk agen lain di wilayah yang sama."
            }
            for seg, action in intervensi.items():
                count = (merah_view["Segmen"] == seg).sum()
                if count > 0:
                    st.warning(f"**{seg}** ({count} agent): {action}")



# ==========================
# FOOTER
# ==========================
st.markdown("---")
st.markdown(
    "<div style='background:linear-gradient(90deg,#00529C,#003B73);color:white;padding:12px 20px;border-radius:10px;text-align:center'>"
    "<b>MELESAT Dashboard</b> – Merchant & Agent Leveraging for Enhanced Sales & Active Transactions<br>"
    "<small>Top 20: 70% Jumlah Transaksi + 30% Sales Volume | Health Score: 5 Dimensi | Program Holding UMi BRI–PNM–Pegadaian</small>"
    "</div>",
    unsafe_allow_html=True
)
