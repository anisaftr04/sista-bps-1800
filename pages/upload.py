
from supabase import create_client, Client
import os
import streamlit as st

url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]

supabase: Client = create_client(url, key)

st.set_page_config(
    page_title="Upload Dokumen",
    page_icon="📤",
    layout="wide"
)

st.title("📤 Upload Dokumen")
st.write("Silakan unggah dokumen Bidang Statistik Sosial.")

uploaded_file = st.file_uploader(
    "Pilih file",
    type=["pdf", "xlsx", "xls", "docx", "pptx"]
)
nama_dokumen = st.text_input(
    "📝 Nama Dokumen"
)

kabupaten = st.selectbox(
    "📍 Kabupaten/Kota",
    [
        "Bandar Lampung",
        "Metro",
        "Lampung Selatan",
        "Lampung Timur",
        "Lampung Tengah",
        "Lampung Barat",
        "Lampung Utara",
        "Way Kanan",
        "Pesawaran",
        "Pringsewu",
        "Mesuji",
        "Tulang Bawang",
        "Tulang Bawang Barat",
        "Pesisir Barat",
        "Tanggamus"
    ]
)

kategori = st.selectbox(
    "📂 Kategori",
    [
        "Surat",
        "Laporan",
        "Rekap",
        "Presentasi",
        "Lainnya"
    ]
)

keterangan = st.text_area(
    "📝 Keterangan"
)

if uploaded_file is not None:
    st.success("✅ File berhasil dipilih")

    st.write("**Nama File:**", uploaded_file.name)
    st.write("**Ukuran:**", round(uploaded_file.size/1024,2), "KB")

if st.button("💾 Simpan Dokumen"):

    if uploaded_file is None:
        st.warning("Silakan pilih file terlebih dahulu.")
    else:
        try:
            file_path = f"{kabupaten}/{uploaded_file.name}"
            st.write("Mulai upload...")
            supabase.storage.from_("dokumen").upload(
            file_path,
            uploaded_file.getvalue(),
            {"content-type": uploaded_file.type}
        )
            st.write("Upload selesai")
            supabase.table("dokumen").insert({
    "nama_dokumen": nama_dokumen,
    "nama_file": uploaded_file.name,
    "kabupaten": kabupaten,
    "kategori": kategori,
    "keterangan": keterangan,
    "path_file": file_path
}).execute()
            st.success("✅ Dokumen berhasil diupload ke Supabase!")

        except Exception as e:
            st.exception(e)