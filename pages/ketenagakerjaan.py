import streamlit as st
import pandas as pd
import plotly.express as px
from supabase import create_client, Client
from io import BytesIO

st.title("💼 Ketenagakerjaan")

# ==========================================
# KONEKSI SUPABASE
# ==========================================

url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]

supabase: Client = create_client(url, key)


# ==========================================
# DAFTAR DATA
# ==========================================

daftar_data = {
    "Angkatan Kerja": "naker_1",
    "TPAK": "naker_11",
    "TPT": "naker_12",
    "Penduduk Bekerja": "naker_2",
    "Lapangan Usaha": "naker_21",
    "Status Pekerjaan": "naker_22",
    "Pendidikan Pekerja": "naker_23",
    "Jam Kerja": "naker_3",
    "Upah/Gaji": "naker_4",
    "Setengah Penganggur": "naker_5",
    "Pekerja Informal": "naker_6"
}


# ==========================================
# PILIH INDIKATOR
# ==========================================

indikator = st.selectbox(
    "📊 Pilih Data Ketenagakerjaan",
    list(daftar_data.keys())
)

nama_tabel = daftar_data[indikator]


# ==========================================
# AMBIL DATA
# ==========================================

try:

    response = (
        supabase
        .table(nama_tabel)
        .select("*")
        .execute()
    )

    data = response.data

except Exception as e:

    st.error(
        f"Gagal mengambil data dari Supabase: {e}"
    )

    st.stop()


if not data:

    st.warning(
        f"Data {indikator} belum tersedia."
    )

    st.stop()


df = pd.DataFrame(data)


# ==========================================
# KONVERSI TIPE DATA
# ==========================================

df["tahun"] = pd.to_numeric(
    df["tahun"],
    errors="coerce"
)

df["nilai"] = pd.to_numeric(
    df["nilai"],
    errors="coerce"
)

df = df.dropna(
    subset=["tahun", "nilai"]
)

df["tahun"] = df["tahun"].astype(int)


# ==========================================
# PILIH KABUPATEN/KOTA
# ==========================================

daftar_wilayah = sorted(
    df["kabupaten_kota"]
    .dropna()
    .unique()
)

wilayah = st.selectbox(
    "📍 Pilih Kabupaten/Kota",
    daftar_wilayah
)


# ==========================================
# FILTER WILAYAH
# ==========================================

df_wilayah = df[
    df["kabupaten_kota"] == wilayah
].copy()


# ==========================================
# PILIH KATEGORI
# KHUSUS SHEET 5 DAN 6
# ==========================================

if "kategori" in df_wilayah.columns:

    daftar_kategori = sorted(
        df_wilayah["kategori"]
        .dropna()
        .unique()
    )

    kategori = st.selectbox(
        "🏷️ Pilih Kategori",
        daftar_kategori
    )

    df_wilayah = df_wilayah[
        df_wilayah["kategori"] == kategori
    ].copy()


# ==========================================
# URUTKAN TAHUN
# ==========================================

df_wilayah = df_wilayah.sort_values(
    "tahun"
)


# ==========================================
# JUDUL
# ==========================================

st.subheader(
    f"💼 {indikator} - {wilayah}"
)

if "kategori" in df_wilayah.columns:

    st.write(
        f"Kategori: **{kategori}**"
    )

st.write(
    f"Data tahun "
    f"{df_wilayah['tahun'].min()}–"
    f"{df_wilayah['tahun'].max()}."
)


# ==========================================
# GRAFIK
# ==========================================

fig = px.line(
    df_wilayah,
    x="tahun",
    y="nilai",
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


# ==========================================
# TABEL
# ==========================================

kolom_tabel = [
    "tahun",
    "nilai"
]

if "kategori" in df_wilayah.columns:
    kolom_tabel.insert(
        1,
        "kategori"
    )

df_tabel = df_wilayah[
    kolom_tabel
].copy()


df_tabel = df_tabel.rename(
    columns={
        "tahun": "Tahun",
        "kategori": "Kategori",
        "nilai": "Nilai"
    }
)

st.subheader("📋 Data")

st.dataframe(
    df_tabel,
    use_container_width=True,
    hide_index=True
)


# ==========================================
# DOWNLOAD EXCEL
# ==========================================

output = BytesIO()

with pd.ExcelWriter(
    output,
    engine="openpyxl"
) as writer:

    df_tabel.to_excel(
        writer,
        index=False,
        sheet_name="Ketenagakerjaan"
    )

output.seek(0)

st.download_button(
    label="📥 Download Excel",
    data=output,
    file_name=(
        f"Ketenagakerjaan_"
        f"{indikator}_"
        f"{wilayah}.xlsx"
    ),
    mime=(
        "application/vnd.openxmlformats-"
        "officedocument.spreadsheetml.sheet"
    )
)