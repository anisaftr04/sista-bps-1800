import streamlit as st
import pandas as pd
import plotly.express as px
from supabase import create_client, Client
from io import BytesIO

from utils import load_css, admin_edit_button, set_toast, admin_import_data

load_css()

# ============================================================
# BREADCRUMB NAVIGASI
# ============================================================
st.markdown(
    """
    <style>
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
        <a href="/" target="_self">Beranda</a> &gt; Statistik Sosial - Kemiskinan
    </div>
    """,
    unsafe_allow_html=True
)

is_admin = st.session_state.get("is_admin", False)

# ============================================================
# JUDUL + TOMBOL EDIT
# ============================================================

col_judul, col_edit = st.columns([8, 1])

with col_judul:
    st.title("📉 Kemiskinan")

with col_edit:
    st.write("")
    admin_edit_button()

# ============================================================
# KONEKSI SUPABASE
# ============================================================

url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
service_key = st.secrets["SUPABASE_SERVICE_ROLE_KEY"]
supabase: Client = create_client(url, key)
supabase_admin: Client = create_client(url, service_key)

# ============================================================
# DAFTAR INDIKATOR (1 indikator = 1 tabel)
# ============================================================

daftar_indikator = {
    "P0 - Persentase Penduduk Miskin": "p0_persen_pend_miskin",
    "Garis Kemiskinan": "garis_kemiskinan",
    "Jumlah Penduduk Miskin": "jumlah_penduduk_miskin",
    "P1 - Indeks Kedalaman Kemiskinan": "p1_indeks_kedalaman",
    "P2 - Indeks Keparahan Kemiskinan": "p2_indeks_keparahan",
    "Gini Ratio": "gini_ratio",
}

# ============================================================
# FILTER: PILIH INDIKATOR DULU (menentukan tabel mana yang di-fetch)
# ============================================================

st.markdown("### 🎛️ Filter Data")
col_f1, col_f2, col_f3 = st.columns(3)

with col_f1:
    indikator = st.selectbox(
        "📊 Pilih Indikator",
        list(daftar_indikator.keys())
    )

nama_tabel = daftar_indikator[indikator]

# ============================================================
# AMBIL DATA (dari tabel indikator yang sedang dipilih)
# ============================================================

response = supabase.table(nama_tabel).select("*").execute()
data = response.data

if not data:
    st.warning(f"Data untuk indikator '{indikator}' belum tersedia.")
    st.stop()

df = pd.DataFrame(data)
df["tahun"] = pd.to_numeric(df["tahun"], errors="coerce")

if "kabupaten_kota" not in df.columns:
    st.error(f"Tabel '{nama_tabel}' tidak memiliki kolom 'kabupaten_kota'. Cek struktur tabel di Supabase.")
    st.stop()

# ============================================================
# FILTER: TAHUN & WILAYAH
# ============================================================

with col_f2:
    semua_tahun = sorted(df["tahun"].dropna().unique().tolist())
    pilih_semua_tahun = st.checkbox("Pilih Semua Tahun", value=True)

    if pilih_semua_tahun:
        tahun_terpilih = st.multiselect("📅 Pilih Tahun", semua_tahun, default=semua_tahun)
    else:
        tahun_terpilih = st.multiselect(
            "📅 Pilih Tahun", semua_tahun,
            default=semua_tahun[:3] if len(semua_tahun) >= 3 else semua_tahun
        )

with col_f3:
    semua_wilayah = sorted(df["kabupaten_kota"].dropna().unique().tolist())
    pilih_semua_wilayah = st.checkbox("Pilih Semua Kabupaten/Kota", value=True)

    if pilih_semua_wilayah:
        wilayah_terpilih = st.multiselect("📍 Pilih Kabupaten/Kota", semua_wilayah, default=semua_wilayah)
    else:
        wilayah_terpilih = st.multiselect(
            "📍 Pilih Kabupaten/Kota", semua_wilayah,
            default=semua_wilayah[:3] if len(semua_wilayah) >= 3 else semua_wilayah
        )

