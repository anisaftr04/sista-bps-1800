import streamlit as st
import pandas as pd
import plotly.express as px
from supabase import create_client, Client
from io import BytesIO

st.title("📉 Kemiskinan")

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
    .table("kemiskinan")
    .select("*")
    .execute()
)

data = response.data

if not data:
    st.warning("Data Kemiskinan belum tersedia.")
    st.stop()

df = pd.DataFrame(data)

# =============================
# KONVERSI DATA
# =============================

df["tahun"] = pd.to_numeric(
    df["tahun"],
    errors="coerce"
)

df = df.sort_values("tahun")

# =============================
# PILIH INDIKATOR
# =============================

daftar_indikator = {
    "P0 - Persentase Penduduk Miskin": {
        "kota": "p0_kota",
        "desa": "p0_desa",
        "kota_desa": "p0_kota_desa"
    },

    "Garis Kemiskinan": {
        "kota": "garis_kemiskinan_kota",
        "desa": "garis_kemiskinan_desa",
        "kota_desa": "garis_kemiskinan_kota_desa"
    },

    "Jumlah Penduduk Miskin": {
        "kota": "jumlah_miskin_kota",
        "desa": "jumlah_miskin_desa",
        "kota_desa": "jumlah_miskin_kota_desa"
    },

    "P1 - Indeks Kedalaman Kemiskinan": {
        "kota": "p1_kota",
        "desa": "p1_desa",
        "kota_desa": "p1_kota_desa"
    },

    "P2 - Indeks Keparahan Kemiskinan": {
        "kota": "p2_kota",
        "desa": "p2_desa",
        "kota_desa": "p2_kota_desa"
    },

    "Gini Ratio": {
        "kota": "gini_kota",
        "desa": "gini_desa",
        "kota_desa": "gini_kota_desa"
    }
}

indikator = st.selectbox(
    "📊 Pilih Indikator",
    list(daftar_indikator.keys())
)

# =============================
# PILIH WILAYAH
# =============================

wilayah_pilihan = {
    "Kota": "kota",
    "Desa": "desa",
    "Kota + Desa": "kota_desa"
}

wilayah = st.selectbox(
    "📍 Pilih Wilayah",
    list(wilayah_pilihan.keys())
)

kolom_data = daftar_indikator[indikator][
    wilayah_pilihan[wilayah]
]

# =============================
# DATA TERPILIH
# =============================

df_tampil = df[
    [
        "tahun",
        "periode",
        kolom_data
    ]
].copy()

df_tampil = df_tampil.rename(
    columns={
        "tahun": "Tahun",
        "periode": "Periode",
        kolom_data: "Nilai"
    }
)

df_tampil = df_tampil.sort_values(
    "Tahun"
)

# =============================
# JUDUL
# =============================

st.subheader(
    f"📉 {indikator} - {wilayah}"
)

st.write(
    f"Data tahun "
    f"{df_tampil['Tahun'].min()}–"
    f"{df_tampil['Tahun'].max()}."
)

# =============================
# TABEL
# =============================

st.dataframe(
    df_tampil,
    use_container_width=True,
    hide_index=True
)

# =============================
# GRAFIK
# =============================

fig = px.line(
    df_tampil,
    x="Tahun",
    y="Nilai",
    markers=True,
    title=f"{indikator} - {wilayah}"
)

fig.update_layout(
    xaxis_title="Tahun",
    yaxis_title="Nilai",
    hovermode="x unified"
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

    df_tampil.to_excel(
        writer,
        index=False,
        sheet_name="Kemiskinan"
    )

output.seek(0)

st.download_button(
    label="📥 Download Excel Kemiskinan",
    data=output,
    file_name=f"Kemiskinan_{indikator}_{wilayah}.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)