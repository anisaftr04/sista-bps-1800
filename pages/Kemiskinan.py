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
        color: #555555;
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
# AMBIL DATA
# ============================================================

response = supabase.table("kemiskinan").select("*").execute()
data = response.data

if not data:
    st.warning("Data Kemiskinan belum tersedia.")
    st.stop()

df = pd.DataFrame(data)
df["tahun"] = pd.to_numeric(df["tahun"], errors="coerce")

# Tentukan nama kolom wilayah di database Anda (ubah jika berbeda, misal: "kabupaten" atau "wilayah")
kolom_wilayah_db = "wilayah" 

# ============================================================
# DAFTAR INDIKATOR
# ============================================================

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

# ============================================================
# FILTER INTERAKTIF (INDIKATOR, TAHUN, WILAYAH)
# ============================================================

st.markdown("### 🎛️ Filter Data")
col_f1, col_f2, col_f3 = st.columns(3)

with col_f1:
    indikator = st.selectbox(
        "📊 Pilih Indikator",
        list(daftar_indikator.keys())
    )
    
    # Pilihan tipe wilayah (kota / desa / gabungan) untuk pemetaan kolom database
    tipe_wilayah_opsi = {
        "Kota": "kota",
        "Desa": "desa",
        "Kota + Desa": "kota_desa"
    }
    tipe_wilayah = st.selectbox("📌 Kategori Wilayah", list(tipe_wilayah_opsi.keys()))

with col_f2:
    semua_tahun = sorted(df["tahun"].dropna().unique().tolist())
    pilih_semua_tahun = st.checkbox("Pilih Semua Tahun", value=True)
    
    if pilih_semua_tahun:
        tahun_terpilih = st.multiselect("📅 Pilih Tahun", semua_tahun, default=semua_tahun)
    else:
        tahun_terpilih = st.multiselect("📅 Pilih Tahun", semua_tahun, default=semua_tahun[:3] if len(semua_tahun)>=3 else semua_tahun)

with col_f3:
    semua_wilayah = sorted(df[kolom_wilayah_db].dropna().unique().tolist()) if kolom_wilayah_db in df.columns else ["Lampung", "Bandar Lampung", "Metro"]
    pilih_semua_wilayah = st.checkbox("Pilih Semua Kabupaten/Kota", value=True)
    
    if pilih_semua_wilayah:
        wilayah_terpilih = st.multiselect("📍 Pilih Kabupaten/Kota", semua_wilayah, default=semua_wilayah)
    else:
        wilayah_terpilih = st.multiselect("📍 Pilih Kabupaten/Kota", semua_wilayah, default=semua_wilayah[:3] if len(semua_wilayah)>=3 else semua_wilayah)

if not tahun_terpilih or not wilayah_terpilih:
    st.warning("⚠️ Silakan pilih minimal satu Tahun dan satu Kabupaten/Kota.")
    st.stop()

# ============================================================
# PROSES PIVOT DATA (BARIS: WILAYAH, KOLOM: TAHUN)
# ============================================================

kolom_data = daftar_indikator[indikator][tipe_wilayah_opsi[tiype_wilayah := tipe_wilayah]]

df_filtered = df[df["tahun"].isin(tahun_terpilih) & df[kolom_wilayah_db].isin(wilayah_terpilih)]

# Membuat tabel matriks
df_matrix = df_filtered.pivot_table(
    index=kolom_wilayah_db,
    columns="tahun",
    values=kolom_data,
    aggfunc="first"
).reset_index()

df_matrix.columns.name = None
df_matrix = df_matrix.rename(columns={kolom_wilayah_db: "Kabupaten/Kota"})

# ============================================================
# TAMPILAN TABEL MATRIKS
# ============================================================

st.markdown("---")
st.subheader(f"📋 Matriks {indikator} ({tipe_wilayah})")
st.write("Tabel perbandingan dengan baris berupa Kabupaten/Kota dan kolom berupa Tahun.")

st.dataframe(
    df_matrix,
    use_container_width=True,
    hide_index=True,
    column_config={
        col: st.column_config.NumberColumn(format="%.2f") for col in df_matrix.columns if col != "Kabupaten/Kota"
    }
)

# ============================================================
# DOWNLOAD EXCEL MATRIKS
# ============================================================

output = BytesIO()

with pd.ExcelWriter(output, engine="openpyxl") as writer:
    df_matrix.to_excel(writer, index=False, sheet_name="Matriks_Kemiskinan")

output.seek(0)