if not tahun_terpilih or not wilayah_terpilih:
    st.warning("⚠️ Silakan pilih minimal satu Tahun dan satu Kabupaten/Kota.")
    st.stop()

# ============================================================
# PROSES PIVOT DATA (BARIS: WILAYAH, KOLOM: TAHUN)
# ============================================================

df_filtered = df[df["tahun"].isin(tahun_terpilih) & df["kabupaten_kota"].isin(wilayah_terpilih)]

df_matrix = df_filtered.pivot_table(
    index="kabupaten_kota",
    columns="tahun",
    values="nilai",
    aggfunc="first"
).reset_index()

df_matrix.columns.name = None
df_matrix = df_matrix.rename(columns={"kabupaten_kota": "Kabupaten/Kota"})

# ============================================================
# TAMPILAN TABEL MATRIKS  # <-- BARU: pakai "-" untuk data kosong
# ============================================================

st.markdown("---")
st.subheader(f"📋 Matriks {indikator}")
st.write("Tabel perbandingan dengan baris berupa Kabupaten/Kota dan kolom berupa Tahun.")

# Versi khusus tampilan: angka diformat jadi teks, kosong jadi "-"
df_matrix_tampil = df_matrix.copy()

def format_angka_id(x):
    if pd.isna(x):
        return "-"
    # Format dulu gaya Amerika (123,456.78), lalu tukar posisi koma & titik
    teks = f"{x:,.2f}"
    teks = teks.replace(",", "TEMP").replace(".", ",").replace("TEMP", ".")
    return teks

for col in df_matrix_tampil.columns:
    if col != "Kabupaten/Kota":
        df_matrix_tampil[col] = df_matrix_tampil[col].apply(format_angka_id)

st.dataframe(
    df_matrix_tampil,
    use_container_width=True,
    hide_index=True
)

# ============================================================
# DOWNLOAD EXCEL MATRIKS  # <-- BARU: Excel juga pakai versi "-"
# ============================================================

output = BytesIO()

with pd.ExcelWriter(output, engine="openpyxl") as writer:
    df_matrix_tampil.to_excel(writer, index=False, sheet_name="Matriks_Kemiskinan")

output.seek(0)

