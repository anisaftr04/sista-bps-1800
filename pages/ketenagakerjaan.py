import streamlit as st
import pandas as pd
import plotly.express as px
from supabase import create_client, Client
from io import BytesIO

from utils import load_css, admin_edit_button, set_toast, admin_import_data

load_css()

is_admin = st.session_state.get("is_admin", False)

DAFTAR_KABKOTA = [
    "Bandar Lampung", "Metro", "Lampung Barat", "Lampung Selatan",
    "Lampung Tengah", "Lampung Timur", "Lampung Utara", "Mesuji",
    "Pesawaran", "Pesisir Barat", "Pringsewu", "Tanggamus",
    "Tulang Bawang", "Tulang Bawang Barat", "Way Kanan"
]

col_judul, col_edit = st.columns([8, 1])
with col_judul:
    st.title("💼 Ketenagakerjaan")
with col_edit:
    st.write("")
    admin_edit_button()

# ==========================================
# KONEKSI SUPABASE
# ==========================================

url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
service_key = st.secrets["SUPABASE_SERVICE_ROLE_KEY"]
supabase: Client = create_client(url, key)
supabase_admin: Client = create_client(url, service_key)

# ==========================================
# DAFTAR DATA
# ==========================================

daftar_data = {
    "Angkatan Kerja": "angkatan_kerja",
    "TPAK": "tpak",
    "TPT": "tpt",
    "Penduduk Bekerja": "penduduk_bekerja",
    "Lapangan Usaha": "lapangan_usaha",
    "Status Pekerjaan": "status_pekerjaan",
    "Pendidikan Pekerja": "pendidikan_pekerja",
    "Jam Kerja": "jam_kerja",
    "Upah/Gaji": "upah",
    "Setengah Penganggur": "setengah_penganggur",
    "Pekerja Informal": "pekerja_informal"
}

indikator = st.selectbox("📊 Pilih Data Ketenagakerjaan", list(daftar_data.keys()))
nama_tabel = daftar_data[indikator]

# ==========================================
# AMBIL DATA
# ==========================================

try:
    response = supabase.table(nama_tabel).select("*").execute()
    data = response.data
except Exception as e:
    st.error(f"Gagal mengambil data dari Supabase: {e}")
    st.stop()

if not data:
    st.warning(f"Data {indikator} belum tersedia.")
    st.stop()

df = pd.DataFrame(data)

df["tahun"] = pd.to_numeric(df["tahun"], errors="coerce")
df["nilai"] = pd.to_numeric(df["nilai"], errors="coerce")
df = df.dropna(subset=["tahun", "nilai"])
df["tahun"] = df["tahun"].astype(int)

ada_kategori = "kategori" in df.columns

# ==========================================
# PILIH KABUPATEN/KOTA
# ==========================================

daftar_wilayah = sorted(df["kabupaten_kota"].dropna().unique())
wilayah = st.selectbox("📍 Pilih Kabupaten/Kota", daftar_wilayah)

df_wilayah = df[df["kabupaten_kota"] == wilayah].copy()

# ==========================================
# PILIH KATEGORI (khusus sheet 5 dan 6)
# ==========================================

if ada_kategori:
    daftar_kategori = sorted(df_wilayah["kategori"].dropna().unique())
    kategori = st.selectbox("🏷️ Pilih Kategori", daftar_kategori)
    df_wilayah = df_wilayah[df_wilayah["kategori"] == kategori].copy()

df_wilayah = df_wilayah.sort_values("tahun")

# ==========================================
# JUDUL
# ==========================================

st.subheader(f"💼 {indikator} - {wilayah}")
if ada_kategori:
    st.write(f"Kategori: **{kategori}**")
st.write(f"Data tahun {df_wilayah['tahun'].min()}–{df_wilayah['tahun'].max()}.")

# ==========================================
# TABEL
# ==========================================

kolom_tabel = ["tahun", "nilai"]
if ada_kategori:
    kolom_tabel.insert(1, "kategori")

df_tabel = df_wilayah[kolom_tabel].copy()
df_tabel = df_tabel.rename(columns={"tahun": "Tahun", "kategori": "Kategori", "nilai": "Nilai"})

st.subheader("📋 Data")
st.dataframe(df_tabel, use_container_width=True, hide_index=True)

# ==========================================
# DOWNLOAD EXCEL
# ==========================================

output = BytesIO()
with pd.ExcelWriter(output, engine="openpyxl") as writer:
    df_tabel.to_excel(writer, index=False, sheet_name="Ketenagakerjaan")
output.seek(0)

