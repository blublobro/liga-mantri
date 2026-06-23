import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import random

random.seed(42)
np.random.seed(42)

st.set_page_config(page_title="MELESAT – PNM", page_icon="🚀", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700;800&display=swap');

html, body, [class*="css"] { font-family: 'Plus Jakarta Sans', sans-serif; }
.stApp { background-color:#f5f7ff; }
.block-container { padding-top:1rem; padding-left:2rem; padding-right:2rem; }

section[data-testid="stSidebar"] {
    background: linear-gradient(180deg,#1a3a6b,#0d1f3c);
}
section[data-testid="stSidebar"] * { color:white !important; }
.stButton>button {
    width:100%; border-radius:12px; background:transparent;
    color:white; border:none; text-align:left; font-weight:600;
    padding:10px 14px; font-size:14px;
}
.stButton>button:hover {
    background:rgba(255,255,255,0.12);
    border-left:4px solid #F37021;
}

div[data-testid="stMetric"] {
    background:white; border-left:5px solid #1a3a6b;
    padding:14px; border-radius:14px;
    box-shadow:0 2px 12px rgba(0,0,0,.07);
}

/* Landing page cards */
.view-card {
    background: white;
    border-radius: 20px;
    padding: 36px 28px;
    text-align: center;
    box-shadow: 0 4px 24px rgba(0,0,0,.10);
    cursor: pointer;
    transition: transform .2s, box-shadow .2s;
    border: 3px solid transparent;
}
.view-card:hover { transform: translateY(-4px); box-shadow: 0 8px 32px rgba(0,0,0,.15); }
.view-card-agent { border-color: #F37021; }
.view-card-kanpus { border-color: #1a3a6b; }

/* Top-20 badge */
.badge-top20 {
    background: linear-gradient(135deg,#FFD700,#FFA500);
    color:#5c3000; font-weight:800; padding:8px 18px;
    border-radius:24px; font-size:15px; display:inline-block;
}
.badge-out {
    background:#fff0f0; color:#c0392b; font-weight:700;
    padding:8px 18px; border-radius:24px; font-size:15px; display:inline-block;
}

/* Info box */
.info-box {
    background:white; border-radius:14px; padding:18px 20px;
    box-shadow:0 2px 10px rgba(0,0,0,.07); margin-bottom:12px;
    border-left: 4px solid #1a3a6b;
}
.info-row { display:flex; justify-content:space-between; padding:6px 0;
            border-bottom:1px solid #f0f0f0; font-size:14px; }
.info-label { color:#888; }
.info-value { font-weight:700; color:#1a3a6b; }

/* Plant animation container */
.plant-wrap { text-align:center; padding:10px 0; }

/* Tooltip helper */
.help-text { font-size:12px; color:#888; font-style:italic; }

/* Section header */
.section-header {
    font-size:18px; font-weight:800; color:#1a3a6b;
    margin-bottom:4px; margin-top:8px;
}
</style>
""", unsafe_allow_html=True)

# =====================================================
# KONSTANTA & HELPER
# =====================================================
PROGRAM_NAME  = "MELESAT"
PROGRAM_FULL  = "Mendorong Ekspansi Layanan & Ekosistem Agen Transaksi"
PROGRAM_TAG   = "Grow Transaction. Grow Profit."
TOP_N         = 20
HEALTH_THRESH_HIJAU  = 65
HEALTH_THRESH_KUNING = 40
VOL_CHAMPION         = 300_000_000

PERIODE_LIST  = ["Juni 2026", "Mei 2026", "April 2026", "Maret 2026"]

KOMPONEN_HEALTH = {
    "Frekuensi Transaksi (30%)":
        "Seberapa sering agent melakukan transaksi dalam sebulan. Semakin banyak, semakin bagus.",
    "Nilai / Sales Volume (20%)":
        "Besarnya total uang yang ditransaksikan. Transaksi bernilai tinggi = skor lebih besar.",
    "Produk Digunakan (15%)":
        "Berapa jenis produk yang dipakai agent: transfer, pulsa, listrik, angsuran, dll. Makin beragam, makin sehat.",
    "Hari Aktif (10%)":
        "Berapa hari dalam sebulan agent aktif buka aplikasi dan bertransaksi.",
    "Growth MoM (10%)":
        "Pertumbuhan transaksi dibanding bulan lalu. Naik = bagus, turun = perlu perhatian.",
}

# =====================================================
# DATA DUMMY
# =====================================================
wilayah_list = ["Jakarta","Surabaya","Bandung","Medan","Makassar","Semarang","Palembang","Balikpapan"]
unit_map = {
    "Jakarta":     ["Jakarta Pusat","Jakarta Selatan","Jakarta Barat","Jakarta Timur"],
    "Surabaya":    ["Surabaya Utara","Surabaya Selatan","Gresik","Sidoarjo"],
    "Bandung":     ["Bandung Kota","Bandung Barat","Cimahi","Garut"],
    "Medan":       ["Medan Kota","Medan Barat","Deli Serdang","Binjai"],
    "Makassar":    ["Makassar Kota","Gowa","Maros","Bone"],
    "Semarang":    ["Semarang Kota","Semarang Barat","Kendal","Salatiga"],
    "Palembang":   ["Palembang Kota","Palembang Barat","Ogan Ilir","Prabumulih"],
    "Balikpapan":  ["Balikpapan Kota","Balikpapan Selatan","Samarinda","Bontang"],
}
nama_depan   = ["Andi","Budi","Citra","Dedi","Eka","Fitra","Gita","Hendra","Indra","Joko",
                "Kiki","Lina","Made","Nanda","Oscar","Putri","Rama","Sari","Tono","Umar",
                "Vina","Wati","Yoga","Zaki","Agus","Bayu","Cici","Dian","Erna","Fajar",
                "Galih","Hani","Ivan","Jeni","Kartika","Lukman","Maya","Niko","Oky","Pipit",
                "Rendi","Sinta","Taufik","Ulfa","Vero","Wendi","Yudi","Zahra","Reza","Fitri"]
nama_belakang= ["Santoso","Wijaya","Pratama","Kusuma","Rahayu","Setiawan","Cahyono","Hartono",
                "Nugroho","Permata","Dewi","Susanto","Lestari","Purnama","Saputra","Wahyudi",
                "Hidayat","Andriani","Mukti","Suryadi"]

N = 80
random.shuffle(nama_depan)
names          = [f"{random.choice(nama_depan)} {random.choice(nama_belakang)}" for _ in range(N)]
wil_assigned   = [random.choice(wilayah_list) for _ in range(N)]
unit_assigned  = [random.choice(unit_map[w]) for w in wil_assigned]
agent_ids      = [f"AGT{1000+i}" for i in range(N)]

sales_volume      = np.random.randint(50, 500, N) * 1_000_000
jumlah_transaksi  = np.random.randint(50, 800, N)
hari_aktif        = np.random.randint(15, 30, N)
produk_digunakan  = np.random.randint(1, 6, N)
growth_mom        = np.random.uniform(-10, 40, N)
fee_income        = (sales_volume * np.random.uniform(0.005, 0.015, N)).astype(int)

baseline_trx  = (jumlah_transaksi * np.random.uniform(0.6, 0.95, N)).astype(int)
baseline_vol  = (sales_volume     * np.random.uniform(0.6, 0.95, N)).astype(int)
inc_trx_pct   = ((jumlah_transaksi - baseline_trx) / baseline_trx * 100).round(1)
inc_vol_pct   = ((sales_volume     - baseline_vol) / baseline_vol * 100).round(1)

# PRIMA Score = 70% transaksi + 30% volume (normalized)
trx_norm = (jumlah_transaksi - jumlah_transaksi.min()) / (jumlah_transaksi.max() - jumlah_transaksi.min()) * 100
vol_norm = (sales_volume     - sales_volume.min())     / (sales_volume.max()     - sales_volume.min())     * 100
prima_score = (0.70 * trx_norm + 0.30 * vol_norm).round(1)

# Health Score (5 komponen, tanpa cust baru)
freq_norm  = jumlah_transaksi / jumlah_transaksi.max() * 100
nom_norm   = sales_volume     / sales_volume.max()     * 100
prod_norm  = produk_digunakan / produk_digunakan.max() * 100
hari_norm  = hari_aktif       / hari_aktif.max()       * 100
grow_norm  = ((growth_mom - growth_mom.min()) / (growth_mom.max() - growth_mom.min()) * 100)

health_score = (
    0.30 * freq_norm +
    0.20 * nom_norm  +
    0.15 * prod_norm +
    0.10 * hari_norm +
    0.10 * grow_norm
).round(1)
# Rescale agar maks 100
health_score = (health_score / health_score.max() * 100).round(1)

def health_status(s):
    if s >= HEALTH_THRESH_HIJAU:  return "🟢 Sehat"
    elif s >= HEALTH_THRESH_KUNING: return "🟡 Perlu Perhatian"
    else: return "🔴 Butuh Bantuan"

def get_segment(hs, vol):
    if hs >= HEALTH_THRESH_HIJAU and vol >= VOL_CHAMPION: return "⭐ Champion"
    elif hs >= HEALTH_THRESH_HIJAU:                        return "🚀 Potensial"
    elif vol >= VOL_CHAMPION:                               return "💰 Volume Tinggi"
    else:                                                   return "💤 Tidak Aktif"

agent_df = pd.DataFrame({
    "Agent ID":            agent_ids,
    "Nama Agent":          names,
    "Wilayah":             wil_assigned,
    "Unit":                unit_assigned,
    "Sales Volume":        sales_volume,
    "Jumlah Transaksi":    jumlah_transaksi,
    "Hari Aktif":          hari_aktif,
    "Produk Digunakan":    produk_digunakan,
    "Growth MoM (%)":      growth_mom.round(1),
    "Fee Income":          fee_income,
    "Incr Trx (%)":        inc_trx_pct,
    "Incr Vol (%)":        inc_vol_pct,
    "MELESAT Score":       prima_score,
    "Health Score":        health_score,
    "Skor Frekuensi":      (0.30 * freq_norm).round(1),
    "Skor Volume":         (0.20 * nom_norm).round(1),
    "Skor Produk":         (0.15 * prod_norm).round(1),
    "Skor Hari Aktif":     (0.10 * hari_norm).round(1),
    "Skor Growth":         (0.10 * grow_norm).round(1),
})

agent_df["Status"]  = agent_df["Health Score"].apply(health_status)
agent_df["Segmen"]  = agent_df.apply(lambda r: get_segment(r["Health Score"], r["Sales Volume"]), axis=1)
agent_df = agent_df.sort_values("MELESAT Score", ascending=False).reset_index(drop=True)
agent_df["Rank"]    = range(1, N+1)
agent_df["Top20"]   = agent_df["Rank"] <= TOP_N
merah_df            = agent_df[agent_df["Status"] == "🔴 Butuh Bantuan"].copy()
TOP20               = agent_df[agent_df["Top20"]].copy()

# Simulasi data per periode (variasi kecil)
def make_period_df(seed_offset):
    np.random.seed(42 + seed_offset)
    vol_p   = (sales_volume  * np.random.uniform(0.75, 1.00, N)).astype(int)
    trx_p   = (jumlah_transaksi * np.random.uniform(0.75, 1.00, N)).astype(int)
    hs_p    = np.clip(health_score + np.random.uniform(-10, 10, N), 0, 100).round(1)
    ps_p    = np.clip(prima_score  + np.random.uniform(-8,  8,  N), 0, 100).round(1)
    df      = agent_df.copy()
    df["Sales Volume"]      = vol_p
    df["Jumlah Transaksi"]  = trx_p
    df["Health Score"]      = hs_p
    df["MELESAT Score"]     = ps_p
    df["Status"]            = df["Health Score"].apply(health_status)
    return df

period_data = {
    "Juni 2026":   agent_df,
    "Mei 2026":    make_period_df(1),
    "April 2026":  make_period_df(2),
    "Maret 2026":  make_period_df(3),
}

# =====================================================
# PLANT SVG HELPER
# =====================================================
def plant_svg(health: float) -> str:
    """Return SVG tanaman yang mencerminkan kondisi health score."""
    if health >= 75:
        # Berbunga lebat – semua hijau segar, bunga merah muda
        stem   = "#2e7d32"
        leaf1  = "#388e3c"; leaf2 = "#43a047"; leaf3 = "#66bb6a"
        flower = True; wilt = False
        pot    = "#5d4037"
        soil   = "#795548"
        glow   = "#a5d6a7"
        emoji_label = "🌸 Sehat & Berbunga!"
        bar_color = "#2e7d32"
    elif health >= 55:
        # Tumbuh baik, satu bunga
        stem   = "#388e3c"
        leaf1  = "#4caf50"; leaf2 = "#66bb6a"; leaf3 = "#81c784"
        flower = True; wilt = False
        pot    = "#5d4037"; soil = "#795548"; glow = "#c8e6c9"
        emoji_label = "🌿 Tumbuh Baik"
        bar_color = "#43a047"
    elif health >= HEALTH_THRESH_KUNING:
        # Kuning, belum layu tapi perlu air
        stem   = "#f9a825"
        leaf1  = "#fbc02d"; leaf2 = "#f9a825"; leaf3 = "#f57f17"
        flower = False; wilt = False
        pot    = "#6d4c41"; soil = "#8d6e63"; glow = "#fff9c4"
        emoji_label = "🌱 Butuh Perhatian"
        bar_color = "#f9a825"
    else:
        # Layu & kusam
        stem   = "#795548"
        leaf1  = "#a1887f"; leaf2 = "#8d6e63"; leaf3 = "#6d4c41"
        flower = False; wilt = True
        pot    = "#4e342e"; soil = "#6d4c41"; glow = "#efebe9"
        emoji_label = "🥀 Perlu Bantuan Segera"
        bar_color = "#c62828"

    wilt_transform_l = 'transform="rotate(30 90 160)"' if wilt else ""
    wilt_transform_r = 'transform="rotate(-30 110 130)"' if wilt else ""
    wilt_stem_d      = "M100 230 C95 180 90 150 100 80" if wilt else "M100 230 C100 190 100 160 100 80"

    flower_svg = ""
    if flower:
        flower_svg = f"""
        <circle cx="100" cy="58" r="10" fill="#e91e63" opacity=".9"/>
        <circle cx="88"  cy="66" r="8"  fill="#f06292" opacity=".85"/>
        <circle cx="112" cy="66" r="8"  fill="#f06292" opacity=".85"/>
        <circle cx="94"  cy="78" r="8"  fill="#f48fb1" opacity=".8"/>
        <circle cx="106" cy="78" r="8"  fill="#f48fb1" opacity=".8"/>
        <circle cx="100" cy="64" r="7"  fill="#fff176"/>
        """

    bar_w = max(4, int(health * 1.4))

    return f"""
    <svg viewBox="0 0 200 300" xmlns="http://www.w3.org/2000/svg" width="160" height="240">
      <!-- Glow background -->
      <ellipse cx="100" cy="150" rx="70" ry="80" fill="{glow}" opacity=".35"/>

      <!-- Stem -->
      <path d="{wilt_stem_d}" stroke="{stem}" stroke-width="6" fill="none" stroke-linecap="round"/>

      <!-- Leaves -->
      <ellipse cx="78" cy="150" rx="24" ry="10" fill="{leaf1}" opacity=".9" {wilt_transform_l}/>
      <ellipse cx="122" cy="125" rx="22" ry="9"  fill="{leaf2}" opacity=".85" {wilt_transform_r}/>
      <ellipse cx="76"  cy="105" rx="18" ry="8"  fill="{leaf3}" opacity=".8"/>

      <!-- Flower / No flower -->
      {flower_svg}

      <!-- Pot -->
      <rect x="72" y="230" width="56" height="36" rx="6" fill="{pot}"/>
      <rect x="66" y="224" width="68" height="12" rx="4" fill="{soil}"/>

      <!-- Health bar background -->
      <rect x="30" y="275" width="140" height="10" rx="5" fill="#e0e0e0"/>
      <rect x="30" y="275" width="{bar_w}" height="10" rx="5" fill="{bar_color}"/>

      <!-- Label -->
      <text x="100" y="298" text-anchor="middle" font-size="9" fill="#555" font-family="sans-serif">{emoji_label}  {health:.0f}/100</text>
    </svg>
    """

# =====================================================
# SESSION STATE
# =====================================================
if "view"      not in st.session_state: st.session_state.view = "landing"
if "page"      not in st.session_state: st.session_state.page = ""
if "agent_id"  not in st.session_state: st.session_state.agent_id = agent_df["Agent ID"].iloc[0]
if "periode"   not in st.session_state: st.session_state.periode = "Juni 2026"
if "wilayah_filter" not in st.session_state: st.session_state.wilayah_filter = "Semua"

# =====================================================
# ██████  LANDING PAGE
# =====================================================
if st.session_state.view == "landing":
    st.markdown("<br>", unsafe_allow_html=True)
    col_logo, _ = st.columns([3,1])
    with col_logo:
        st.markdown(f"""
        <div style='text-align:center; padding:20px 0'>
          <div style='font-size:52px'>🚀</div>
          <h1 style='color:#1a3a6b;font-size:40px;margin:0'>{PROGRAM_NAME}</h1>
          <p style='color:#555;font-size:16px;margin-top:6px'>{PROGRAM_FULL}</p>
          <p style='color:#F37021;font-weight:700;font-size:15px'>{PROGRAM_TAG}</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<h3 style='text-align:center;color:#1a3a6b;margin-top:10px'>Pilih Dashboard Anda</h3>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center;color:#888;margin-bottom:24px'>Klik salah satu kartu di bawah untuk mulai</p>", unsafe_allow_html=True)

    lc, rc = st.columns(2, gap="large")
    with lc:
        st.markdown("""
        <div class='view-card view-card-agent'>
          <div style='font-size:56px'>👤</div>
          <h2 style='color:#F37021;margin:8px 0'>Dashboard Agent</h2>
          <p style='color:#555;font-size:14px'>Lihat ranking, skor, dan performa<br>transaksi Anda secara mudah</p>
          <p style='background:#fff4ee;color:#F37021;border-radius:10px;padding:8px;font-size:13px;font-weight:600'>Untuk: Agen PNM</p>
        </div>""", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("👤  Masuk sebagai Agent", use_container_width=True, key="btn_agent"):
            st.session_state.view = "agent"
            st.session_state.page = "Beranda"
            st.rerun()

    with rc:
        st.markdown("""
        <div class='view-card view-card-kanpus'>
          <div style='font-size:56px'>🏢</div>
          <h2 style='color:#1a3a6b;margin:8px 0'>Dashboard Kantor Pusat</h2>
          <p style='color:#555;font-size:14px'>Pantau seluruh wilayah, unit, agent,<br>dan early warning secara menyeluruh</p>
          <p style='background:#eef2ff;color:#1a3a6b;border-radius:10px;padding:8px;font-size:13px;font-weight:600'>Untuk: Manajemen & Supervisor</p>
        </div>""", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🏢  Masuk sebagai Kantor Pusat", use_container_width=True, key="btn_kanpus"):
            st.session_state.view = "kanpus"
            st.session_state.page = "Overview"
            st.rerun()

    st.markdown("<br><hr>", unsafe_allow_html=True)
    st.markdown(f"<p style='text-align:center;color:#bbb;font-size:12px'>© 2026 {PROGRAM_NAME} – {PROGRAM_FULL} | Program Holding UMi BRI–PNM–Pegadaian</p>", unsafe_allow_html=True)
    st.stop()

# =====================================================
# SIDEBAR (setelah landing)
# =====================================================
with st.sidebar:
    if st.button("← Ganti Dashboard", key="back_landing"):
        st.session_state.view = "landing"
        st.rerun()

    st.markdown(f"<h2 style='color:white;margin:4px 0'>🚀 {PROGRAM_NAME}</h2>", unsafe_allow_html=True)
    st.markdown(f"<p style='color:#8ab4d4;font-size:11px;margin:0'>{PROGRAM_FULL}</p>", unsafe_allow_html=True)
    st.divider()

    # ---- Pilih Periode ----
    st.markdown("<b style='color:#8ab4d4;font-size:11px'>📅 PERIODE</b>", unsafe_allow_html=True)
    st.session_state.periode = st.selectbox("", PERIODE_LIST, label_visibility="collapsed",
                                            index=PERIODE_LIST.index(st.session_state.periode))
    st.divider()

    if st.session_state.view == "agent":
        # ---- Pilih Agent ----
        st.markdown("<b style='color:#8ab4d4;font-size:11px'>🔍 CARI AGENT</b>", unsafe_allow_html=True)
        search_q = st.text_input("", placeholder="Ketik nama agent...", label_visibility="collapsed")
        filtered_names = agent_df["Nama Agent"].tolist()
        if search_q:
            filtered_names = [n for n in filtered_names if search_q.lower() in n.lower()]
        if filtered_names:
            sel_name = st.selectbox("", filtered_names, label_visibility="collapsed")
            st.session_state.agent_id = agent_df[agent_df["Nama Agent"] == sel_name]["Agent ID"].iloc[0]
        else:
            st.warning("Agent tidak ditemukan")

        st.divider()
        st.markdown("<b style='color:#8ab4d4;font-size:11px'>📋 MENU</b>", unsafe_allow_html=True)
        agent_menus = [
            ("🏠  Beranda", "Beranda"),
            ("🏅  Top 20 Penerima Hadiah", "Top 20"),
            ("📊  Performa Saya", "Performa"),
            ("🎯  Target & Tantangan", "Target"),
        ]
        for label, val in agent_menus:
            if st.button(label, use_container_width=True, key=f"am_{val}"):
                st.session_state.page = val

    else:
        st.markdown("<b style='color:#8ab4d4;font-size:11px'>🗺️ FILTER WILAYAH</b>", unsafe_allow_html=True)
        st.session_state.wilayah_filter = st.selectbox(
            "", ["Semua"] + wilayah_list, label_visibility="collapsed",
            index=(["Semua"] + wilayah_list).index(st.session_state.wilayah_filter)
        )
        st.divider()
        st.markdown("<b style='color:#8ab4d4;font-size:11px'>📋 MENU</b>", unsafe_allow_html=True)
        kanpus_menus = [
            ("📊  Overview Nasional", "Overview"),
            ("🏅  Top 20 Penerima Hadiah", "Top 20 KP"),
            ("🗺️  Breakdown Wilayah & Unit", "Wilayah"),
            ("🔴  Early Warning", "Warning"),
            ("👤  Detail Agent", "Detail Agent"),
        ]
        for label, val in kanpus_menus:
            if st.button(label, use_container_width=True, key=f"km_{val}"):
                st.session_state.page = val

        if st.session_state.page == "Detail Agent":
            st.divider()
            st.markdown("<b style='color:#8ab4d4;font-size:11px'>🔍 CARI AGENT</b>", unsafe_allow_html=True)
            kp_search = st.text_input("", placeholder="Ketik nama...", label_visibility="collapsed", key="kp_search")
            kp_names  = agent_df["Nama Agent"].tolist()
            if kp_search:
                kp_names = [n for n in kp_names if kp_search.lower() in n.lower()]
            if kp_names:
                kp_sel = st.selectbox("", kp_names, label_visibility="collapsed", key="kp_sel")
                st.session_state.agent_id = agent_df[agent_df["Nama Agent"] == kp_sel]["Agent ID"].iloc[0]

    st.divider()
    mode_lbl = "👤 Agent" if st.session_state.view == "agent" else "🏢 Kantor Pusat"
    st.markdown(f"<small style='color:#8ab4d4'>Mode: {mode_lbl}<br>Periode: {st.session_state.periode}</small>", unsafe_allow_html=True)

# =====================================================
# DATA AKTIF (sesuai periode)
# =====================================================
cur_df = period_data[st.session_state.periode].copy()
cur_df = cur_df.sort_values("MELESAT Score", ascending=False).reset_index(drop=True)
cur_df["Rank"] = range(1, N+1)
cur_df["Top20"] = cur_df["Rank"] <= TOP_N
cur_merah  = cur_df[cur_df["Status"] == "🔴 Butuh Bantuan"].copy()
cur_top20  = cur_df[cur_df["Top20"]].copy()

if st.session_state.wilayah_filter != "Semua":
    cur_wil_df = cur_df[cur_df["Wilayah"] == st.session_state.wilayah_filter].copy()
else:
    cur_wil_df = cur_df.copy()

# =====================================================
# HEADER GLOBAL
# =====================================================
hc1, hc2, hc3, hc4 = st.columns([4,1,1,1])
with hc1:
    mode_lbl = "👤 Agent PNM" if st.session_state.view == "agent" else "🏢 Kantor Pusat"
    st.markdown(f"""
    <h1 style='color:#1a3a6b;margin-bottom:0'>🚀 {PROGRAM_NAME}
      <span style='font-size:16px;color:#F37021;font-weight:600'> {mode_lbl}</span>
    </h1>
    <p style='color:#888;font-size:12px;margin:0'>{PROGRAM_FULL} &nbsp;|&nbsp; {PROGRAM_TAG}</p>
    """, unsafe_allow_html=True)
with hc2:
    st.metric("Periode", st.session_state.periode)
with hc3:
    st.metric("Total Agent", f"{N}")
with hc4:
    wl = st.session_state.wilayah_filter if st.session_state.view == "kanpus" else "-"
    st.metric("Wilayah", wl)
st.divider()

# =====================================================
# ██████  AGENT VIEW
# =====================================================
if st.session_state.view == "agent":
    me = cur_df[cur_df["Agent ID"] == st.session_state.agent_id].iloc[0]
    hs = float(me["Health Score"])
    in_top20 = bool(me["Top20"])

    # ---- BERANDA ----
    if st.session_state.page == "Beranda":
        # Top banner status
        if in_top20:
            st.markdown(f"""
            <div style='background:linear-gradient(90deg,#f9a825,#ff6f00);border-radius:14px;padding:14px 22px;margin-bottom:12px;display:flex;align-items:center;gap:14px'>
              <span style='font-size:36px'>🏆</span>
              <div>
                <b style='color:white;font-size:18px'>SELAMAT! Anda masuk Top 20 Penerima Hadiah!</b><br>
                <span style='color:#fff8e1;font-size:14px'>Posisi #{int(me['Rank'])} dari {N} agent – Pertahankan terus!</span>
              </div>
            </div>""", unsafe_allow_html=True)
        else:
            gap = cur_df.iloc[TOP_N-1]["MELESAT Score"] - me["MELESAT Score"]
            st.markdown(f"""
            <div style='background:linear-gradient(90deg,#1a3a6b,#0d47a1);border-radius:14px;padding:14px 22px;margin-bottom:12px;display:flex;align-items:center;gap:14px'>
              <span style='font-size:36px'>🎯</span>
              <div>
                <b style='color:white;font-size:18px'>Anda di posisi #{int(me['Rank'])} — Belum masuk Top 20</b><br>
                <span style='color:#bbdefb;font-size:14px'>Butuh +{gap:.1f} poin lagi untuk masuk daftar penerima hadiah. Ayo semangat!</span>
              </div>
            </div>""", unsafe_allow_html=True)

        # KPI baris atas
        k1,k2,k3,k4 = st.columns(4)
        with k1: st.metric("🏅 Posisi Saya",     f"#{int(me['Rank'])} / {N}")
        with k2: st.metric("⭐ MELESAT Score",   f"{me['MELESAT Score']:.1f} poin")
        with k3: st.metric("💰 Total Transaksi",  f"{int(me['Jumlah Transaksi'])} kali")
        with k4: st.metric("💵 Sales Volume",     f"Rp {me['Sales Volume']/1e6:.0f} Jt")

        st.divider()

        # Baris utama: Tanaman + Breakdown
        pa, pb, pc = st.columns([1, 1.2, 1.5])

        with pa:
            st.markdown("<div class='section-header'>🌱 Kondisi Anda</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='plant-wrap'>{plant_svg(hs)}</div>", unsafe_allow_html=True)
            st.markdown(f"""
            <div style='text-align:center;margin-top:4px'>
              <span style='font-size:13px;color:#555'>Status: <b>{me['Status']}</b></span><br>
              <span style='font-size:13px;color:#555'>Health Score: <b>{hs:.0f} / 100</b></span>
            </div>""", unsafe_allow_html=True)

        with pb:
            st.markdown("<div class='section-header'>🧩 Apa yang Dinilai?</div>", unsafe_allow_html=True)
            st.markdown("<p style='font-size:12px;color:#888'>Hover/arahkan kursor ke tiap baris untuk keterangan</p>", unsafe_allow_html=True)

            komp_rows = [
                ("Frekuensi Transaksi", me["Skor Frekuensi"],  30, "Seberapa sering Anda bertransaksi. Makin sering, makin besar nilainya."),
                ("Nilai Transaksi",     me["Skor Volume"],      20, "Total uang yang ditransaksikan. Transaksi besar = skor besar."),
                ("Produk Digunakan",    me["Skor Produk"],      15, "Berapa jenis produk yang Anda pakai: transfer, pulsa, listrik, dll."),
                ("Hari Aktif",          me["Skor Hari Aktif"],  10, "Berapa hari dalam sebulan Anda aktif buka aplikasi dan transaksi."),
                ("Pertumbuhan",         me["Skor Growth"],      10, "Apakah transaksi Anda naik dibanding bulan lalu."),
            ]
            for nama_k, skor, maks_bobot, tooltip in komp_rows:
                pct = min(100, skor / maks_bobot * 100) if maks_bobot > 0 else 0
                bar_col = "#2e7d32" if pct >= 70 else ("#f9a825" if pct >= 40 else "#c62828")
                st.markdown(f"""
                <div style='margin-bottom:8px' title="{tooltip}">
                  <div style='display:flex;justify-content:space-between;font-size:13px'>
                    <span style='color:#333'>{nama_k}
                      <span style='font-size:11px;color:#aaa'> (maks {maks_bobot})</span>
                    </span>
                    <b style='color:{bar_col}'>{skor:.1f}</b>
                  </div>
                  <div style='background:#e0e0e0;border-radius:6px;height:8px;margin-top:3px'>
                    <div style='background:{bar_col};width:{pct:.0f}%;height:8px;border-radius:6px'></div>
                  </div>
                  <div style='font-size:10px;color:#aaa;font-style:italic;margin-top:1px'>{tooltip}</div>
                </div>
                """, unsafe_allow_html=True)

        with pc:
            st.markdown("<div class='section-header'>📊 Posisi vs Top 20</div>", unsafe_allow_html=True)
            plot_df = cur_df.head(TOP_N + 5).copy()
            colors  = ["#F37021" if r["Agent ID"] == me["Agent ID"] else ("#FFD700" if r["Top20"] else "#b0bec5")
                       for _, r in plot_df.iterrows()]
            fig = go.Figure(go.Bar(
                y=[f"#{int(r)} {n[:14]}" for r, n in zip(plot_df["Rank"], plot_df["Nama Agent"])],
                x=plot_df["MELESAT Score"],
                orientation="h",
                marker_color=colors,
                text=[f"{s:.0f}" for s in plot_df["MELESAT Score"]],
                textposition="outside"
            ))
            fig.update_layout(
                plot_bgcolor="white", paper_bgcolor="white",
                xaxis=dict(range=[0,115]), yaxis=dict(autorange="reversed"),
                height=370, margin=dict(t=10,b=10,l=10,r=30)
            )
            st.plotly_chart(fig, use_container_width=True)
            st.markdown(f"""
            <div style='font-size:12px;color:#888;text-align:center'>
              🟠 = Anda &nbsp; 🟡 = Top 20 &nbsp; ⬜ = Di luar Top 20
            </div>""", unsafe_allow_html=True)

        st.divider()

        # Info lengkap agent
        st.markdown("<div class='section-header'>📋 Info Lengkap Anda</div>", unsafe_allow_html=True)
        ia, ib = st.columns(2)
        info_items_a = [
            ("Agent ID",        me["Agent ID"]),
            ("Nama",            me["Nama Agent"]),
            ("Wilayah",         me["Wilayah"]),
            ("Unit",            me["Unit"]),
            ("Segmen",          me["Segmen"]),
        ]
        info_items_b = [
            ("Hari Aktif",      f"{int(me['Hari Aktif'])} hari / bulan"),
            ("Produk Digunakan",f"{int(me['Produk Digunakan'])} produk"),
            ("Growth MoM",      f"{me['Growth MoM (%)']:.1f}%"),
            ("Fee Income",      f"Rp {me['Fee Income']/1e6:.2f} Jt"),
            ("Naik vs Bulan Lalu", f"+{me['Incr Trx (%)']:.1f}% transaksi"),
        ]
        with ia:
            rows_html = "".join([f"<div class='info-row'><span class='info-label'>{k}</span><span class='info-value'>{v}</span></div>" for k,v in info_items_a])
            st.markdown(f"<div class='info-box'>{rows_html}</div>", unsafe_allow_html=True)
        with ib:
            rows_html = "".join([f"<div class='info-row'><span class='info-label'>{k}</span><span class='info-value'>{v}</span></div>" for k,v in info_items_b])
            st.markdown(f"<div class='info-box'>{rows_html}</div>", unsafe_allow_html=True)

    # ---- TOP 20 ----
    elif st.session_state.page == "Top 20":
        st.markdown(f"<div class='section-header'>🏅 Top 20 Penerima Hadiah MELESAT – {st.session_state.periode}</div>", unsafe_allow_html=True)
        st.caption("Formula: 70% Jumlah Transaksi + 30% Sales Volume (dinormalisasi 0–100)")

        my_rank = int(me["Rank"])
        if my_rank <= TOP_N:
            st.success(f"✅ Selamat! Anda ada di posisi #{my_rank} — Anda termasuk penerima hadiah!")
        else:
            gap = cur_df.iloc[TOP_N-1]["MELESAT Score"] - me["MELESAT Score"]
            st.warning(f"Posisi Anda: #{my_rank}. Perlu +{gap:.1f} poin lagi untuk masuk Top 20.")

        # Podium Top 3
        po1, po2, po3 = st.columns(3)
        medals = [("🥇","#FFD700","#7B3F00"), ("🥈","#C0C0C0","#333"), ("🥉","#CD7F32","white")]
        for col, i, (med, bg, fg) in zip([po2,po1,po3], [1,0,2], medals):
            r = cur_top20.iloc[i]
            with col:
                st.markdown(f"""
                <div style='background:{bg};border-radius:14px;padding:16px;text-align:center;color:{fg}'>
                  <div style='font-size:32px'>{med}</div>
                  <b style='font-size:15px'>{r['Nama Agent']}</b><br>
                  <span style='font-size:12px'>{r['Wilayah']} – {r['Unit']}</span><br>
                  <b style='font-size:18px'>{r['MELESAT Score']:.1f} poin</b><br>
                  <span style='font-size:11px'>{int(r['Jumlah Transaksi'])} trx | Rp {r['Sales Volume']/1e6:.0f} Jt</span>
                </div>""", unsafe_allow_html=True)

        st.divider()

        disp = cur_top20[["Rank","Nama Agent","Wilayah","Unit","MELESAT Score","Jumlah Transaksi","Sales Volume","Health Score","Status","Segmen"]].copy()
        disp["Sales Volume"] = disp["Sales Volume"].apply(lambda x: f"Rp {x/1e6:.0f} Jt")
        disp.columns = ["#","Nama","Wilayah","Unit","Skor","Transaksi","Sales Vol","Health","Status","Segmen"]

        def hl_me(row):
            return ["background:#fff8e1;font-weight:bold"]*len(row) if row["Nama"] == me["Nama Agent"] else [""]*len(row)

        st.dataframe(disp.style.apply(hl_me, axis=1), use_container_width=True, hide_index=True)

        fig = px.bar(
            cur_top20.sort_values("MELESAT Score"),
            x="MELESAT Score", y="Nama Agent", orientation="h",
            text="MELESAT Score", color="MELESAT Score",
            color_continuous_scale="Blues", title="MELESAT Score – Top 20"
        )
        fig.update_layout(plot_bgcolor="white", paper_bgcolor="white", height=560, xaxis=dict(range=[0,110]))
        st.plotly_chart(fig, use_container_width=True)

    # ---- PERFORMA ----
    elif st.session_state.page == "Performa":
        st.markdown(f"<div class='section-header'>📊 Performa Saya – {me['Nama Agent']} | {st.session_state.periode}</div>", unsafe_allow_html=True)

        k1,k2,k3,k4 = st.columns(4)
        with k1: st.metric("Jumlah Transaksi", f"{int(me['Jumlah Transaksi'])} kali", f"+{me['Incr Trx (%)']:.1f}% vs bln lalu")
        with k2: st.metric("Sales Volume",      f"Rp {me['Sales Volume']/1e6:.0f} Jt", f"+{me['Incr Vol (%)']:.1f}%")
        with k3: st.metric("Fee Income",         f"Rp {me['Fee Income']/1e6:.2f} Jt")
        with k4: st.metric("Hari Aktif",          f"{int(me['Hari Aktif'])} / 30 hari")

        st.divider()
        days = list(range(1,31))
        trx_d = [random.randint(int(me["Jumlah Transaksi"]*0.02), int(me["Jumlah Transaksi"]*0.06)) for _ in days]
        vol_d = [random.randint(int(me["Sales Volume"]*0.02), int(me["Sales Volume"]*0.06)) for _ in days]

        ca, cb = st.columns(2)
        with ca:
            df_t = pd.DataFrame({"Hari":days,"Transaksi":trx_d})
            fig  = px.area(df_t, x="Hari", y="Transaksi", title="Transaksi Harian")
            fig.update_traces(line_color="#1a3a6b", fillcolor="rgba(26,58,107,.12)")
            fig.update_layout(plot_bgcolor="white", paper_bgcolor="white", height=270)
            st.plotly_chart(fig, use_container_width=True)
        with cb:
            df_v = pd.DataFrame({"Hari":days,"Volume (Juta)":[v/1e6 for v in vol_d]})
            fig2 = px.area(df_v, x="Hari", y="Volume (Juta)", title="Sales Volume Harian")
            fig2.update_traces(line_color="#F37021", fillcolor="rgba(243,112,33,.12)")
            fig2.update_layout(plot_bgcolor="white", paper_bgcolor="white", height=270)
            st.plotly_chart(fig2, use_container_width=True)

        st.divider()
        st.markdown("<div class='section-header'>🛒 Jenis Transaksi Saya</div>", unsafe_allow_html=True)
        trx_types = pd.DataFrame({
            "Jenis":["Transfer","Top Up","Pulsa","Listrik/BPJS","Angsuran","Lainnya"],
            "Jumlah":[random.randint(10,100) for _ in range(6)]
        })
        fig3 = px.pie(trx_types, names="Jenis", values="Jumlah", hole=0.45,
                      color_discrete_sequence=["#1a3a6b","#2e7d32","#F37021","#f9a825","#6a1b9a","#0097a7"])
        fig3.update_layout(height=300)
        st.plotly_chart(fig3, use_container_width=True)

    # ---- TARGET ----
    elif st.session_state.page == "Target":
        st.markdown(f"<div class='section-header'>🎯 Target & Tantangan – {st.session_state.periode}</div>", unsafe_allow_html=True)

        target_trx = 600; target_vol = 400_000_000; target_health = 65.0
        pct_trx    = min(100, me["Jumlah Transaksi"] / target_trx * 100)
        pct_vol    = min(100, me["Sales Volume"]      / target_vol * 100)
        pct_health = min(100, hs / target_health * 100)
        pct_rank   = max(0, min(100, (N - me["Rank"]) / (N - TOP_N) * 100))

        ta, tb, tc, td = st.columns(4)
        with ta: st.metric("Transaksi",  f"{int(me['Jumlah Transaksi'])} / {target_trx}", f"{pct_trx:.0f}% tercapai")
        with tb: st.metric("Sales Vol",  f"Rp {me['Sales Volume']/1e6:.0f} / 400 Jt",    f"{pct_vol:.0f}%")
        with tc: st.metric("Health",     f"{hs:.0f} / {int(target_health)}",              f"{pct_health:.0f}%")
        with td: st.metric("Posisi",     f"#{int(me['Rank'])} → Top {TOP_N}",            "✅ Masuk!" if me["Rank"]<=TOP_N else "❌ Belum")

        st.divider()
        for label, pct in [("Jumlah Transaksi",pct_trx),("Sales Volume",pct_vol),("Health Score",pct_health),("Ranking ke Top 20",pct_rank)]:
            col_bar = "#2e7d32" if pct>=100 else ("#F37021" if pct>=60 else "#c62828")
            st.markdown(f"""
            <div style='margin-bottom:14px'>
              <div style='display:flex;justify-content:space-between;font-size:14px;font-weight:600'>
                <span>{label}</span><span style='color:{col_bar}'>{pct:.0f}%</span>
              </div>
              <div style='background:#e0e0e0;border-radius:8px;height:14px;margin-top:4px'>
                <div style='background:{col_bar};width:{pct:.0f}%;height:14px;border-radius:8px'></div>
              </div>
            </div>""", unsafe_allow_html=True)

        st.divider()
        st.markdown("#### 💡 Saran untuk Anda")
        if pct_trx < 100:
            st.info(f"📌 Tingkatkan transaksi **{target_trx - int(me['Jumlah Transaksi'])} kali lagi** bulan ini.")
        if pct_vol < 100:
            st.info(f"📌 Tambah sales volume **Rp {(target_vol - me['Sales Volume'])/1e6:.0f} Jt lagi**.")
        if hs < target_health:
            st.warning(f"🌱 Health Score Anda {hs:.0f}. Coba perbanyak jenis produk dan hari aktif transaksi.")
        if me["Rank"] <= TOP_N:
            st.success("🎉 Anda sudah masuk Top 20! Terus pertahankan!")
        else:
            n_up = int(me["Rank"]) - TOP_N
            st.error(f"🔴 Naik {n_up} peringkat lagi. Fokus perbanyak frekuensi transaksi harian.")

# =====================================================
# ██████  KANTOR PUSAT VIEW
# =====================================================
else:

    # ---- OVERVIEW ----
    if st.session_state.page == "Overview":
        st.markdown(f"<div class='section-header'>📊 Overview Nasional – {st.session_state.periode}</div>", unsafe_allow_html=True)
        if st.session_state.wilayah_filter != "Semua":
            st.info(f"Filter aktif: **{st.session_state.wilayah_filter}** — menampilkan data wilayah ini saja.")

        df_show = cur_wil_df

        tot_h   = (df_show["Status"]=="🟢 Sehat").sum()
        tot_k   = (df_show["Status"]=="🟡 Perlu Perhatian").sum()
        tot_m   = (df_show["Status"]=="🔴 Butuh Bantuan").sum()
        tot_vol = df_show["Sales Volume"].sum()
        tot_trx = df_show["Jumlah Transaksi"].sum()
        tot_fee = df_show["Fee Income"].sum()

        k1,k2,k3,k4,k5,k6 = st.columns(6)
        with k1: st.metric("Total Agent",       f"{len(df_show)}")
        with k2: st.metric("🟢 Sehat",          f"{tot_h}",  f"{tot_h/len(df_show)*100:.0f}%")
        with k3: st.metric("🟡 Perhatian",       f"{tot_k}", f"{tot_k/len(df_show)*100:.0f}%")
        with k4: st.metric("🔴 Butuh Bantuan",  f"{tot_m}",  f"{tot_m/len(df_show)*100:.0f}%")
        with k5: st.metric("Total Sales Vol",   f"Rp {tot_vol/1e9:.1f} M")
        with k6: st.metric("Total Fee Income",  f"Rp {tot_fee/1e9:.2f} M")

        st.divider()

        ca, cb, cc = st.columns(3)
        with ca:
            fig_s = px.pie(names=["🟢 Sehat","🟡 Perhatian","🔴 Butuh Bantuan"],
                           values=[tot_h,tot_k,tot_m],
                           color_discrete_sequence=["#2e7d32","#f9a825","#c62828"], hole=0.5,
                           title="Status Agent")
            fig_s.update_layout(height=280, margin=dict(t=30,b=10))
            st.plotly_chart(fig_s, use_container_width=True)
        with cb:
            seg_c = df_show["Segmen"].value_counts().reset_index()
            seg_c.columns = ["Segmen","Jumlah"]
            fig_sg = px.bar(seg_c, x="Segmen", y="Jumlah", color="Segmen",
                            color_discrete_sequence=["#1a3a6b","#F37021","#2e7d32","#9c27b0"],
                            title="Segmen Agent")
            fig_sg.update_layout(plot_bgcolor="white",paper_bgcolor="white",height=280,showlegend=False)
            st.plotly_chart(fig_sg, use_container_width=True)
        with cc:
            fig_h = px.histogram(df_show, x="Health Score", nbins=15,
                                 color_discrete_sequence=["#1a3a6b"], title="Distribusi Health Score")
            fig_h.update_layout(plot_bgcolor="white",paper_bgcolor="white",height=280)
            st.plotly_chart(fig_h, use_container_width=True)

        st.divider()
        st.markdown("<div class='section-header'>🗺️ Performa per Wilayah</div>", unsafe_allow_html=True)

        wil_sum = df_show.groupby("Wilayah").agg(
            Vol_M    =("Sales Volume", lambda x: x.sum()/1e6),
            Trx      =("Jumlah Transaksi","sum"),
            Health   =("Health Score","mean"),
            Merah    =("Status", lambda x: (x=="🔴 Butuh Bantuan").sum()),
            Agent    =("Agent ID","count"),
        ).reset_index().round(1)

        cw1, cw2 = st.columns(2)
        with cw1:
            fig_w = px.bar(wil_sum.sort_values("Vol_M"), x="Vol_M", y="Wilayah",
                           orientation="h", text_auto=".0f", color="Vol_M",
                           color_continuous_scale="Blues", title="Sales Volume per Wilayah (Juta Rp)")
            fig_w.update_layout(plot_bgcolor="white",paper_bgcolor="white",height=380)
            st.plotly_chart(fig_w, use_container_width=True)
        with cw2:
            fig_m = px.bar(wil_sum.sort_values("Merah",ascending=False), x="Merah", y="Wilayah",
                           orientation="h", text_auto="d", color="Merah",
                           color_continuous_scale="Reds", title="Agent Merah per Wilayah")
            fig_m.update_layout(plot_bgcolor="white",paper_bgcolor="white",height=380)
            st.plotly_chart(fig_m, use_container_width=True)

    # ---- TOP 20 KANPUS ----
    elif st.session_state.page == "Top 20 KP":
        st.markdown(f"<div class='section-header'>🏅 Top 20 Penerima Hadiah – {st.session_state.periode}</div>", unsafe_allow_html=True)
        st.caption("Formula MELESAT Score: 70% Jumlah Transaksi + 30% Sales Volume (normalized 0–100)")

        p1,p2,p3 = st.columns(3)
        for col, i, medal in zip([p2,p1,p3],[1,0,2],["🥈","🥇","🥉"]):
            r = cur_top20.iloc[i]
            bg = {"🥇":"#FFD700","🥈":"#e0e0e0","🥉":"#cd7f32"}[medal]
            with col:
                st.markdown(f"""
                <div style='background:{bg};border-radius:14px;padding:16px;text-align:center'>
                  <div style='font-size:28px'>{medal}</div>
                  <b style='font-size:15px'>{r['Nama Agent']}</b><br>
                  <span style='font-size:12px;color:#555'>{r['Wilayah']} – {r['Unit']}</span><br>
                  <b style='font-size:20px'>{r['MELESAT Score']:.1f} poin</b><br>
                  <span style='font-size:11px'>{int(r['Jumlah Transaksi'])} trx | Rp {r['Sales Volume']/1e6:.0f} Jt</span>
                </div>""", unsafe_allow_html=True)

        st.divider()
        disp = cur_top20[["Rank","Nama Agent","Wilayah","Unit","MELESAT Score","Jumlah Transaksi","Sales Volume","Health Score","Status","Segmen","Fee Income"]].copy()
        disp["Sales Volume"] = disp["Sales Volume"].apply(lambda x: f"Rp {x/1e6:.0f} Jt")
        disp["Fee Income"]   = disp["Fee Income"].apply(lambda x:   f"Rp {x/1e6:.2f} Jt")
        disp.columns = ["#","Nama","Wilayah","Unit","Skor","Trx","Sales Vol","Health","Status","Segmen","Fee"]
        st.dataframe(disp, use_container_width=True, hide_index=True)

        cq, cr = st.columns(2)
        with cq:
            fig = px.bar(cur_top20.sort_values("MELESAT Score"),
                         x="MELESAT Score", y="Nama Agent", orientation="h",
                         text="MELESAT Score", color="MELESAT Score",
                         color_continuous_scale="Blues", title="MELESAT Score Top 20")
            fig.update_layout(plot_bgcolor="white",paper_bgcolor="white",height=560,xaxis=dict(range=[0,110]))
            st.plotly_chart(fig, use_container_width=True)
        with cr:
            wil_t20 = cur_top20["Wilayah"].value_counts().reset_index()
            wil_t20.columns = ["Wilayah","Jumlah"]
            fig2 = px.pie(wil_t20, names="Wilayah", values="Jumlah", hole=0.4, title="Asal Wilayah Top 20")
            fig2.update_layout(height=280)
            st.plotly_chart(fig2, use_container_width=True)
            seg_t20 = cur_top20["Segmen"].value_counts().reset_index()
            seg_t20.columns = ["Segmen","Jumlah"]
            fig3 = px.bar(seg_t20, x="Segmen", y="Jumlah", color="Segmen", title="Segmen Agent Top 20")
            fig3.update_layout(plot_bgcolor="white",paper_bgcolor="white",height=240,showlegend=False)
            st.plotly_chart(fig3, use_container_width=True)

    # ---- BREAKDOWN WILAYAH & UNIT ----
    elif st.session_state.page == "Wilayah":
        st.markdown("<div class='section-header'>🗺️ Breakdown Wilayah & Unit</div>", unsafe_allow_html=True)
        st.caption(f"Periode: {st.session_state.periode} | Filter: {st.session_state.wilayah_filter}")

        wil_sum = cur_wil_df.groupby("Wilayah").agg(
            Agent    =("Agent ID","count"),
            Avg_Skor =("MELESAT Score","mean"),
            Avg_Hlth =("Health Score","mean"),
            Vol_M    =("Sales Volume", lambda x: x.sum()/1e6),
            Trx      =("Jumlah Transaksi","sum"),
            Fee_M    =("Fee Income", lambda x: x.sum()/1e6),
            Merah    =("Status", lambda x: (x=="🔴 Butuh Bantuan").sum()),
            Hijau    =("Status", lambda x: (x=="🟢 Sehat").sum()),
            Top20    =("Top20", "sum"),
        ).reset_index().round(1)

        wil_sum.columns = ["Wilayah","Agent","Avg Skor","Avg Health","Vol (Jt)","Total Trx","Fee (Jt)","🔴 Merah","🟢 Sehat","Top 20"]
        st.dataframe(wil_sum, use_container_width=True, hide_index=True)

        st.divider()
        sel_unit_wil = st.selectbox("📍 Pilih wilayah untuk lihat detail unit:", ["Semua"] + wilayah_list)
        unit_src     = cur_df if sel_unit_wil == "Semua" else cur_df[cur_df["Wilayah"]==sel_unit_wil]

        unit_sum = unit_src.groupby(["Wilayah","Unit"]).agg(
            Agent    =("Agent ID","count"),
            Avg_Skor =("MELESAT Score","mean"),
            Avg_Hlth =("Health Score","mean"),
            Vol_M    =("Sales Volume", lambda x: x.sum()/1e6),
            Trx      =("Jumlah Transaksi","sum"),
            Merah    =("Status", lambda x: (x=="🔴 Butuh Bantuan").sum()),
            Top20    =("Top20","sum"),
        ).reset_index().round(1)
        unit_sum.columns = ["Wilayah","Unit","Agent","Avg Skor","Avg Health","Vol (Jt)","Total Trx","🔴 Merah","Top 20"]
        st.dataframe(unit_sum, use_container_width=True, hide_index=True)

        st.divider()
        fig_sc = px.scatter(
            unit_src, x="Health Score", y="MELESAT Score",
            color="Status", size="Jumlah Transaksi",
            hover_data=["Nama Agent","Wilayah","Unit","Sales Volume"],
            color_discrete_map={"🟢 Sehat":"#2e7d32","🟡 Perlu Perhatian":"#f9a825","🔴 Butuh Bantuan":"#c62828"},
            title="Health Score vs MELESAT Score per Agent"
        )
        fig_sc.update_layout(plot_bgcolor="white",paper_bgcolor="white",height=430)
        st.plotly_chart(fig_sc, use_container_width=True)

    # ---- EARLY WARNING ----
    elif st.session_state.page == "Warning":
        df_m = cur_wil_df[cur_wil_df["Status"]=="🔴 Butuh Bantuan"].copy()
        st.markdown(f"<div class='section-header'>🔴 Early Warning – Agent Butuh Intervensi | {st.session_state.periode}</div>", unsafe_allow_html=True)

        if len(df_m) == 0:
            st.success("✅ Tidak ada agent berstatus Merah di filter ini. Semua sehat!")
        else:
            st.error(f"⚠️ Terdapat **{len(df_m)} agent berstatus MERAH** yang butuh tindakan segera.")

            em1,em2,em3,em4 = st.columns(4)
            with em1: st.metric("Agent Merah", f"{len(df_m)}")
            with em2: st.metric("Avg Health",   f"{df_m['Health Score'].mean():.1f}")
            with em3: st.metric("Avg Transaksi", f"{df_m['Jumlah Transaksi'].mean():.0f} kali")
            with em4: st.metric("Potensi Fee Hilang", f"Rp {(cur_df['Fee Income'].mean()-df_m['Fee Income'].mean())*len(df_m)/1e6:.1f} Jt")

            st.divider()

            disp_m = df_m[["Rank","Nama Agent","Wilayah","Unit","Health Score","MELESAT Score","Jumlah Transaksi","Sales Volume","Hari Aktif","Growth MoM (%)","Segmen"]].copy()
            disp_m["Sales Volume"] = disp_m["Sales Volume"].apply(lambda x: f"Rp {x/1e6:.0f} Jt")
            disp_m.columns = ["#","Nama","Wilayah","Unit","Health","Skor","Trx","Sales Vol","Hari Aktif","Growth%","Segmen"]
            st.dataframe(disp_m.sort_values("Health").reset_index(drop=True), use_container_width=True, hide_index=True)

            st.divider()
            ew1, ew2 = st.columns(2)
            with ew1:
                mw = df_m.groupby("Wilayah").size().reset_index(name="Jumlah")
                fig_ew = px.bar(mw.sort_values("Jumlah",ascending=False), x="Wilayah", y="Jumlah",
                                text_auto="d", color="Jumlah", color_continuous_scale="Reds",
                                title="Agent Merah per Wilayah")
                fig_ew.update_layout(plot_bgcolor="white",paper_bgcolor="white",height=300)
                st.plotly_chart(fig_ew, use_container_width=True)
            with ew2:
                ms = df_m.groupby("Segmen").size().reset_index(name="Jumlah")
                fig_es = px.pie(ms, names="Segmen", values="Jumlah", hole=0.45,
                                title="Segmen Agent Merah")
                fig_es.update_layout(height=300)
                st.plotly_chart(fig_es, use_container_width=True)

            st.divider()
            st.markdown("#### 📋 Panduan Intervensi")
            intervensi = {
                "💤 Tidak Aktif":    "Lakukan reactivation call + kunjungan mantri. Target minimal 5 transaksi/hari.",
                "💰 Volume Tinggi": "Dorong diversifikasi produk. Insentif berbasis kenaikan nominal transaksi.",
                "🚀 Potensial":     "Coaching intensif + akses produk baru. Potensi naik ke Champion.",
                "⭐ Champion":      "Monitor ketat & jadikan role model. Cari penyebab penurunan sementara.",
            }
            for seg, act in intervensi.items():
                cnt = (df_m["Segmen"]==seg).sum()
                if cnt > 0:
                    st.warning(f"**{seg}** ({cnt} agent): {act}")

            st.info("""
**Siklus Monitoring:**
🔴 Terdeteksi → 📋 Analisis → 👤 Intervensi Mantri → 📅 Monitor 7 Hari → ✅ Naik? Close : Eskalasi Wilayah
            """)

    # ---- DETAIL AGENT (KANPUS) ----
    elif st.session_state.page == "Detail Agent":
        me_kp = cur_df[cur_df["Agent ID"] == st.session_state.agent_id].iloc[0]
        hs_kp = float(me_kp["Health Score"])

        st.markdown(f"<div class='section-header'>👤 Detail Agent: {me_kp['Nama Agent']} | {st.session_state.periode}</div>", unsafe_allow_html=True)

        status_color = {"🟢 Sehat":"#2e7d32","🟡 Perlu Perhatian":"#f9a825","🔴 Butuh Bantuan":"#c62828"}
        sc = status_color.get(me_kp["Status"], "#555")
        st.markdown(f"""
        <div style='background:{sc};border-radius:12px;padding:10px 20px;margin-bottom:12px;color:white;display:inline-block;font-weight:700;font-size:15px'>
          {me_kp['Status']} &nbsp;|&nbsp; {me_kp['Segmen']} &nbsp;|&nbsp; Rank #{int(me_kp['Rank'])} dari {N}
        </div>""", unsafe_allow_html=True)

        d1,d2,d3,d4,d5 = st.columns(5)
        with d1: st.metric("MELESAT Score",  f"{me_kp['MELESAT Score']:.1f}")
        with d2: st.metric("Health Score",   f"{hs_kp:.1f}")
        with d3: st.metric("Transaksi",       f"{int(me_kp['Jumlah Transaksi'])} kali")
        with d4: st.metric("Sales Volume",    f"Rp {me_kp['Sales Volume']/1e6:.0f} Jt")
        with d5: st.metric("Fee Income",      f"Rp {me_kp['Fee Income']/1e6:.2f} Jt")

        st.divider()
        da, db, dc = st.columns([1, 1.2, 1.5])

        with da:
            st.markdown("**🌱 Kondisi Health**")
            st.markdown(f"<div class='plant-wrap'>{plant_svg(hs_kp)}</div>", unsafe_allow_html=True)

        with db:
            st.markdown("**🧩 Komponen Health Score**")
            komp_rows_kp = [
                ("Frekuensi Transaksi", me_kp["Skor Frekuensi"],  30, "Seberapa sering agent bertransaksi dalam sebulan."),
                ("Nilai Transaksi",     me_kp["Skor Volume"],      20, "Total nilai uang yang ditransaksikan."),
                ("Produk Digunakan",    me_kp["Skor Produk"],      15, "Jumlah jenis produk yang aktif digunakan agent."),
                ("Hari Aktif",          me_kp["Skor Hari Aktif"],  10, "Jumlah hari aktif bertransaksi dalam sebulan."),
                ("Pertumbuhan MoM",     me_kp["Skor Growth"],      10, "Pertumbuhan transaksi vs bulan lalu."),
            ]
            for nama_k, skor, maks_b, tooltip in komp_rows_kp:
                pct = min(100, skor/maks_b*100) if maks_b>0 else 0
                bar_col = "#2e7d32" if pct>=70 else ("#f9a825" if pct>=40 else "#c62828")
                st.markdown(f"""
                <div style='margin-bottom:8px' title="{tooltip}">
                  <div style='display:flex;justify-content:space-between;font-size:13px'>
                    <span>{nama_k}<span style='font-size:10px;color:#aaa'> (maks {maks_b})</span></span>
                    <b style='color:{bar_col}'>{skor:.1f}</b>
                  </div>
                  <div style='background:#e0e0e0;border-radius:6px;height:8px;margin-top:2px'>
                    <div style='background:{bar_col};width:{pct:.0f}%;height:8px;border-radius:6px'></div>
                  </div>
                  <div style='font-size:10px;color:#aaa;font-style:italic'>{tooltip}</div>
                </div>""", unsafe_allow_html=True)

        with dc:
            st.markdown("**📋 Info Lengkap**")
            info_kp = [
                ("Agent ID",       me_kp["Agent ID"]),
                ("Wilayah",        me_kp["Wilayah"]),
                ("Unit",           me_kp["Unit"]),
                ("Hari Aktif",     f"{int(me_kp['Hari Aktif'])} hari"),
                ("Produk",         f"{int(me_kp['Produk Digunakan'])} jenis"),
                ("Growth MoM",     f"{me_kp['Growth MoM (%)']:.1f}%"),
                ("Naik Trx",       f"+{me_kp['Incr Trx (%)']:.1f}% vs bln lalu"),
                ("Naik Volume",    f"+{me_kp['Incr Vol (%)']:.1f}%"),
            ]
            rows_html = "".join([f"<div class='info-row'><span class='info-label'>{k}</span><span class='info-value'>{v}</span></div>" for k,v in info_kp])
            st.markdown(f"<div class='info-box'>{rows_html}</div>", unsafe_allow_html=True)

            # Perbandingan vs rata-rata wilayah
            avg_wil = cur_df[cur_df["Wilayah"]==me_kp["Wilayah"]]
            st.markdown("**📊 vs Rata-rata Wilayah**")
            for metric, col_name, fmt in [
                ("MELESAT Score", "MELESAT Score", ".1f"),
                ("Health Score",  "Health Score",  ".1f"),
                ("Transaksi",     "Jumlah Transaksi", ".0f"),
            ]:
                avg_val  = avg_wil[col_name].mean()
                my_val   = float(me_kp[col_name])
                delta    = my_val - avg_val
                arrow    = "▲" if delta>=0 else "▼"
                col_d    = "#2e7d32" if delta>=0 else "#c62828"
                st.markdown(f"""
                <div style='display:flex;justify-content:space-between;font-size:13px;padding:4px 0;border-bottom:1px solid #f0f0f0'>
                  <span style='color:#888'>{metric}</span>
                  <span><b>{my_val:{fmt}}</b>
                    <span style='color:{col_d};font-size:11px'> {arrow}{abs(delta):{fmt}} vs avg {avg_val:{fmt}}</span>
                  </span>
                </div>""", unsafe_allow_html=True)

# =====================================================
# FOOTER
# =====================================================
st.markdown("---")
st.markdown(f"""
<div style='background:linear-gradient(90deg,#1a3a6b,#0d1f3c);color:white;padding:14px 24px;border-radius:12px;text-align:center'>
  <b>🚀 {PROGRAM_NAME}</b> – {PROGRAM_FULL}<br>
  <small>Top 20: 70% Jumlah Transaksi + 30% Sales Volume &nbsp;|&nbsp; Health Score: 5 Komponen &nbsp;|&nbsp; Program Holding UMi BRI–PNM–Pegadaian</small>
</div>
""", unsafe_allow_html=True)
