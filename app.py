import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import random

random.seed(42)
np.random.seed(42)

st.set_page_config(page_title="PRIMA Dashboard", page_icon="🏆", layout="wide")

st.markdown("""
<style>
.stApp {background-color:#f0f4f8;}
.block-container{padding-top:1rem;padding-left:2rem;padding-right:2rem;}
section[data-testid="stSidebar"]{background:linear-gradient(180deg,#00529C,#003B73);}
section[data-testid="stSidebar"] *{color:white !important;}
.stButton>button{width:100%;border-radius:10px;background:transparent;color:white;border:none;text-align:left;font-weight:600;padding:8px 12px;}
.stButton>button:hover{background:rgba(255,255,255,0.15);border-left:4px solid #F37021;}
div[data-testid="stMetric"]{background:white;border-left:5px solid #00529C;padding:10px;border-radius:10px;box-shadow:0 2px 8px rgba(0,0,0,.08);}
.top20-badge{background:linear-gradient(135deg,#FFD700,#FFA500);color:#7B3F00;font-weight:bold;padding:6px 14px;border-radius:20px;display:inline-block;font-size:13px;}
.rank-badge-1{background:#FFD700;color:#7B3F00;font-weight:bold;padding:4px 10px;border-radius:12px;}
.rank-badge-2{background:#C0C0C0;color:#333;font-weight:bold;padding:4px 10px;border-radius:12px;}
.rank-badge-3{background:#CD7F32;color:white;font-weight:bold;padding:4px 10px;border-radius:12px;}
.status-hijau{background:#d4edda;color:#155724;padding:4px 10px;border-radius:8px;font-weight:bold;}
.status-kuning{background:#fff3cd;color:#856404;padding:4px 10px;border-radius:8px;font-weight:bold;}
.status-merah{background:#f8d7da;color:#721c24;padding:4px 10px;border-radius:8px;font-weight:bold;}
.card-info{background:white;border-radius:12px;padding:16px;box-shadow:0 2px 8px rgba(0,0,0,.08);margin-bottom:10px;}
</style>
""", unsafe_allow_html=True)

# ==========================
# DATA DUMMY
# ==========================

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

random.shuffle(nama_depan)
N = 80
names = [f"{random.choice(nama_depan)} {random.choice(nama_belakang)}" for _ in range(N)]
wilayah_assigned = [random.choice(wilayah_list) for _ in range(N)]
unit_assigned = [random.choice(unit_map[w]) for w in wilayah_assigned]
agent_ids = [f"AGT{1000+i}" for i in range(N)]

sales_volume = np.random.randint(50, 500, N) * 1_000_000
jumlah_transaksi = np.random.randint(50, 800, N)
hari_aktif = np.random.randint(15, 30, N)
customer_baru = np.random.randint(0, 50, N)
produk_digunakan = np.random.randint(1, 6, N)
growth_mom = np.random.uniform(-10, 40, N)
fee_income = (sales_volume * np.random.uniform(0.005, 0.015, N)).astype(int)

# Baseline bulan lalu
baseline_trx = (jumlah_transaksi * np.random.uniform(0.6, 0.95, N)).astype(int)
baseline_vol = (sales_volume * np.random.uniform(0.6, 0.95, N)).astype(int)
incremental_trx_pct = ((jumlah_transaksi - baseline_trx) / baseline_trx * 100).round(1)
incremental_vol_pct = ((sales_volume - baseline_vol) / baseline_vol * 100).round(1)

# Score PRIMA = 70% jumlah transaksi (normalized) + 30% sales volume (normalized)
trx_norm = (jumlah_transaksi - jumlah_transaksi.min()) / (jumlah_transaksi.max() - jumlah_transaksi.min()) * 100
vol_norm = (sales_volume - sales_volume.min()) / (sales_volume.max() - sales_volume.min()) * 100
prima_score = (0.70 * trx_norm + 0.30 * vol_norm).round(1)

# Agent Health Score = 30% frekuensi + 20% nominal + 15% produk + 15% cust baru + 10% hari aktif + 10% growth
freq_norm = (jumlah_transaksi / jumlah_transaksi.max() * 100)
nom_norm   = (sales_volume / sales_volume.max() * 100)
prod_norm  = (produk_digunakan / produk_digunakan.max() * 100)
cust_norm  = (customer_baru / customer_baru.max() * 100)
hari_norm  = (hari_aktif / hari_aktif.max() * 100)
grow_norm  = ((growth_mom - growth_mom.min()) / (growth_mom.max() - growth_mom.min()) * 100)

