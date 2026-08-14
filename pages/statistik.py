import streamlit as st
import pandas as pd
import plotly.express as px
from supabase import create_client, Client
from io import BytesIO

st.title("📊 Statistik Pendidikan")

# =============================
# KONEKSI SUPABASE
# =============================

url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]

supabase: Client = create_client(url, key)

# =============================
# AMBIL DATA PENDIDIKAN
# =============================

response = (
    supabase
    .table("pendidikan_kemiskinan")
    .select("*")
    .execute()
)

data = response.data

if not data:
    st.warning("Data pendidikan belum tersedia.")
    st.stop()

df = pd.DataFrame(data)

# =============================
# PILIH KABUPATEN/KOTA
# =============================

daftar_wilayah = sorted(df["kabupaten_kota"].dropna().unique())

wilayah = st.selectbox(
    "📍 Pilih Kabupaten/Kota",
    daftar_wilayah
)

df_wilayah = df[df["kabupaten_kota"] == wilayah].copy()

# Agar tahun tampil tanpa koma
df_wilayah["tahun"] = df_wilayah["tahun"].astype(int).astype(str)

# Urutkan berdasarkan tahun
df_wilayah = df_wilayah.sort_values("tahun")



# =============================
# INFORMASI WILAYAH
# =============================

st.subheader(f"🎓 Pendidikan Penduduk - {wilayah}")

st.write(
    f"Menampilkan data pendidikan penduduk {wilayah} "
    f"periode {df_wilayah['tahun'].min()}–{df_wilayah['tahun'].max()}."
)

# =============================
# TABEL DATA
# =============================

st.dataframe(
    df_wilayah[
        ["tahun", "sd", "tamat_sd_smp", "sma"]
    ],
    use_container_width=True,
    hide_index=True
)

# =============================
# DOWNLOAD EXCEL
# =============================

df_download = df_wilayah[
    ["tahun", "sd", "tamat_sd_smp", "sma"]
].copy()

# Ubah nama kolom agar lebih mudah dibaca di Excel
df_download = df_download.rename(
    columns={
        "tahun": "Tahun",
        "sd": "< SD",
        "tamat_sd_smp": "Tamat SD/SMP",
        "sma": ">= SMA"
    }
)

# Membuat file Excel di memory
output = BytesIO()

with pd.ExcelWriter(output, engine="openpyxl") as writer:
    df_download.to_excel(
        writer,
        index=False,
        sheet_name="Data Pendidikan"
    )

output.seek(0)

st.download_button(
    label="📥 Download Excel",
    data=output,
    file_name=f"pendidikan_{wilayah}.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)
# =============================
# DOWNLOAD DATA
# =============================

csv_download = df_wilayah[
    ["tahun", "sd", "tamat_sd_smp", "sma"]
].to_csv(index=False)

st.download_button(
    label="📥 Download Data",
    data=csv_download,
    file_name=f"pendidikan_{wilayah}.csv",
    mime="text/csv"
)
# =============================
# GRAFIK
# =============================

df_grafik = df_wilayah[
    ["tahun", "sd", "tamat_sd_smp", "sma"]
].copy()

df_grafik = df_grafik.rename(
    columns={
        "sd": "< SD",
        "tamat_sd_smp": "Tamat SD/SMP",
        "sma": ">= SMA"
    }
)

df_long = df_grafik.melt(
    id_vars="tahun",
    var_name="Tingkat Pendidikan",
    value_name="Persentase"
)

fig = px.line(
    df_long,
    x="tahun",
    y="Persentase",
    color="Tingkat Pendidikan",
    markers=True,
    title=f"Persentase Pendidikan Penduduk - {wilayah}"
)

fig.update_layout(
    xaxis_title="Tahun",
    yaxis_title="Persentase (%)",
    legend_title="Tingkat Pendidikan"
)

st.plotly_chart(fig, use_container_width=True)