st.download_button(
    label="📥 Download Excel Matriks (Wilayah x Tahun)",
    data=output,
    file_name=f"Matriks_Kemiskinan_{indikator}.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)

# ============================================================
# GRAFIK GARIS (PERBANDINGAN ANTAR WILAYAH)
# ============================================================

st.markdown("---")
st.subheader(f"📈 Grafik Tren {indikator} ({tipe_wilayah})")

# Ubah format data kembali ke bentuk long format agar mudah dibaca Plotly Express
df_long = df_filtered.melt(
    id_vars=[kolom_wilayah_db, "tahun"],
    value_vars=[kolom_data],
    var_name="Indikator",
    value_name="Nilai"
)

fig = px.line(
    df_long,
    x="tahun",
    y="Nilai",
    color=kolom_wilayah_db,
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
# PANEL ADMIN
# ============================================================

if is_admin and st.session_state.get("show_admin_panel", False):

    st.markdown("---")
    st.subheader("⚙️ Panel Admin — Kelola Data Kemiskinan")

    semua_kolom_nilai = []
    for ind in daftar_indikator.values():
        semua_kolom_nilai.extend(ind.values())
    semua_kolom_nilai = sorted(set(semua_kolom_nilai))

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
                    tahun_baru = st.number_input("Tahun", min_value=2000, max_value=2100, step=1)
                with col_b:
                    periode_baru = st.text_input("Periode", placeholder="Misal: Maret / September")
                with col_c:
                    wilayah_baru = st.text_input("Kabupaten/Kota", placeholder="Nama Wilayah")

                st.markdown("**Isi nilai per indikator:**")
                nilai_input = {}
                cols = st.columns(3)
                for i, kolom in enumerate(semua_kolom_nilai):
                    with cols[i % 3]:
                        nilai_input[kolom] = st.number_input(kolom.replace("_", " ").title(), value=0.0, key=f"tambah_{kolom}")

                if st.form_submit_button("💾 Simpan Data Baru"):
                    data_baru = {
                        "tahun": int(tahun_baru), 
                        "periode": periode_baru,
                        kolom_wilayah_db: wilayah_baru
                    }
                    data_baru.update(nilai_input)
                    try:
                        supabase_admin.table("kemiskinan").insert(data_baru).execute()
                        set_toast("Data baru berhasil ditambahkan.")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Gagal menyimpan data: {e}")
        else:
            kolom_wajib = ["tahun", "periode", kolom_wilayah_db] + semua_kolom_nilai
            admin_import_data(
                supabase_admin=supabase_admin,
                table_name="kemiskinan",
                kolom_wajib=kolom_wajib,
                key_prefix="kemiskinan",
                kolom_teks=["periode", kolom_wilayah_db]
            )

    # ========================================================
    # EDIT DATA
    # ========================================================
    with tab_edit:
        opsi_baris = [
            f"{row['tahun']} - {row.get(kolom_wilayah_db, '')} ({row['periode']})"
            for _, row in df.iterrows()
        ]

        pilih_baris = st.selectbox("Pilih data yang mau diedit", opsi_baris, key="pilih_edit")

        if pilih_baris:
            # Sederhanakan parsing berdasarkan data dataframe asli
            baris_idx = opsi_baris.index(pilih_baris)
            baris = df.iloc[baris_idx]

            with st.form("form_edit_kemiskinan"):
                st.write(f"Mengedit data: **{pilih_baris}**")
                nilai_edit = {}
                cols = st.columns(3)

                for i, kolom in enumerate(semua_kolom_nilai):
                    with cols[i % 3]:
                        nilai_edit[kolom] = st.number_input(
                            kolom.replace("_", " ").title(),
                            value=float(baris[kolom]) if pd.notna(baris[kolom]) else 0.0,
                            key=f"edit_{kolom}"
                        )

                if st.form_submit_button("💾 Simpan Perubahan"):
                    try:
                        supabase_admin.table("kemiskinan").update(nilai_edit).eq("id", baris["id"] if "id" in baris else baris.get("tahun")).execute()
                        set_toast("Data berhasil diperbarui.")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Gagal memperbarui data: {e}")

   # ========================================================
    # HAPUS DATA
    # ========================================================
    with tab_hapus:
        opsi_hapus = [
            f"{row['tahun']} - {row.get(kolom_wilayah_db, '')} ({row['periode']})"
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
                        
                        supabase_admin.table("kemiskinan").delete().eq("tahun", int(baris_target["tahun"])).eq(kolom_wilayah_db, baris_target[kolom_wilayah_db]).eq("periode", baris_target["periode"]).execute()
                        
                        # Perbaikan baris penghapusan session state
                        if "konfirmasi_hapus_kemiskinan" in st.session_state:
                            del st.session_state["konfirmasi_hapus_kemiskinan"]
                        if "konfirmasi_hapus_kemisklan" in st.session_state:
                            del st.session_state["konfirmasi_hapus_kemisklan"]
                        
                        set_toast("Data berhasil dihapus.")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Gagal menghapus data: {e}")

            with col_batal:
                if st.button("❌ Batal", key="batal_hapus_kemiskinan"):
                    if "konfirmasi_hapus_kemiskinan" in st.session_state:
                        del st.session_state["konfirmasi_hapus_kemiskinan"]
                    st.rerun()
