import streamlit as st
from supabase import create_client, Client

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

st.title("📂 Manajemen Dokumen")

cari = st.text_input("🔍 Cari Dokumen")

response = (
    supabase.table("dokumen")
    .select("*")
    .order("created_at", desc=True)
    .execute()
)

data = response.data

if not data:
    st.info("Belum ada dokumen.")

else:

    if cari:
        data = [
            d for d in data
            if cari.lower() in (d["nama_dokumen"] or "").lower()
        ]

    for dok in data:

        with st.container(border=True):

            st.subheader(f"📄 {dok['nama_dokumen']}")

            st.write(f"**Kabupaten :** {dok['kabupaten']}")
            st.write(f"**Kategori :** {dok['kategori']}")
            st.write(f"**Keterangan :** {dok['keterangan']}")

            col1, col2 = st.columns(2)

            with col1:

                url = supabase.storage.from_("dokumen").get_public_url(
                    dok["path_file"]
                )

                st.link_button(
                    "📥 Download",
                    url
                )

            with col2:

                if st.button(
                    "🗑️ Hapus",
                    key=dok["id"]
                ):

                    supabase.storage.from_("dokumen").remove(
                        [dok["path_file"]]
                    )

                    supabase.table("dokumen").delete().eq(
                        "id",
                        dok["id"]
                    ).execute()

                    st.success("Dokumen berhasil dihapus.")
                    st.rerun()
