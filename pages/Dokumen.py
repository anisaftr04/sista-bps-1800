
import streamlit as st
import os
import uuid
from supabase import create_client, Client


# =====================================================
# 1. KONFIGURASI HALAMAN
# =====================================================

st.set_page_config(
    page_title="Manajemen Dokumen",
    page_icon="📂",
    layout="wide"
)


# =====================================================
# 2. KONEKSI SUPABASE
# =====================================================

url = st.secrets["SUPABASE_URL"]
anon_key = st.secrets["SUPABASE_KEY"]

# Koneksi umum untuk membaca dokumen
supabase: Client = create_client(
    url,
    anon_key
)

# Status login Admin dari aplikasi SISTA
is_admin = st.session_state.get("is_admin", False)

# Koneksi khusus Admin
supabase_admin = None

if is_admin:
    service_key = st.secrets.get(
        "SUPABASE_SERVICE_ROLE_KEY"
    )

    if service_key:
        supabase_admin = create_client(
            url,
            service_key
        )


# =====================================================
# 3. SESSION STATE UNTUK RESET FORM
# =====================================================

if "upload_form_version" not in st.session_state:
    st.session_state["upload_form_version"] = 0

form_version = st.session_state["upload_form_version"]


# Notifikasi setelah upload berhasil
if st.session_state.get("upload_success_message"):
    st.success(
        st.session_state.pop("upload_success_message")
    )


# =====================================================
# 4. JUDUL HALAMAN
# =====================================================

st.title("📂 Manajemen Dokumen")


# =====================================================
# 5. FORM UPLOAD DOKUMEN (KHUSUS ADMIN)
# =====================================================

if is_admin:

    st.subheader("📤 Upload Dokumen")

    if supabase_admin is None:

        st.error(
            "Koneksi Admin belum tersedia. "
            "Periksa SUPABASE_SERVICE_ROLE_KEY "
            "pada Secrets."
        )

    else:

        st.write(
            "Silakan unggah dokumen Bidang Statistik Sosial."
        )

        # Upload file
        uploaded_file = st.file_uploader(
            "Pilih file",
            type=[
                "pdf",
                "xlsx",
                "xls",
                "docx",
                "pptx",
                "csv",
                "txt"
            ],
            key=f"uploaded_file_{form_version}"
        )

        # Nama dokumen
        nama_dokumen = st.text_input(
            "📝 Nama Dokumen",
            key=f"nama_dokumen_{form_version}"
        )

        # Kabupaten/Kota
        kabupaten = st.selectbox(
            "📍 Kabupaten/Kota",
            [
                "Lampung Barat",
                "Tanggamus",
                "Lampung Selatan",
                "Lampung Timur",
                "Lampung Tengah",
                "Lampung Utara",
                "Way Kanan",
                "Tulang Bawang",
                "Pesawaran",
                "Pringsewu",
                "Mesuji",
                "Tulang Bawang Barat",
                "Pesisir Barat",
                "Bandar Lampung",
                "Metro",
                "Provinsi Lampung"
            ],
            key=f"kabupaten_{form_version}"
        )

        # Kategori dokumen
        kategori = st.selectbox(
            "📂 Kategori",
            [
                "Surat",
                "Laporan",
                "Rekap",
                "Presentasi",
                "Syntax",
                "Lainnya"
            ],
            key=f"kategori_{form_version}"
        )

        # Keterangan
        keterangan = st.text_area(
            "📝 Keterangan",
            key=f"keterangan_{form_version}"
        )

        # Informasi file
        if uploaded_file is not None:

            st.success("✅ File berhasil dipilih")

            st.write(
                "**Nama File:**",
                uploaded_file.name
            )

            st.write(
                "**Ukuran:**",
                round(uploaded_file.size / 1024, 2),
                "KB"
            )

        # Tombol simpan
        if st.button(
            "💾 Simpan Dokumen",
            use_container_width=True
        ):

            if uploaded_file is None:

                st.warning(
                    "Silakan pilih file terlebih dahulu."
                )

            elif not nama_dokumen.strip():

                st.warning(
                    "Nama Dokumen wajib diisi."
                )

            else:

                file_path = None

                try:

                    # Nama file asli
                    nama_file = os.path.basename(
                        uploaded_file.name
                    )

                    # Membuat nama penyimpanan unik
                    # agar file dengan nama sama tidak bentrok
                    nama_unik = (
                        f"{uuid.uuid4().hex}_{nama_file}"
                    )

                    file_path = (
                        f"{kabupaten}/{nama_unik}"
                    )

                    # ---------------------------------
                    # Upload ke Supabase Storage
                    # ---------------------------------

                    supabase_admin.storage.from_(
                        "dokumen"
                    ).upload(
                        file_path,
                        uploaded_file.getvalue(),
                        {
                            "content-type": (
                                uploaded_file.type
                                or "application/octet-stream"
                            )
                        }
                    )

                    # ---------------------------------
                    # Simpan informasi ke tabel
                    # ---------------------------------

                    supabase_admin.table(
                        "dokumen"
                    ).insert({

                        "nama_dokumen": (
                            nama_dokumen.strip()
                        ),

                        "nama_file": nama_file,

                        "kabupaten": kabupaten,

                        "kategori": kategori,

                        "keterangan": keterangan,

                        "path_file": file_path

                    }).execute()

                    # ---------------------------------
                    # Reset form
                    # ---------------------------------

                    st.session_state[
                        "upload_success_message"
                    ] = (
                        "✅ Dokumen berhasil diupload ke Supabase!"
                    )

                    st.session_state[
                        "upload_form_version"
                    ] = form_version + 1

                    st.rerun()

                except Exception as e:

                    # Jika penyimpanan database gagal,
                    # coba hapus file yang telanjur diupload
                    if file_path:

                        try:
                            supabase_admin.storage.from_(
                                "dokumen"
                            ).remove([file_path])

                        except Exception:
                            pass

                    st.error(
                        "Gagal menyimpan dokumen."
                    )

                    st.exception(e)

    st.divider()