health_score = (
    0.30 * freq_norm + 0.20 * nom_norm + 0.15 * prod_norm +
    0.15 * cust_norm + 0.10 * hari_norm + 0.10 * grow_norm
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
    "Customer Baru": customer_baru,
    "Produk Digunakan": produk_digunakan,
    "Growth MoM (%)": growth_mom.round(1),
    "Fee Income (Rp)": fee_income,
    "Incremental Trx (%)": incremental_trx_pct,
    "Incremental Vol (%)": incremental_vol_pct,
    "PRIMA Score": prima_score,
    "Health Score": health_score,
})

agent_df["Status"] = agent_df["Health Score"].apply(health_status)
agent_df["Segmen"] = agent_df.apply(lambda r: segment(r["Health Score"], r["Sales Volume (Rp)"]), axis=1)
agent_df = agent_df.sort_values("PRIMA Score", ascending=False).reset_index(drop=True)
agent_df["Rank"] = range(1, len(agent_df) + 1)
agent_df["Top 20"] = agent_df["Rank"] <= 20

TOP20    = agent_df[agent_df["Top 20"]].copy()
merah_df = agent_df[agent_df["Status"] == "🔴 Merah"].copy()

# ==========================
# SESSION STATE
# ==========================
if "view" not in st.session_state:
    st.session_state.view = "agent"
if "page" not in st.session_state:
    st.session_state.page = "Beranda"
if "selected_agent_id" not in st.session_state:
    st.session_state.selected_agent_id = agent_df["Agent ID"].iloc[0]

# ==========================
# SIDEBAR
# ==========================
with st.sidebar:
    st.markdown("<h2 style='color:white;margin-bottom:0'>🏆 PRIMA</h2>", unsafe_allow_html=True)
    st.markdown("<p style='color:#acd4f5;font-size:12px'>PNM Revenue Improvement through<br>Merchant & Agent Acceleration</p>", unsafe_allow_html=True)
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
            index=agent_df[agent_df["Agent ID"] == st.session_state.selected_agent_id].index[0]
        )
        st.session_state.selected_agent_id = agent_df[agent_df["Nama Agent"] == selected_name]["Agent ID"].iloc[0]

    else:
        st.markdown("<b style='color:#acd4f5;font-size:12px'>MENU KANTOR PUSAT</b>", unsafe_allow_html=True)
        kanpus_menus = [
            ("📊 Overview Nasional", "Overview"),
            ("🏅 Top 20 Penerima Hadiah", "Top 20 Penerima Hadiah"),
            ("🗺️ Breakdown Wilayah", "Breakdown Wilayah"),
            ("🔴 Early Warning", "Early Warning"),
            ("📈 KPI Balanced", "KPI Balanced"),
        ]
        for label, val in kanpus_menus:
            if st.button(label, use_container_width=True):
                st.session_state.page = val

    st.divider()
    st.markdown(f"<small style='color:#acd4f5'>Mode: {'👤 Agent PNM' if st.session_state.view=='agent' else '🏢 Kantor Pusat'}</small>", unsafe_allow_html=True)
    st.markdown("<small style='color:#acd4f5'>Periode: Juni 2026</small>", unsafe_allow_html=True)

# ==========================
# HEADER
# ==========================
h1, h2, h3 = st.columns([4, 1, 1])
with h1:
    mode_label = "👤 Agent PNM View" if st.session_state.view == "agent" else "🏢 Kantor Pusat View"
    st.markdown(
        f"<h1 style='color:#00529C;margin-bottom:0'>PRIMA <span style='color:#F37021;font-size:18px'>{mode_label}</span></h1>"
        "<p style='color:gray;font-size:13px'>More Active Agents, More Valuable Transactions | Program PRIMA – PNM Holding BRI</p>",
        unsafe_allow_html=True
    )
with h2:
    st.metric("Periode", "Jun 2026")
with h3:
    st.metric("Total Agent", f"{N} Agent")

st.divider()

