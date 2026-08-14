import streamlit as st
import pandas as pd
import plotly.express as px
from supabase import create_client, Client
from io import BytesIO

st.title("🍚 Pengeluaran Perkapita untuk Makanan")

# =============================
# KONEKSI SUPABASE
# =============================

url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]

supabase: Client = create_client(url, key)

# =============================
# AMBIL DATA
# =============================

response = (
    supabase
    .table("pengeluaran_makanan")
    .select("*")
    .execute()
)

data = response.data

if not data:
    st.warning("Data Pengeluaran Perkapita untuk Makanan belum tersedia.")
    st.stop()

df = pd.DataFrame(data)

# =============================
# PILIH KABUPATEN/KOTA
# =============================

daftar_wilayah = sorted(
    df["kabupaten_kota"]
    .dropna()
    .unique()
)

wilayah = st.selectbox(
    "📍 Pilih Kabupaten/Kota",
    daftar_wilayah
)

# Filter wilayah
df_wilayah = df[
    df["kabupaten_kota"] == wilayah
].copy()

df_wilayah = df_wilayah.sort_values("tahun")

# =============================
# JUDUL
# =============================

st.subheader(
    f"🍚 Pengeluaran Perkapita untuk Makanan - {wilayah}"
)

st.write(
    f"Data tahun "
    f"{df_wilayah['tahun'].min()}–"
    f"{df_wilayah['tahun'].max()}."
)

# =============================
# TABEL
# =============================

df_tabel = df_wilayah[
    [
        "tahun",
        "miskin",
        "tidak_miskin",
        "miskin_dan_tidak_miskin"
    ]
].copy()

df_tabel = df_tabel.rename(
    columns={
        "tahun": "Tahun",
        "miskin": "Miskin",
        "tidak_miskin": "Tidak Miskin",
        "miskin_dan_tidak_miskin":
            "Miskin dan Tidak Miskin"
    }
)

st.dataframe(
    df_tabel,
    use_container_width=True,
    hide_index=True
)

# =============================
# GRAFIK
# =============================

df_grafik = df_wilayah[
    [
        "tahun",
        "miskin",
        "tidak_miskin",
        "miskin_dan_tidak_miskin"
    ]
].copy()

df_grafik = df_grafik.rename(
    columns={
        "miskin": "Miskin",
        "tidak_miskin": "Tidak Miskin",
        "miskin_dan_tidak_miskin":
            "Miskin dan Tidak Miskin"
    }
)

df_long = df_grafik.melt(
    id_vars="tahun",
    var_name="Kategori",
    value_name="Persentase"
)

fig = px.line(
    df_long,
    x="tahun",
    y="Persentase",
    color="Kategori",
    markers=True,
    title=f"Pengeluaran Perkapita untuk Makanan - {wilayah}"
)

fig.update_layout(
    xaxis_title="Tahun",
    yaxis_title="Persentase (%)"
)

st.plotly_chart(
    fig,
    use_container_width=True
)

# =============================
# DOWNLOAD EXCEL
# =============================

output = BytesIO()

with pd.ExcelWriter(
    output,
    engine="openpyxl"
) as writer:

    df_tabel.to_excel(
        writer,
        index=False,
        sheet_name="Pengeluaran Makanan"
    )

output.seek(0)

st.download_button(
    label="📥 Download Excel Pengeluaran Makanan",
    data=output,
    file_name=f"Pengeluaran_Makanan_{wilayah}.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)