st.download_button(
    label="📥 Download Excel",
    data=output,
    file_name=f"Matriks_Kemiskinan_{indikator}.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)

# ============================================================
# GRAFIK GARIS (PERBANDINGAN ANTAR WILAYAH)
# ============================================================

st.markdown("---")
st.subheader(f"📈 Grafik Tren {indikator}")

fig = px.line(
    df_filtered,
    x="tahun",
    y="nilai",
    color="kabupaten_kota",
    markers=True,
    title=f"Tren {indikator} Berdasarkan Wilayah"
)

fig.update_layout(
    xaxis_title="Tahun",
    yaxis_title="Nilai",
    hovermode="x unified",
    xaxis=dict(showgrid=False),
    yaxis=dict(showgrid=False)
)

st.plotly_chart(
    fig,
    use_container_width=True
)

# =========================================================
# INFORMASI
# =========================================================
st.caption("Sumber data: Badan Pusat Statistik (BPS).")

# ============================================================
# PANEL ADMIN (beroperasi ke tabel indikator terpilih)
# ============================================================

if is_admin and st.session_state.get("show_admin_panel", False):

    st.markdown("---")
    st.subheader(f"⚙️ Panel Admin — Kelola Data {indikator}")

    tab_tambah, tab_edit, tab_hapus = st.tabs([
        "➕ Tambah Data",
        "✏️ Edit Data",
        "🗑 Hapus Data"
    ])

    # ========================================================
    # TAMBAH DATA
    # ========================================================
    with tab_tambah:
        metode = st.radio(
            "Metode Input",
            ["Input Manual", "Import Excel/CSV"],
            horizontal=True,
            key="metode_tambah_kemiskinan"
        )

        st.markdown("---")

        if metode == "Input Manual":
            with st.form("form_tambah_kemiskinan", clear_on_submit=True):
                col_a, col_b, col_c = st.columns(3)
                with col_a:
                    wilayah_baru = st.text_input("Kabupaten/Kota", placeholder="Nama Wilayah")
                with col_b:
                    tahun_baru = st.number_input("Tahun", min_value=2000, max_value=2100, step=1)
                with col_c:
                    nilai_baru = st.number_input("Nilai", value=0.0, format="%.2f")

                if st.form_submit_button("💾 Simpan Data Baru"):
                    data_baru = {
                        "kabupaten_kota": wilayah_baru,
                        "tahun": int(tahun_baru),
                        "nilai": nilai_baru
                    }
                    try:
                        supabase_admin.table(nama_tabel).insert(data_baru).execute()
                        set_toast("Data baru berhasil ditambahkan.")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Gagal menyimpan data: {e}")
        else:
            admin_import_data(
                supabase_admin=supabase_admin,
                table_name=nama_tabel,
                kolom_wajib=["kabupaten_kota", "tahun", "nilai"],
                key_prefix=nama_tabel,
                kolom_teks=["kabupaten_kota"]
            )

    # ========================================================
    # EDIT DATA
    # ========================================================
    with tab_edit:
        opsi_baris = [
            f"{row['kabupaten_kota']} - {row['tahun']}: {row['nilai']}"
            for _, row in df.iterrows()
        ]

        pilih_baris = st.selectbox("Pilih data yang mau diedit", opsi_baris, key="pilih_edit")

        if pilih_baris:
            baris_idx = opsi_baris.index(pilih_baris)
            baris = df.iloc[baris_idx]

            with st.form("form_edit_kemiskinan"):
                st.write(f"Mengedit data: **{pilih_baris}**")

                nilai_edit = st.number_input(
                    "Nilai",
                    value=float(baris["nilai"]) if pd.notna(baris["nilai"]) else 0.0,
                    format="%.2f",
                    key="edit_nilai"
                )

                if st.form_submit_button("💾 Simpan Perubahan"):
                    try:
                        supabase_admin.table(nama_tabel).update(
                            {"nilai": nilai_edit}
                        ).eq("id", baris["id"]).execute()
                        set_toast("Data berhasil diperbarui.")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Gagal memperbarui data: {e}")

    # ========================================================
    # HAPUS DATA
    # ========================================================
    with tab_hapus:
        opsi_hapus = [
            f"{row['kabupaten_kota']} - {row['tahun']}: {row['nilai']}"
            for _, row in df.iterrows()
        ]

        pilih_hapus = st.selectbox("Pilih data yang mau dihapus", opsi_hapus, key="pilih_hapus")

        if st.button("🗑 Hapus Data Ini", key="tombol_hapus"):
            st.session_state["konfirmasi_hapus_kemiskinan"] = pilih_hapus

        if st.session_state.get("konfirmasi_hapus_kemiskinan"):
            target = st.session_state["konfirmasi_hapus_kemiskinan"]
            st.warning(f"Yakin ingin menghapus data **{target}**? Tindakan ini tidak bisa dibatalkan.")

            col_ya, col_batal = st.columns(2)
            with col_ya:
                if st.button("✅ Ya, Hapus Permanen", key="ya_hapus_kemiskinan"):
                    try:
                        baris_idx = opsi_hapus.index(target)
                        baris_target = df.iloc[baris_idx]

                        supabase_admin.table(nama_tabel).delete().eq(
                            "id", baris_target["id"]
                        ).execute()

                        if "konfirmasi_hapus_kemiskinan" in st.session_state:
                            del st.session_state["konfirmasi_hapus_kemiskinan"]

                        set_toast("Data berhasil dihapus.")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Gagal menghapus data: {e}")

            with col_batal:
                if st.button("❌ Batal", key="batal_hapus_kemiskinan"):
                    if "konfirmasi_hapus_kemiskinan" in st.session_state:
                        del st.session_state["konfirmasi_hapus_kemiskinan"]
                    st.rerun()