# ==========================
# ========== AGENT VIEW ==========
# ==========================
if st.session_state.view == "agent":

    me = agent_df[agent_df["Agent ID"] == st.session_state.selected_agent_id].iloc[0]

    # ---- BERANDA ----
    if st.session_state.page == "Beranda":
        st.subheader(f"Selamat Datang, {me['Nama Agent']} 👋")

        in_top20 = me["Top 20"]
        if in_top20:
            st.markdown(f"<div class='top20-badge'>🎉 SELAMAT! Anda masuk TOP 20 penerima hadiah PRIMA! (Rank #{int(me['Rank'])})</div><br>", unsafe_allow_html=True)
        else:
            gap = agent_df.iloc[19]["PRIMA Score"] - me["PRIMA Score"]
            st.warning(f"⚠️ Anda belum masuk Top 20. Butuh **+{gap:.1f} poin PRIMA** lagi untuk masuk daftar penerima hadiah.")

        k1,k2,k3,k4,k5 = st.columns(5)
        with k1:
            st.metric("🏅 Rank Anda", f"#{int(me['Rank'])} / {N}")
        with k2:
            st.metric("⭐ PRIMA Score", f"{me['PRIMA Score']:.1f}")
        with k3:
            st.metric("💚 Health Score", f"{me['Health Score']:.1f}", me["Status"])
        with k4:
            st.metric("💰 Sales Volume", f"Rp {me['Sales Volume (Rp)']/1e6:.0f} Jt")
        with k5:
            st.metric("🔁 Jumlah Transaksi", f"{int(me['Jumlah Transaksi'])} Trx")

        st.divider()

        c1, c2 = st.columns([1.2, 1])

        with c1:
            st.markdown("#### 📊 PRIMA Score Anda vs Top 20")
            top20_scores = agent_df.head(20)["PRIMA Score"].tolist()
            labels = [f"Rank {i+1}" for i in range(20)]
            colors = ["#F37021" if agent_df.iloc[i]["Agent ID"] == me["Agent ID"] else "#00529C" for i in range(20)]
            fig = go.Figure(go.Bar(
                x=labels, y=top20_scores,
                marker_color=colors,
                text=[f"{s:.1f}" for s in top20_scores],
                textposition="outside"
            ))
            fig.update_layout(
                plot_bgcolor="white", paper_bgcolor="white",
                yaxis=dict(range=[0, 110]),
                height=320, margin=dict(t=20, b=20)
            )
            st.plotly_chart(fig, use_container_width=True)

        with c2:
            st.markdown("#### 🧩 Breakdown PRIMA Score")
            trx_contrib = (0.70 * trx_norm[agent_df[agent_df["Agent ID"]==me["Agent ID"]].index[0]])
            vol_contrib = (0.30 * vol_norm[agent_df[agent_df["Agent ID"]==me["Agent ID"]].index[0]])
            fig2 = go.Figure(go.Pie(
                labels=["Jumlah Transaksi (70%)", "Sales Volume (30%)"],
                values=[trx_contrib, vol_contrib],
                hole=0.5,
                marker_colors=["#00529C", "#F37021"]
            ))
            fig2.update_layout(height=220, margin=dict(t=10, b=10), showlegend=True)
            st.plotly_chart(fig2, use_container_width=True)

            st.info(f"""
**Rincian Kontribusi:**
- Transaksi (70%): **{trx_contrib:.1f} poin**
- Sales Volume (30%): **{vol_contrib:.1f} poin**
- **Total: {me['PRIMA Score']:.1f} poin**
            """)

        st.divider()

        a1, a2 = st.columns(2)
        with a1:
            st.markdown("#### 🎯 Health Score Breakdown")
            idx = agent_df[agent_df["Agent ID"]==me["Agent ID"]].index[0]
            categories = ["Frekuensi Trx (30%)", "Nominal (20%)", "Produk (15%)", "Cust Baru (15%)", "Hari Aktif (10%)", "Growth (10%)"]
            values = [
                round(0.30 * freq_norm[idx], 1),
                round(0.20 * nom_norm[idx], 1),
                round(0.15 * prod_norm[idx], 1),
                round(0.15 * cust_norm[idx], 1),
                round(0.10 * hari_norm[idx], 1),
                round(0.10 * grow_norm[idx], 1),
            ]
            fig3 = go.Figure(go.Bar(
                y=categories, x=values, orientation="h",
                marker_color="#00529C", text=values, textposition="outside"
            ))
            fig3.update_layout(
                plot_bgcolor="white", paper_bgcolor="white",
                xaxis=dict(range=[0,35]), height=280, margin=dict(t=10,b=10)
            )
            st.plotly_chart(fig3, use_container_width=True)

        with a2:
            st.markdown("#### 📋 Info Detail Agent")
            st.markdown(f"""
<div class='card-info'>
<b>Agent ID:</b> {me['Agent ID']}<br>
<b>Nama:</b> {me['Nama Agent']}<br>
<b>Wilayah:</b> {me['Wilayah']}<br>
<b>Unit:</b> {me['Unit']}<br>
<b>Segmen:</b> {me['Segmen']}<br>
<b>Status:</b> {me['Status']}<br>
<b>Hari Aktif:</b> {int(me['Hari Aktif'])} hari<br>
<b>Customer Baru:</b> {int(me['Customer Baru'])} nasabah<br>
<b>Produk Digunakan:</b> {int(me['Produk Digunakan'])} produk<br>
<b>Growth MoM:</b> {me['Growth MoM (%)']:.1f}%<br>
<b>Fee Income:</b> Rp {me['Fee Income (Rp)']/1e6:.2f} Jt<br>
</div>
""", unsafe_allow_html=True)

    # ---- TOP 20 LEADERBOARD (AGENT VIEW) ----
    elif st.session_state.page == "Top 20 Leaderboard":
        st.subheader("🏅 Top 20 Penerima Hadiah PRIMA – Juni 2026")

        my_rank = int(me["Rank"])
        if my_rank <= 20:
            st.success(f"✅ Anda ada di posisi #{my_rank} — Selamat, Anda termasuk penerima hadiah!")
        else:
            gap = agent_df.iloc[19]["PRIMA Score"] - me["PRIMA Score"]
            st.warning(f"Posisi Anda: #{my_rank}. Butuh **+{gap:.1f} poin** untuk masuk Top 20.")

        display = TOP20[["Rank","Nama Agent","Wilayah","Unit","PRIMA Score","Jumlah Transaksi","Sales Volume (Rp)","Health Score","Status","Segmen"]].copy()
        display["Sales Volume (Rp)"] = display["Sales Volume (Rp)"].apply(lambda x: f"Rp {x/1e6:.0f} Jt")
        display["PRIMA Score"] = display["PRIMA Score"].round(1)
        display["Health Score"] = display["Health Score"].round(1)
        display.columns = ["#","Nama Agent","Wilayah","Unit","PRIMA Score","Transaksi","Sales Vol","Health","Status","Segmen"]

        def highlight_me(row):
            if row["Nama Agent"] == me["Nama Agent"]:
                return ["background-color: #fff3cd"] * len(row)
            return [""] * len(row)

        st.dataframe(display.style.apply(highlight_me, axis=1), use_container_width=True, hide_index=True)

        st.divider()
        fig = px.bar(
            TOP20.sort_values("PRIMA Score"),
            x="PRIMA Score", y="Nama Agent", orientation="h",
            text="PRIMA Score",
            color="PRIMA Score", color_continuous_scale="Blues",
            title="PRIMA Score – Top 20 Agent"
        )
        fig.update_layout(plot_bgcolor="white", paper_bgcolor="white", height=600, xaxis=dict(range=[0,110]))
        st.plotly_chart(fig, use_container_width=True)

    # ---- PERFORMA SAYA ----
    elif st.session_state.page == "Performa Saya":
        st.subheader(f"📊 Performa Saya – {me['Nama Agent']}")

        k1,k2,k3,k4 = st.columns(4)
        with k1: st.metric("Sales Volume", f"Rp {me['Sales Volume (Rp)']/1e6:.0f} Jt", f"+{me['Incremental Vol (%)']:.1f}% vs bulan lalu")
        with k2: st.metric("Jumlah Transaksi", f"{int(me['Jumlah Transaksi'])} Trx", f"+{me['Incremental Trx (%)']:.1f}% vs bulan lalu")
        with k3: st.metric("Fee Income", f"Rp {me['Fee Income (Rp)']/1e6:.2f} Jt")
        with k4: st.metric("Hari Aktif", f"{int(me['Hari Aktif'])} / 30 hari")

        st.divider()

        days = list(range(1, 31))
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
        st.subheader(f"🎯 Target & Progress – {me['Nama Agent']}")

        target_trx = 600
        target_vol = 400_000_000
        target_health = 65.0
        target_rank = 20

        p1,p2,p3,p4 = st.columns(4)
        pct_trx = min(100, me["Jumlah Transaksi"] / target_trx * 100)
        pct_vol = min(100, me["Sales Volume (Rp)"] / target_vol * 100)
        pct_health = min(100, me["Health Score"] / target_health * 100)
        pct_rank = max(0, min(100, (N - me["Rank"]) / (N - target_rank) * 100))

        with p1: st.metric("Transaksi", f"{int(me['Jumlah Transaksi'])} / {target_trx}", f"{pct_trx:.0f}% tercapai")
        with p2: st.metric("Sales Volume", f"Rp {me['Sales Volume (Rp)']/1e6:.0f} / 400 Jt", f"{pct_vol:.0f}% tercapai")
        with p3: st.metric("Health Score", f"{me['Health Score']:.1f} / {target_health}", f"{pct_health:.0f}% tercapai")
        with p4: st.metric("Target Rank", f"#{int(me['Rank'])} → Top {target_rank}", "✅ Masuk!" if me["Rank"] <= target_rank else "❌ Belum")

        st.divider()

        indicators = ["Transaksi", "Sales Volume", "Health Score", "Ranking Progress"]
        pct_values = [pct_trx, pct_vol, pct_health, pct_rank]
        colors_bar = ["#00529C" if p >= 100 else ("#F37021" if p >= 60 else "#dc3545") for p in pct_values]

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
            height=320, title="Progress Menuju Target Top 20",
            barmode="overlay"
        )
        st.plotly_chart(fig, use_container_width=True)

        st.divider()
        st.markdown("#### 💡 Rekomendasi Aksi")
        if pct_trx < 100:
            st.warning(f"📌 Tingkatkan transaksi sebanyak **{target_trx - int(me['Jumlah Transaksi'])} trx** lagi untuk mencapai target.")
        if pct_vol < 100:
            st.warning(f"📌 Tambah sales volume **Rp {(target_vol - me['Sales Volume (Rp)'])/1e6:.0f} Jt** lagi.")
        if me["Health Score"] < target_health:
            st.info(f"💡 Naikkan Health Score dari {me['Health Score']:.1f} → {target_health}. Fokus: tambah produk digunakan dan customer baru.")
        if me["Rank"] <= target_rank:
            st.success("🎉 Anda sudah masuk Top 20! Pertahankan dan tingkatkan posisi Anda!")
        else:
            st.error(f"🔴 Anda perlu naik **{int(me['Rank']) - target_rank} peringkat** lagi. Tingkatkan frekuensi transaksi harian.")

