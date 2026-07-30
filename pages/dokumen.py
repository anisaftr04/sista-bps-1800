import streamlit as st
import pandas as pd
from supabase import create_client, Client

# ==========================
# Koneksi Supabase
# ==========================
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]

supabase: Client = create_client(url, key)

st.title("📂 Manajemen Dokumen")
st.write("Kelola seluruh dokumen yang telah diunggah ke sistem.")

cari = st.text_input("🔍 Cari nama dokumen")

# ==========================
# Ambil data dari tabel dokumen
# ==========================
response = supabase.table("dokumen").select("*").order("created_at", desc=True).execute()

data = response.data

if len(data) == 0:
    st.info("Belum ada dokumen.")

else:
    df = pd.DataFrame(data)

    # Mengubah nama kolom
    df = df.rename(columns={
        "nama_dokumen": "Nama Dokumen",
        "nama_file": "Nama File",
        "kabupaten": "Kabupaten",
        "kategori": "Kategori",
        "keterangan": "Keterangan",
        "created_at": "Tanggal Upload"
    })

    # Menghapus kolom yang tidak diperlukan
    df = df.drop(columns=["id", "path_file"], errors="ignore")

    # Filter pencarian
    if cari:
        df = df[
            df["Nama Dokumen"].fillna("").str.contains(cari, case=False)
        ]

    # Tampilkan tabel
    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True
    )