else:

    st.info(
        "🔒 Login sebagai Admin untuk mengunggah atau menghapus dokumen."
    )


# =====================================================
# 6. MANAJEMEN DOKUMEN
# =====================================================

st.subheader("📂 Daftar Dokumen")


# =====================================================
# 7. FILTER DAN PENCARIAN
# =====================================================

with st.form("form_cari_dokumen"):

    kategori_filter = st.selectbox(
        "📂 Pilih Kategori Dokumen",
        [
            "Semua Kategori",
            "Surat",
            "Laporan",
            "Rekap",
            "Presentasi",
            "Syntax",
            "Lainnya"
        ]
    )

    cari = st.text_input(
        "🔍 Cari Dokumen",
        placeholder="Masukkan nama dokumen..."
    )

    tombol_cari = st.form_submit_button(
        "🔍 Cari Dokumen",
        use_container_width=True
    )


# =====================================================
# 8. AMBIL DATA DOKUMEN
# =====================================================

try:

    response = (
        supabase.table("dokumen")
        .select("*")
        .order("created_at", desc=True)
        .execute()
    )

    data = response.data or []

except Exception as e:

    st.error(
        "Gagal mengambil data dokumen dari Supabase."
    )

    st.exception(e)

    data = []


# =====================================================
# 9. FILTER DATA
# =====================================================

if tombol_cari:

    # Filter kategori
    if kategori_filter != "Semua Kategori":

        data = [
            d for d in data
            if d.get("kategori") == kategori_filter
        ]

    # Filter nama dokumen
    if cari.strip():

        kata_kunci = cari.strip().lower()

        data = [
            d for d in data
            if kata_kunci in (
                d.get("nama_dokumen") or ""
            ).lower()
        ]


# =====================================================
# 10. TAMPILKAN DAFTAR DOKUMEN
# =====================================================

if not data:

    st.info(
        "Belum ada dokumen atau dokumen tidak ditemukan."
    )

else:

    st.caption(
        f"Jumlah dokumen: {len(data)}"
    )

    for dok in data:

        with st.container(border=True):

            # Judul dokumen
            judul = (
                dok.get("nama_dokumen")
                or dok.get("nama_file")
                or "(Tanpa Nama)"
            )

            st.subheader(f"📄 {judul}")

            # Informasi dokumen
            col_info1, col_info2 = st.columns(2)

            with col_info1:

                st.write(
                    f"**Kabupaten/Kota :** "
                    f"{dok.get('kabupaten') or '-'}"
                )

                st.write(
                    f"**Kategori :** "
                    f"{dok.get('kategori') or '-'}"
                )

            with col_info2:

                st.write(
                    f"**Nama File :** "
                    f"{dok.get('nama_file') or '-'}"
                )

                st.write(
                    f"**Keterangan :** "
                    f"{dok.get('keterangan') or 'Tidak ada keterangan'}"
                )

            # Kolom tombol
            col1, col2 = st.columns(2)

            # -----------------------------------------
            # DOWNLOAD (SEMUA PENGGUNA)
            # -----------------------------------------

            with col1:

                try:

                    doc_url = (
                        supabase.storage
                        .from_("dokumen")
                        .get_public_url(
                            dok["path_file"]
                        )
                    )

                    st.link_button(
                        "📥 Download",
                        doc_url,
                        use_container_width=True
                    )

                except Exception as e:

                    st.error(
                        "Link download tidak dapat dibuat."
                    )

            # -----------------------------------------
            # HAPUS (KHUSUS ADMIN)
            # -----------------------------------------

            with col2:

                if is_admin:

                    if st.button(
                        "🗑️ Hapus",
                        key=f"hapus_{dok['id']}",
                        use_container_width=True
                    ):

                        if supabase_admin is None:

                            st.error(
                                "Koneksi Admin tidak tersedia."
                            )

                        else:

                            try:

                                # Hapus file dari Storage
                                supabase_admin.storage.from_(
                                    "dokumen"
                                ).remove([
                                    dok["path_file"]
                                ])

                                # Hapus data dari database
                                hasil = (
                                    supabase_admin.table(
                                        "dokumen"
                                    )
                                    .delete()
                                    .eq(
                                        "id",
                                        dok["id"]
                                    )
                                    .select("id")
                                    .execute()
                                )

                                # Periksa hasil penghapusan
                                if hasil.data:

                                    st.success(
                                        "✅ Dokumen berhasil dihapus!"
                                    )

                                    st.rerun()

                                else:

                                    st.error(
                                        "Data dokumen tidak ditemukan "
                                        "atau gagal dihapus."
                                    )

                            except Exception as e:

                                st.error(
                                    "Gagal menghapus dokumen."
                                )

                                st.exception(e)