# ==========================
# ========== KANTOR PUSAT VIEW ==========
# ==========================
else:

    # ---- OVERVIEW ----
    if st.session_state.page == "Overview":
        st.subheader("📊 Overview Nasional PRIMA – Juni 2026")

        total_hijau = (agent_df["Status"] == "🟢 Hijau").sum()
        total_kuning = (agent_df["Status"] == "🟡 Kuning").sum()
        total_merah = (agent_df["Status"] == "🔴 Merah").sum()
        total_vol = agent_df["Sales Volume (Rp)"].sum()
        total_trx = agent_df["Jumlah Transaksi"].sum()
        total_fee = agent_df["Fee Income (Rp)"].sum()

        k1,k2,k3,k4,k5,k6 = st.columns(6)
        with k1: st.metric("Total Agent", f"{N}")
        with k2: st.metric("🟢 Aktif (Hijau)", f"{total_hijau}", f"{total_hijau/N*100:.0f}%")
        with k3: st.metric("🟡 Waspada", f"{total_kuning}", f"{total_kuning/N*100:.0f}%")
        with k4: st.metric("🔴 Butuh Intervensi", f"{total_merah}", f"{total_merah/N*100:.0f}%")
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
            seg_counts = agent_df["Segmen"].value_counts().reset_index()
            seg_counts.columns = ["Segmen","Jumlah"]
            fig_sg = px.bar(seg_counts, x="Segmen", y="Jumlah",
                            color="Segmen", color_discrete_sequence=["#00529C","#F37021","#198754","#6f42c1"])
            fig_sg.update_layout(plot_bgcolor="white", paper_bgcolor="white", height=280, showlegend=False)
            st.plotly_chart(fig_sg, use_container_width=True)

        with c3:
            st.markdown("#### Health Score Distribusi")
            fig_h = px.histogram(agent_df, x="Health Score", nbins=20,
                                 color_discrete_sequence=["#00529C"])
            fig_h.update_layout(plot_bgcolor="white", paper_bgcolor="white", height=280)
            st.plotly_chart(fig_h, use_container_width=True)

        st.divider()
        st.markdown("#### 🗺️ Sales Volume & Transaksi per Wilayah")

        wilayah_summary = agent_df.groupby("Wilayah").agg(
            Total_Vol=("Sales Volume (Rp)","sum"),
            Total_Trx=("Jumlah Transaksi","sum"),
            Avg_Health=("Health Score","mean"),
            Total_Agent=("Agent ID","count"),
            Agent_Merah=("Status", lambda x: (x=="🔴 Merah").sum())
        ).reset_index()
        wilayah_summary["Total_Vol_M"] = (wilayah_summary["Total_Vol"]/1e6).round(1)

        c4, c5 = st.columns(2)
        with c4:
            fig_w = px.bar(wilayah_summary.sort_values("Total_Vol"), x="Total_Vol_M", y="Wilayah",
                           orientation="h", text_auto=".0f", color="Total_Vol_M",
                           color_continuous_scale="Blues", title="Sales Volume per Wilayah (Juta Rp)")
            fig_w.update_layout(plot_bgcolor="white", paper_bgcolor="white", height=380)
            st.plotly_chart(fig_w, use_container_width=True)
        with c5:
            fig_w2 = px.bar(wilayah_summary.sort_values("Total_Trx"), x="Total_Trx", y="Wilayah",
                            orientation="h", text_auto="d", color="Total_Trx",
                            color_continuous_scale="Oranges", title="Jumlah Transaksi per Wilayah")
            fig_w2.update_layout(plot_bgcolor="white", paper_bgcolor="white", height=380)
            st.plotly_chart(fig_w2, use_container_width=True)

    # ---- TOP 20 PENERIMA HADIAH ----
    elif st.session_state.page == "Top 20 Penerima Hadiah":
        st.subheader("🏅 Top 20 Penerima Hadiah PRIMA – Juni 2026")
        st.caption("Formula: PRIMA Score = 70% Jumlah Transaksi (normalized) + 30% Sales Volume (normalized)")

        m1,m2,m3 = st.columns(3)
        with m1: st.metric("🥇 Rank 1", TOP20.iloc[0]["Nama Agent"], f"{TOP20.iloc[0]['PRIMA Score']:.1f} poin")
        with m2: st.metric("🥈 Rank 2", TOP20.iloc[1]["Nama Agent"], f"{TOP20.iloc[1]['PRIMA Score']:.1f} poin")
        with m3: st.metric("🥉 Rank 3", TOP20.iloc[2]["Nama Agent"], f"{TOP20.iloc[2]['PRIMA Score']:.1f} poin")

        st.divider()

        display_top = TOP20[[
            "Rank","Nama Agent","Wilayah","Unit","PRIMA Score",
            "Jumlah Transaksi","Sales Volume (Rp)","Health Score","Status","Segmen","Fee Income (Rp)"
        ]].copy()
        display_top["Sales Volume (Rp)"] = display_top["Sales Volume (Rp)"].apply(lambda x: f"Rp {x/1e6:.0f} Jt")
        display_top["Fee Income (Rp)"] = display_top["Fee Income (Rp)"].apply(lambda x: f"Rp {x/1e6:.2f} Jt")
        display_top.columns = ["#","Nama","Wilayah","Unit","PRIMA Score","Trx","Sales Vol","Health","Status","Segmen","Fee Income"]
        st.dataframe(display_top, use_container_width=True, hide_index=True)

        st.divider()

        c1, c2 = st.columns(2)
        with c1:
            fig = px.bar(
                TOP20.sort_values("PRIMA Score"),
                x="PRIMA Score", y="Nama Agent", orientation="h",
                text="PRIMA Score", color="PRIMA Score",
                color_continuous_scale="Blues", title="PRIMA Score Top 20 Agent"
            )
            fig.update_layout(plot_bgcolor="white", paper_bgcolor="white", height=600, xaxis=dict(range=[0,110]))
            st.plotly_chart(fig, use_container_width=True)

        with c2:
            st.markdown("#### Distribusi Wilayah Top 20")
            top20_wil = TOP20["Wilayah"].value_counts().reset_index()
            top20_wil.columns = ["Wilayah","Jumlah"]
            fig2 = px.pie(top20_wil, names="Wilayah", values="Jumlah", hole=0.4,
                          title="Asal Wilayah Top 20 Agent")
            fig2.update_layout(height=300)
            st.plotly_chart(fig2, use_container_width=True)

            st.markdown("#### Segmen Top 20")
            top20_seg = TOP20["Segmen"].value_counts().reset_index()
            top20_seg.columns = ["Segmen","Jumlah"]
            fig3 = px.bar(top20_seg, x="Segmen", y="Jumlah", color="Segmen",
                          title="Segmen Agent dalam Top 20")
            fig3.update_layout(plot_bgcolor="white", paper_bgcolor="white", height=280, showlegend=False)
            st.plotly_chart(fig3, use_container_width=True)

    # ---- BREAKDOWN WILAYAH ----
    elif st.session_state.page == "Breakdown Wilayah":
        st.subheader("🗺️ Breakdown per Wilayah & Unit")

        selected_wil = st.selectbox("Pilih Wilayah", ["Semua"] + wilayah_list)

        if selected_wil == "Semua":
            filtered = agent_df.copy()
        else:
            filtered = agent_df[agent_df["Wilayah"] == selected_wil]

        wil_summary = filtered.groupby("Wilayah").agg(
            Jumlah_Agent=("Agent ID","count"),
            Avg_PRIMA=("PRIMA Score","mean"),
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
        display_wil.columns = ["Wilayah","Agent","Avg PRIMA","Avg Health","Vol (Jt)","Trx","Fee (Jt)","🔴 Merah","🟢 Hijau","Top 20"]
        st.dataframe(display_wil, use_container_width=True, hide_index=True)

        st.divider()

        if selected_wil != "Semua":
            st.markdown(f"#### Detail Unit di {selected_wil}")
            unit_summary = filtered.groupby("Unit").agg(
                Jumlah_Agent=("Agent ID","count"),
                Avg_PRIMA=("PRIMA Score","mean"),
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
            d_unit.columns = ["Unit","Agent","Avg PRIMA","Avg Health","Vol (Jt)","Trx","🔴 Merah","Top 20"]
            st.dataframe(d_unit, use_container_width=True, hide_index=True)

            st.divider()
            st.markdown("#### Scatter: Health Score vs PRIMA Score")
            fig_sc = px.scatter(
                filtered, x="Health Score", y="PRIMA Score",
                color="Status", hover_data=["Nama Agent","Unit","Jumlah Transaksi","Sales Volume (Rp)"],
                color_discrete_map={"🟢 Hijau":"#198754","🟡 Kuning":"#ffc107","🔴 Merah":"#dc3545"},
                size="Jumlah Transaksi", title=f"Health vs PRIMA Score – {selected_wil}"
            )
            fig_sc.update_layout(plot_bgcolor="white", paper_bgcolor="white", height=450)
            st.plotly_chart(fig_sc, use_container_width=True)
        else:
            c1, c2 = st.columns(2)
            with c1:
                fig_a = px.bar(wil_summary.sort_values("Avg_PRIMA"), x="Avg_PRIMA", y="Wilayah",
                               orientation="h", text_auto=".1f", color="Avg_PRIMA",
                               color_continuous_scale="Blues", title="Rata-rata PRIMA Score per Wilayah")
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
        st.subheader("🔴 Early Warning – Agent Butuh Intervensi")

        total_merah = len(merah_df)
        st.error(f"⚠️ Terdapat **{total_merah} agent berstatus MERAH** yang membutuhkan intervensi segera.")

        m1,m2,m3,m4 = st.columns(4)
        with m1: st.metric("Agent Merah", f"{total_merah}")
        with m2: st.metric("Avg Health Score", f"{merah_df['Health Score'].mean():.1f}")
        with m3: st.metric("Avg Transaksi", f"{merah_df['Jumlah Transaksi'].mean():.0f} Trx")
        with m4: st.metric("Total Loss Fee Potential", f"Rp {(agent_df['Fee Income (Rp)'].mean() - merah_df['Fee Income (Rp)'].mean()) * total_merah / 1e6:.1f} Jt")

        st.divider()

        display_merah = merah_df[[
            "Rank","Nama Agent","Wilayah","Unit","Health Score","PRIMA Score",
            "Jumlah Transaksi","Sales Volume (Rp)","Hari Aktif","Growth MoM (%)","Segmen"
        ]].copy()
        display_merah["Sales Volume (Rp)"] = display_merah["Sales Volume (Rp)"].apply(lambda x: f"Rp {x/1e6:.0f} Jt")
        display_merah["Growth MoM (%)"] = display_merah["Growth MoM (%)"].round(1)
        display_merah.columns = ["Rank","Nama Agent","Wilayah","Unit","Health","PRIMA Score",
                                   "Trx","Sales Vol","Hari Aktif","Growth %","Segmen"]
        st.dataframe(display_merah.sort_values("Health").reset_index(drop=True), use_container_width=True, hide_index=True)

        st.divider()

        c1, c2 = st.columns(2)
        with c1:
            merah_wil = merah_df.groupby("Wilayah").size().reset_index(name="Jumlah")
            fig_ew = px.bar(merah_wil.sort_values("Jumlah", ascending=False),
                            x="Wilayah", y="Jumlah", text_auto="d",
                            color="Jumlah", color_continuous_scale="Reds",
                            title="Distribusi Agent Merah per Wilayah")
            fig_ew.update_layout(plot_bgcolor="white", paper_bgcolor="white", height=320)
            st.plotly_chart(fig_ew, use_container_width=True)

        with c2:
            merah_seg = merah_df.groupby("Segmen").size().reset_index(name="Jumlah")
            fig_es = px.pie(merah_seg, names="Segmen", values="Jumlah", hole=0.45,
                            title="Segmen Agent Merah",
                            color_discrete_sequence=["#dc3545","#fd7e14","#6f42c1","#0dcaf0"])
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
            count = (merah_df["Segmen"] == seg).sum()
            if count > 0:
                st.warning(f"**{seg}** ({count} agent): {action}")

        st.divider()
        st.markdown("#### 🔄 Monitoring Cycle Early Warning")
        st.info("""
**Alur Intervensi:**

🔴 Agent Merah Terdeteksi
↓
📋 Analisis Penyebab (Dashboard: hari aktif, frekuensi, produk)
↓
👤 Mantri / Supervisor Melakukan Kunjungan / Intervensi
↓
📅 Monitoring 7 Hari
↓
✅ Naik ke Kuning/Hijau → Close  |  ❌ Tetap Merah → Eskalasi ke Wilayah
        """)

    # ---- KPI BALANCED ----
    elif st.session_state.page == "KPI Balanced":
        st.subheader("📈 KPI Balanced Scorecard PRIMA")

        total_vol = agent_df["Sales Volume (Rp)"].sum()
        total_trx = agent_df["Jumlah Transaksi"].sum()
        total_fee = agent_df["Fee Income (Rp)"].sum()
        active_agent = (agent_df["Status"] != "🔴 Merah").sum()
        avg_rev_per_agent = total_fee / N

        tab1, tab2, tab3, tab4 = st.tabs(["💰 Financial", "👥 Customer", "⚙️ Operational", "🛡️ Risk"])

        with tab1:
            st.markdown("### 💰 Financial Perspective")
            f1,f2,f3 = st.columns(3)
            with f1: st.metric("Total Fee Based Income", f"Rp {total_fee/1e9:.3f} M")
            with f2: st.metric("Revenue per Agent (Avg)", f"Rp {avg_rev_per_agent/1e6:.2f} Jt")
            with f3: st.metric("Cost per Transaction (Est.)", "Rp 2.500")
            fig_f = px.bar(
                agent_df.groupby("Wilayah")["Fee Income (Rp)"].sum().reset_index().assign(**{"Fee (Jt)": lambda d: d["Fee Income (Rp)"]/1e6}),
                x="Wilayah", y="Fee (Jt)", text_auto=".1f", color="Fee (Jt)",
                color_continuous_scale="Blues", title="Fee Income per Wilayah (Juta Rp)"
            )
            fig_f.update_layout(plot_bgcolor="white", paper_bgcolor="white", height=350)
            st.plotly_chart(fig_f, use_container_width=True)

        with tab2:
            st.markdown("### 👥 Customer Perspective")
            c1,c2,c3 = st.columns(3)
            with c1: st.metric("Total Customer Baru", f"{agent_df['Customer Baru'].sum():,}")
            with c2: st.metric("Avg Customer Baru / Agent", f"{agent_df['Customer Baru'].mean():.1f}")
            with c3: st.metric("Repeat Trx Rate (Est.)", "68.4%")
            fig_c = px.scatter(
                agent_df, x="Customer Baru", y="Fee Income (Rp)",
                color="Status", size="Jumlah Transaksi",
                color_discrete_map={"🟢 Hijau":"#198754","🟡 Kuning":"#ffc107","🔴 Merah":"#dc3545"},
                hover_data=["Nama Agent","Wilayah"],
                title="Korelasi Customer Baru vs Fee Income"
            )
            fig_c.update_layout(plot_bgcolor="white", paper_bgcolor="white", height=400)
            st.plotly_chart(fig_c, use_container_width=True)

        with tab3:
            st.markdown("### ⚙️ Operational Perspective")
            o1,o2,o3 = st.columns(3)
            with o1: st.metric("Active Agent Ratio", f"{active_agent/N*100:.1f}%", f"{active_agent}/{N}")
            with o2: st.metric("Avg Trx / Active Agent", f"{total_trx/active_agent:.0f} Trx")
            with o3: st.metric("Avg Produk / Agent", f"{agent_df['Produk Digunakan'].mean():.1f}")

            prod_dist = agent_df["Produk Digunakan"].value_counts().reset_index()
            prod_dist.columns = ["Jumlah Produk","Jumlah Agent"]
            fig_o = px.bar(prod_dist.sort_values("Jumlah Produk"),
                           x="Jumlah Produk", y="Jumlah Agent", text_auto="d",
                           color="Jumlah Produk", color_continuous_scale="Purples",
                           title="Distribusi Jumlah Produk yang Digunakan per Agent")
            fig_o.update_layout(plot_bgcolor="white", paper_bgcolor="white", height=350)
            st.plotly_chart(fig_o, use_container_width=True)

        with tab4:
            st.markdown("### 🛡️ Risk Perspective")
            r1,r2,r3 = st.columns(3)
            with r1: st.metric("Agent Merah (Risiko Tinggi)", f"{len(merah_df)}", f"{len(merah_df)/N*100:.1f}%")
            with r2: st.metric("Fraud Rate (Est.)", "0.12%")
            with r3: st.metric("Failed Trx Rate (Est.)", "1.8%")

            fig_r = px.scatter(
                agent_df, x="PRIMA Score", y="Health Score",
                color="Status", size="Sales Volume (Rp)",
                color_discrete_map={"🟢 Hijau":"#198754","🟡 Kuning":"#ffc107","🔴 Merah":"#dc3545"},
                hover_data=["Nama Agent","Wilayah"],
                title="Risk Matrix: PRIMA Score vs Health Score"
            )
            fig_r.add_hline(y=40, line_dash="dash", line_color="red", annotation_text="Threshold Merah (40)")
            fig_r.add_hline(y=65, line_dash="dash", line_color="green", annotation_text="Threshold Hijau (65)")
            fig_r.update_layout(plot_bgcolor="white", paper_bgcolor="white", height=420)
            st.plotly_chart(fig_r, use_container_width=True)

# ==========================
# FOOTER
# ==========================
st.markdown("---")
st.markdown(
    "<div style='background:linear-gradient(90deg,#00529C,#003B73);color:white;padding:12px 20px;border-radius:10px;text-align:center'>"
    "<b>PRIMA Dashboard</b> – PNM Revenue Improvement through Merchant & Agent Acceleration<br>"
    "<small>Top 20: 70% Jumlah Transaksi + 30% Sales Volume | Health Score: 6 Dimensi | Program Holding UMi BRI–PNM–Pegadaian</small>"
    "</div>",
    unsafe_allow_html=True
)