st.download_button(
    label="📥 Download Excel",
    data=output,
    file_name=f"Ketenagakerjaan_{indikator}_{wilayah}.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)

# ==========================================
# GRAFIK
# ==========================================

fig = px.line(df_wilayah, x="tahun", y="nilai", markers=True, title=f"{indikator} - {wilayah}")
fig.update_layout(xaxis_title="Tahun", yaxis_title="Nilai", hovermode="x unified", xaxis=dict(showgrid=False), yaxis=dict(showgrid=False))
st.plotly_chart(fig, use_container_width=True)

# =========================================================
# INFORMASI
# =========================================================
st.caption("Sumber data: Badan Pusat Statistik (BPS).")

# ==========================================
# PANEL ADMIN
# ==========================================

if is_admin and st.session_state.get("show_admin_panel", False):

    st.markdown("---")
    st.subheader(f"⚙️ Panel Admin — {indikator}")
    st.caption(f"Mengelola tabel: `{nama_tabel}`")

    tab_tambah, tab_edit, tab_hapus = st.tabs(["➕ Tambah Data", "✏️ Edit Data", "🗑 Hapus Data"])

    with tab_tambah:

        metode = st.radio(
            "Metode Input",
            ["Input Manual", "Import Excel/CSV"],
            horizontal=True,
            key=f"metode_tambah_{nama_tabel}"
        )

        st.markdown("---")

        if metode == "Input Manual":

            with st.form(f"form_tambah_{nama_tabel}", clear_on_submit=True):
                col_a, col_b = st.columns(2)
                with col_a:
                    tahun_baru = st.number_input("Tahun", min_value=2000, max_value=2100, step=1)
                with col_b:
                    kabkota_baru = st.selectbox("Kabupaten/Kota", DAFTAR_KABKOTA, key="tambah_kabkota_naker")

                kategori_baru = None
                if ada_kategori:
                    kategori_baru = st.text_input("Kategori")

                nilai_baru = st.number_input("Nilai", value=0.0)

                if st.form_submit_button("💾 Simpan Data Baru"):
                    data_baru = {
                        "tahun": int(tahun_baru),
                        "kabupaten_kota": kabkota_baru,
                        "nilai": nilai_baru
                    }
                    if ada_kategori:
                        data_baru["kategori"] = kategori_baru

                    try:
                        supabase_admin.table(nama_tabel).insert(data_baru).execute()
                        set_toast("Data baru berhasil ditambahkan.")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Gagal menyimpan data: {e}")

        else:

            kolom_wajib = ["tahun", "kabupaten_kota", "nilai"]
            kolom_teks = ["kabupaten_kota"]
            if ada_kategori:
                kolom_wajib.append("kategori")
                kolom_teks.append("kategori")

            admin_import_data(
                supabase_admin=supabase_admin,
                table_name=nama_tabel,
                kolom_wajib=kolom_wajib,
                key_prefix=nama_tabel,
                kolom_teks=kolom_teks
            )

    with tab_edit:
        if ada_kategori:
            opsi_baris = [f"{row['tahun']} - {row['kabupaten_kota']} - {row['kategori']}" for _, row in df.iterrows()]
        else:
            opsi_baris = [f"{row['tahun']} - {row['kabupaten_kota']}" for _, row in df.iterrows()]

        pilih_baris = st.selectbox("Pilih data yang mau diedit", opsi_baris, key=f"pilih_edit_{nama_tabel}")

        if pilih_baris:
            bagian = pilih_baris.split(" - ")
            tahun_pilih = int(bagian[0])
            kabkota_pilih = bagian[1]

            if ada_kategori:
                kategori_pilih = bagian[2]
                baris = df[(df["tahun"] == tahun_pilih) & (df["kabupaten_kota"] == kabkota_pilih) & (df["kategori"] == kategori_pilih)].iloc[0]
            else:
                baris = df[(df["tahun"] == tahun_pilih) & (df["kabupaten_kota"] == kabkota_pilih)].iloc[0]

            with st.form(f"form_edit_{nama_tabel}"):
                st.write(f"Mengedit data: **{pilih_baris}**")
                nilai_edit = st.number_input("Nilai", value=float(baris["nilai"]))

                if st.form_submit_button("💾 Simpan Perubahan"):
                    query = supabase_admin.table(nama_tabel).update({"nilai": nilai_edit}).eq("tahun", tahun_pilih).eq("kabupaten_kota", kabkota_pilih)
                    if ada_kategori:
                        query = query.eq("kategori", kategori_pilih)

                    try:
                        query.execute()
                        set_toast("Data berhasil diperbarui.")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Gagal memperbarui data: {e}")

    with tab_hapus:
        if ada_kategori:
            opsi_hapus = [f"{row['tahun']} - {row['kabupaten_kota']} - {row['kategori']}" for _, row in df.iterrows()]
        else:
            opsi_hapus = [f"{row['tahun']} - {row['kabupaten_kota']}" for _, row in df.iterrows()]

        pilih_hapus = st.selectbox("Pilih data yang mau dihapus", opsi_hapus, key=f"pilih_hapus_{nama_tabel}")

        if st.button("🗑 Hapus Data Ini", key=f"tombol_hapus_{nama_tabel}"):
            st.session_state[f"konfirmasi_hapus_{nama_tabel}"] = pilih_hapus

        konfirmasi_key = f"konfirmasi_hapus_{nama_tabel}"
        if st.session_state.get(konfirmasi_key):
            target = st.session_state[konfirmasi_key]
            st.warning(f"Yakin ingin menghapus data **{target}**? Tindakan ini tidak bisa dibatalkan.")

            col_ya, col_batal = st.columns(2)
            with col_ya:
                if st.button("✅ Ya, Hapus Permanen", key=f"ya_hapus_{nama_tabel}"):
                    bagian = target.split(" - ")
                    tahun_hapus = int(bagian[0])
                    kabkota_hapus = bagian[1]

                    query = supabase_admin.table(nama_tabel).delete().eq("tahun", tahun_hapus).eq("kabupaten_kota", kabkota_hapus)
                    if ada_kategori:
                        query = query.eq("kategori", bagian[2])

                    try:
                        query.execute()
                        del st.session_state[konfirmasi_key]
                        set_toast("Data berhasil dihapus.")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Gagal menghapus data: {e}")

            with col_batal:
                if st.button("❌ Batal", key=f"batal_hapus_{nama_tabel}"):
                    del st.session_state[konfirmasi_key]
                    st.rerun()