import streamlit as st
import pandas as pd
import plotly.express as px
from supabase import create_client, Client
from io import BytesIO

from utils import load_css, admin_edit_button, set_toast, admin_import_data

load_css()

# ==========================================
# CUSTOM CSS AGAR TAMPILAN LEBIH RAPI
# ==========================================
st.markdown(
    """
    <style>
    div[data-baseweb="popover"] {
        margin-top: 8px !important;
    }
    .breadcrumb-container {
        font-size: 15px;
        color: #60758c;
        margin-bottom: 15px;
        margin-top: -10px;
    }
    .breadcrumb-container a {
        color: #0067b9;
        text-decoration: none;
        font-weight: 600;
    }
    .breadcrumb-container a:hover {
        text-decoration: underline;
    }
    </style>
    <div class="breadcrumb-container">
        <a href="/" target="_self">Beranda</a> &gt; Statistik Sosial - Ketenagakerjaan
    </div>
    """,
    unsafe_allow_html=True
)

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

# ==========================================
# FILTER DATA (DI LUAR FORM AGAR RESPONSIF)
# ==========================================
st.subheader("⚙️ Filter Data")

col_f1, col_f2, col_f3 = st.columns(3)

with col_f1:
    st.markdown("📊 **Pilih Indikator**")
    indikator_input = st.selectbox("📊 Pilih Data Ketenagakerjaan", list(daftar_data.keys()), label_visibility="collapsed")

# Ambil data tahun spesifik langsung dari tabel indikator yang dipilih secara akurat
tabel_input = daftar_data.get(indikator_input, "angkatan_kerja")
try:
    resp_opt = supabase.table(tabel_input).select("tahun").execute()
    df_opt = pd.DataFrame(resp_opt.data)
    if not df_opt.empty and "tahun" in df_opt.columns:
        df_opt["tahun"] = pd.to_numeric(df_opt["tahun"], errors="coerce")
        daftar_tahun_opt = sorted(df_opt["tahun"].dropna().unique().astype(int), reverse=True)
    else:
        daftar_tahun_opt = []
except:
    daftar_tahun_opt = []

# Ambil daftar Kabupaten/Kota langsung dari data tabel yang sama,
# supaya namanya pasti sama persis dengan yang tersimpan di Supabase
try:
    resp_wil_opt = supabase.table(tabel_input).select("kabupaten_kota").execute()
    df_wil_opt = pd.DataFrame(resp_wil_opt.data)
    if not df_wil_opt.empty and "kabupaten_kota" in df_wil_opt.columns:
        daftar_wilayah_opt = sorted(df_wil_opt["kabupaten_kota"].dropna().unique())
    else:
        daftar_wilayah_opt = []
except:
    daftar_wilayah_opt = []

with col_f2:
    st.markdown("📅 **Tahun**")
    semua_tahun_chk = st.checkbox("Pilih Semua", value=True, key=f"chk_semua_tahun_{indikator_input}")

    # Deteksi perubahan status "Pilih Semua", langsung sinkronkan
    # (aman karena checkbox ini di luar st.form, jadi tiap klik langsung rerun)
    prev_key_tahun = f"_prev_chk_semua_tahun_{indikator_input}"
    if prev_key_tahun not in st.session_state:
        st.session_state[prev_key_tahun] = semua_tahun_chk
    elif st.session_state[prev_key_tahun] != semua_tahun_chk:
        for thn in daftar_tahun_opt:
            st.session_state[f"thn_{thn}_{indikator_input}"] = semua_tahun_chk
        st.session_state[prev_key_tahun] = semua_tahun_chk

    with st.container(height=160):
        tahun_terpilih_input = []
        if daftar_tahun_opt:
            for thn in daftar_tahun_opt:
                cek = st.checkbox(str(thn), value=semua_tahun_chk, key=f"thn_{thn}_{indikator_input}")
                if cek:
                    tahun_terpilih_input.append(int(thn))
        else:
            st.warning("Tidak ada data tahun.")

with col_f3:
    st.markdown("📍 **Kabupaten/Kota**")
    semua_wilayah_chk = st.checkbox("Pilih Semua", value=True, key=f"chk_semua_wilayah_{indikator_input}")

    prev_key_wilayah = f"_prev_chk_semua_wilayah_{indikator_input}"
    if prev_key_wilayah not in st.session_state:
        st.session_state[prev_key_wilayah] = semua_wilayah_chk
    elif st.session_state[prev_key_wilayah] != semua_wilayah_chk:
        for wil in daftar_wilayah_opt:
            st.session_state[f"wil_{wil}_{indikator_input}"] = semua_wilayah_chk
        st.session_state[prev_key_wilayah] = semua_wilayah_chk

    with st.container(height=160):
        wilayah_terpilih_input = []
        if daftar_wilayah_opt:
            for wil in daftar_wilayah_opt:
                cek_wil = st.checkbox(wil, value=semua_wilayah_chk, key=f"wil_{wil}_{indikator_input}")
                if cek_wil:
                    wilayah_terpilih_input.append(wil)
        else:
            st.warning("Tidak ada data wilayah.")

