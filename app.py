
import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="Liga Mantri",
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
# NAVIGASI
# ==========================
if "page" not in st.session_state:
    st.session_state.page = "Overview"

with st.sidebar:
    st.title("🏆 Liga Mantri")
    st.caption("Performance Dashboard")
    st.divider()

    menus = [
        ("🏠 Overview","Overview"),
        ("🏅 Leaderboard Unit","Leaderboard Unit"),
        ("👨‍💼 Leaderboard Mantri","Leaderboard Mantri"),
        ("📈 Kontribusi Unit","Kontribusi Unit"),
        ("🔥 Top Performer","Top Performer"),
    ]

    for label, value in menus:
        if st.button(label, use_container_width=True):
            st.session_state.page = value

    st.divider()
    st.info(f"Halaman Aktif:\n\n**{st.session_state.page}**")

# ==========================
# HEADER
# ==========================
h1, h2 = st.columns([5,1])
with h1:
    st.markdown(
        "<h1 style='color:#00529C;margin-bottom:0'>Liga <span style='color:#F37021'>Mantri</span></h1>"
        "<p style='color:gray'>Performance & Leaderboard Dashboard</p>",
        unsafe_allow_html=True
    )
with h2:
    st.metric("Periode","Jun 2026")

st.divider()

# ==========================
# OVERVIEW
# ==========================
if st.session_state.page == "Overview":

    k1,k2,k3,k4,k5 = st.columns(5)
    k1.metric("🏅 Ranking","#4 / 23","+2")
    k2.metric("📈 Growth","+18.5%")
    k3.metric("💰 Outstanding","Rp18,2 M")
    k4.metric("🟢 Quality","98.4%")

    leaderboard = pd.DataFrame({
        "Unit":["Purwokerto Timur","Sokaraja","Ajibarang","⭐ Unit Anda","Cilongok"],
        "Score":[1020,980,945,910,875]
    })

    trend = pd.DataFrame({
        "Bulan":["Jan","Feb","Mar","Apr","Mei","Jun"],
        "Ranking":[8,7,6,5,4,4]
    })

    kontribusi = pd.DataFrame({
        "Mantri":["Andi","Budi","Citra","Dedi","Eko"],
        "Kontribusi":[32,24,18,15,11]
    })

    c1,c2 = st.columns([2,1])

    with c1:
        st.subheader("🏅 Leaderboard Unit")
        fig = px.bar(
            leaderboard.sort_values("Score"),
            x="Score",
            y="Unit",
            orientation="h",
            text="Score"
        )
        fig.update_traces(marker_color="#00529C")
        fig.update_layout(plot_bgcolor="white",paper_bgcolor="white")
        st.plotly_chart(fig,use_container_width=True)

    with c2:
        st.subheader("📈 Trend Ranking")
        fig2 = px.line(trend,x="Bulan",y="Ranking",markers=True)
        fig2.update_yaxes(autorange="reversed")
        fig2.update_traces(line_color="#00529C")
        st.plotly_chart(fig2,use_container_width=True)

    a,b = st.columns([2,1])

    with a:
        st.subheader("👨‍💼 Kontribusi Mantri")
        fig3 = px.bar(
            kontribusi.sort_values("Kontribusi"),
            x="Kontribusi",
            y="Mantri",
            orientation="h",
            text="Kontribusi"
        )
        fig3.update_traces(marker_color="#F37021")
        st.plotly_chart(fig3,use_container_width=True)

    with b:
        st.subheader("🔥 Top Performer")
        st.metric("🥇 Andi","945 Poin")
        st.metric("🥈 Budi","902 Poin")
        st.metric("🥉 Citra","875 Poin")

    st.info("""
**Insight Bulan Ini**

- Unit Anda berada di peringkat 4 dari 23.
- Naik 2 peringkat dibanding bulan lalu.
- Dibutuhkan tambahan 35 poin untuk masuk Top 3.
- Andi menjadi kontributor terbesar (32%).
""")

elif st.session_state.page == "Leaderboard Unit":

    st.header("🏅 Leaderboard Unit")

    df = pd.DataFrame({
        "Ranking":[1,2,3,4,5],
        "Unit":["Purwokerto Timur","Sokaraja","Ajibarang","⭐ Unit Anda","Cilongok"],
        "Liga Score":[1020,980,945,910,875]
    })

    st.dataframe(df,use_container_width=True,hide_index=True)

    fig = px.bar(df.sort_values("Liga Score"),
                 x="Liga Score",
                 y="Unit",
                 orientation="h",
                 text="Liga Score")
    fig.update_traces(marker_color="#00529C")
    st.plotly_chart(fig,use_container_width=True)

elif st.session_state.page == "Leaderboard Mantri":

    st.header("👨‍💼 Leaderboard Mantri")

    df = pd.DataFrame({
        "Ranking":[1,2,3,4,5],
        "Nama":["Andi","Budi","Citra","Dedi","Eko"],
        "Unit":["A","A","B","C","D"],
        "Liga Score":[945,902,875,852,810]
    })

    st.dataframe(df,use_container_width=True,hide_index=True)

    fig = px.bar(df.sort_values("Liga Score"),
                 x="Liga Score",
                 y="Nama",
                 orientation="h",
                 text="Liga Score")
    fig.update_traces(marker_color="#00529C")
    st.plotly_chart(fig,use_container_width=True)

elif st.session_state.page == "Kontribusi Unit":

    st.header("📈 Kontribusi Unit")

    df = pd.DataFrame({
        "Mantri":["Andi","Budi","Citra","Dedi","Eko"],
        "Kontribusi (%)":[32,24,18,15,11]
    })

    st.dataframe(df,use_container_width=True,hide_index=True)

    fig = px.pie(df,names="Mantri",values="Kontribusi (%)",hole=.55)
    fig.update_traces(marker=dict(colors=["#00529C","#1E88E5","#64B5F6","#90CAF9","#F37021"]))
    st.plotly_chart(fig,use_container_width=True)


elif st.session_state.page == "Top Performer":

    st.header("🔥 Top Performer")

    top = pd.DataFrame({
        "Peringkat":[1,2,3,4,5],
        "Nama":["Andi","Budi","Citra","Dedi","Eko"],
        "Liga Score":[945,902,875,852,810]
    })

    st.dataframe(top,use_container_width=True,hide_index=True)

    st.success("🥇 Andi menjadi Top Performer bulan ini.")

st.markdown("---")
st.markdown(
    "<div style='background:#00529C;color:white;padding:10px;border-radius:10px;text-align:center'>"
    "<b>Liga Mantri Dashboard</b><br>Performance Monitoring & Leaderboard"
    "</div>",
    unsafe_allow_html=True
)