st.markdown("")
submitted = st.button("🔍 Tampilkan Data", use_container_width=True)

# Simpan state saat tombol ditekan
if submitted:
    st.session_state["submitted_naker"] = True
    st.session_state["indikator_final"] = indikator_input
    st.session_state["tahun_final"] = tahun_terpilih_input
    st.session_state["wilayah_final"] = wilayah_terpilih_input

# Jika belum pernah submit sama sekali
if not st.session_state.get("submitted_naker", False):
    st.info("👆 Silakan sesuaikan pilihan indikator, tahun, dan wilayah di atas, lalu klik tombol **Tampilkan Data**.")
    st.stop()

# Ambil variabel dari session state
indikator = st.session_state.get("indikator_final", list(daftar_data.keys())[0])
nama_tabel = daftar_data[indikator]
tahun_terpilih = st.session_state.get("tahun_final", [])
wilayah_terpilih = st.session_state.get("wilayah_final", [])

if not tahun_terpilih or not wilayah_terpilih:
    st.warning("⚠️ Tahun atau Kabupaten/Kota belum ada yang dicentang. Silakan centang minimal satu lalu klik Tampilkan Data.")
    st.stop()

# Ambil data utama dari Supabase sesuai indikator terpilih
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

df_filtered = df[df["kabupaten_kota"].isin(wilayah_terpilih) & df["tahun"].isin(tahun_terpilih)].copy()

# ==========================================
# PILIH KATEGORI (Jika ada)
# ==========================================
kategori_terpilih = None
if ada_kategori:
    daftar_kategori = sorted(df_filtered["kategori"].dropna().unique())
    kategori_terpilih = st.selectbox("🏷️ Pilih Kategori", daftar_kategori)
    df_filtered = df_filtered[df_filtered["kategori"] == kategori_terpilih].copy()

# ==========================================
# JUDUL & RINGKASAN
# ==========================================
judul_teks = f"{indikator}"
if ada_kategori and kategori_terpilih:
    judul_teks += f" - {kategori_terpilih}"

st.markdown("---")
st.subheader(f":material/work: {judul_teks}")
st.write(f"Menampilkan data untuk {len(wilayah_terpilih)} wilayah dan {len(tahun_terpilih)} tahun.")

# ==========================================
# TABEL PIVOT (Baris = Wilayah, Kolom = Tahun)
# ==========================================
if not df_filtered.empty:
    df_pivot = df_filtered.pivot_table(
        index="kabupaten_kota", 
        columns="tahun", 
        values="nilai", 
        aggfunc="sum"
    ).reset_index()

    kolom_tahun_urut = sorted([col for col in df_pivot.columns if isinstance(col, int)])
    df_pivot = df_pivot[["kabupaten_kota"] + kolom_tahun_urut]
    df_pivot = df_pivot.rename(columns={"kabupaten_kota": "Kabupaten/Kota"})

    df_tampilkan = df_pivot.copy()
    for col in kolom_tahun_urut:
        df_tampilkan[col] = df_tampilkan[col].apply(
            lambda x: f"{x:,.0f}".replace(",", ".") if pd.notnull(x) else "-"
        )

    st.subheader(":material/list_alt: Data")
    st.dataframe(df_tampilkan, use_container_width=True, hide_index=True)

    # ==========================================
    # DOWNLOAD EXCEL
    # ==========================================
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df_tampilkan.to_excel(writer, index=False, sheet_name="Ketenagakerjaan")
    output.seek(0)

    st.download_button(
        label="📥 Download Excel",
        data=output,
        file_name=f"Ketenagakerjaan_{indikator}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    # ==========================================
    # GRAFIK
    # ==========================================
    fig = px.line(
        df_filtered, 
        x="tahun", 
        y="nilai", 
        color="kabupaten_kota", 
        markers=True, 
        title=f"{judul_teks} Berdasarkan Wilayah"
    )
    fig.update_layout(
        xaxis_title="Tahun", 
        yaxis_title="Nilai", 
        hovermode="x unified", 
        xaxis=dict(showgrid=False), 
        yaxis=dict(showgrid=False)
    )
    st.plotly_chart(fig, use_container_width=True)
else:
    st.warning("Tidak ada data yang sesuai dengan filter yang dipilih.")

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
        metode = st.radio("Metode Input", ["Input Manual", "Import Excel/CSV"], horizontal=True, key=f"metode_tambah_{nama_tabel}")
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