import streamlit as st
import pandas as pd
import plotly.express as px
from supabase import create_client, Client
from io import BytesIO

from utils import load_css, admin_edit_button, set_toast, admin_import_data

load_css()

is_admin = st.session_state.get("is_admin", False)

# =========================================================
# KONFIGURASI SUPABASE
# =========================================================
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
service_key = st.secrets["SUPABASE_SERVICE_ROLE_KEY"]
supabase: Client = create_client(url, key)
supabase_admin: Client = create_client(url, service_key)


# =========================================================
# JUDUL
# =========================================================
col_judul, col_edit = st.columns([8, 1])
with col_judul:
    st.title("📚 Indikator Pendidikan")
with col_edit:
    st.write("")
    admin_edit_button()

st.write(
    "Halaman ini menyajikan beberapa indikator pendidikan "
    "di Provinsi Lampung, meliputi Angka Partisipasi Sekolah "
    "(APS), Angka Partisipasi Murni (APM), dan Angka Partisipasi "
    "Kasar (APK)."
)


# =========================================================
# PEMETAAN KODE WILAYAH
# =========================================================
nama_wilayah = {
    "1801": "Lampung Barat", "1802": "Tanggamus", "1803": "Lampung Selatan",
    "1804": "Lampung Timur", "1805": "Lampung Tengah", "1806": "Lampung Utara",
    "1807": "Way Kanan", "1808": "Tulang Bawang", "1809": "Pesawaran",
    "1810": "Pringsewu", "1811": "Mesuji", "1812": "Tulang Bawang Barat",
    "1813": "Pesisir Barat", "1871": "Bandar Lampung", "1872": "Metro"
}

kode_dari_nama = {v: k for k, v in nama_wilayah.items()}


# =========================================================
# FUNGSI AMBIL DATA
# =========================================================
@st.cache_data
def get_data(tabel):
    response = supabase.table(tabel).select("*").execute()
    return pd.DataFrame(response.data)


# =========================================================
# FUNGSI BANTU: DOWNLOAD EXCEL
# =========================================================
def tombol_download_excel(df_export, nama_sheet, nama_file):
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df_export.to_excel(writer, index=False, sheet_name=nama_sheet)
    output.seek(0)

    st.download_button(
        label="📥 Download Excel",
        data=output,
        file_name=nama_file,
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )


# =========================================================
# AMBIL SEMUA DATA
# =========================================================
df_aps = get_data("aps")
df_aps_2025 = get_data("aps_kabko_2025")
df_apm = get_data("apm_kabko_2025")
df_apk = get_data("apk_kabko_2025")

TABEL_MAP = {
    "aps": df_aps,
    "aps_kabko_2025": df_aps_2025,
    "apm_kabko_2025": df_apm,
    "apk_kabko_2025": df_apk
}

# =========================================================
# NORMALISASI KODE WILAYAH
# =========================================================
for tabel_df in [df_aps, df_aps_2025, df_apm, df_apk]:
    if not tabel_df.empty and "kode_wilayah" in tabel_df.columns:
        tabel_df["kode_wilayah"] = tabel_df["kode_wilayah"].astype(str).str.strip().str.replace(".0", "", regex=False)
        tabel_df["nama_wilayah"] = tabel_df["kode_wilayah"].map(nama_wilayah)


# =========================================================
# GABUNG DAFTAR WILAYAH
# =========================================================
wilayah = set()
for tabel_df in [df_aps, df_aps_2025, df_apm, df_apk]:
    if not tabel_df.empty and "nama_wilayah" in tabel_df.columns:
        wilayah.update(tabel_df["nama_wilayah"].dropna().unique())
wilayah = sorted(wilayah)


# =========================================================
# PILIH WILAYAH
# =========================================================
st.subheader("📍 Pilih Kabupaten/Kota")
pilihan_wilayah = st.selectbox("Kabupaten/Kota", wilayah)


# =========================================================
# PILIH INDIKATOR
# =========================================================
st.subheader("📊 Pilih Indikator Pendidikan")
indikator = st.selectbox("Indikator", ["APS", "APM", "APK"])

admin_tabel = None
admin_kolom_map = {}


# =========================================================
# APS
# =========================================================
if indikator == "APS":

    st.subheader(f"📚 Angka Partisipasi Sekolah (APS) — {pilihan_wilayah}")

    kategori_aps = st.selectbox("Kategori APS", ["Berdasarkan Kelompok Umur", "Kabupaten/Kota Tahun 2025"])

    if kategori_aps == "Berdasarkan Kelompok Umur":

        admin_tabel = "aps"
        admin_kolom_map = {"usia_7_12": "7–12 Tahun", "usia_13_15": "13–15 Tahun"}

        df = df_aps[df_aps["nama_wilayah"] == pilihan_wilayah].copy()

        if df.empty:
            st.info("Data APS berdasarkan kelompok umur tidak tersedia untuk wilayah ini.")
        else:
            df = df.sort_values("tahun")
            kolom = [c for c in ["tahun", "usia_7_12", "usia_13_15"] if c in df.columns]
            tabel = df[kolom].rename(columns={"tahun": "Tahun", "usia_7_12": "7–12 Tahun", "usia_13_15": "13–15 Tahun"})

            st.dataframe(tabel, use_container_width=True, hide_index=True)

            tombol_download_excel(
                tabel, "APS Kelompok Umur",
                f"APS_KelompokUmur_{pilihan_wilayah}.xlsx"
            )

            if len(tabel.columns) > 1:
                st.subheader("📈 Perkembangan APS")

                tabel_long = tabel.melt(id_vars="Tahun", var_name="Kelompok Usia", value_name="APS")

                fig = px.line(
                    tabel_long, x="Tahun", y="APS", color="Kelompok Usia",
                    markers=True, title="Perkembangan APS Berdasarkan Kelompok Usia"
                )
                fig.update_layout(
                    xaxis_title="Tahun", yaxis_title="APS (%)",
                    xaxis=dict(showgrid=False), yaxis=dict(showgrid=False)
                )
                st.plotly_chart(fig, use_container_width=True)

    else:

        admin_tabel = "aps_kabko_2025"
        admin_kolom_map = {
            "aps_7_12": "APS 7–12 Tahun", "aps_13_15": "APS 13–15 Tahun",
            "aps_16_18": "APS 16–18 Tahun", "aps_19_23": "APS 19–23 Tahun"
        }

        df = df_aps_2025[df_aps_2025["nama_wilayah"] == pilihan_wilayah].copy()

        if df.empty:
            st.info("Data APS tahun 2025 tidak tersedia untuk wilayah ini.")
        else:
            kolom = [c for c in ["tahun", "aps_7_12", "aps_13_15", "aps_16_18", "aps_19_23"] if c in df.columns]
            tabel = df[kolom].rename(columns={
                "tahun": "Tahun", "aps_7_12": "APS 7–12 Tahun", "aps_13_15": "APS 13–15 Tahun",
                "aps_16_18": "APS 16–18 Tahun", "aps_19_23": "APS 19–23 Tahun"
            })

            st.dataframe(tabel, use_container_width=True, hide_index=True)

            tombol_download_excel(
                tabel, "APS 2025",
                f"APS_2025_{pilihan_wilayah}.xlsx"
            )

            st.subheader("📊 APS Berdasarkan Kelompok Umur Tahun 2025")

            tabel_long = tabel.melt(id_vars="Tahun", var_name="Kelompok Usia", value_name="APS")

            fig = px.bar(
                tabel_long, x="Tahun", y="APS", color="Kelompok Usia",
                barmode="group", title="APS Berdasarkan Kelompok Umur Tahun 2025"
            )
            fig.update_layout(
                xaxis_title="Tahun", yaxis_title="APS (%)",
                xaxis=dict(showgrid=False), yaxis=dict(showgrid=False)
            )
            st.plotly_chart(fig, use_container_width=True)


# =========================================================
# APM
# =========================================================
elif indikator == "APM":

    st.subheader(f"🎓 Angka Partisipasi Murni (APM) — {pilihan_wilayah}")

    admin_tabel = "apm_kabko_2025"
    admin_kolom_map = {"apm_sd": "APM SD", "apm_smp": "APM SMP", "apm_sma": "APM SMA", "apm_pt": "APM Perguruan Tinggi"}

    df = df_apm[df_apm["nama_wilayah"] == pilihan_wilayah].copy()

    if df.empty:
        st.info("Data APM tidak tersedia untuk wilayah ini.")
    else:
        kolom = [c for c in ["tahun", "apm_sd", "apm_smp", "apm_sma", "apm_pt"] if c in df.columns]
        tabel = df[kolom].rename(columns={
            "tahun": "Tahun", "apm_sd": "APM SD", "apm_smp": "APM SMP", "apm_sma": "APM SMA", "apm_pt": "APM Perguruan Tinggi"
        })

        st.dataframe(tabel, use_container_width=True, hide_index=True)

        tombol_download_excel(
            tabel, "APM 2025",
            f"APM_{pilihan_wilayah}.xlsx"
        )

        st.subheader("📌 Nilai APM Tahun 2025")
        data = df.iloc[0]
        col1, col2, col3, col4 = st.columns(4)
        with col1: st.metric("APM SD", f"{data['apm_sd']:.2f}%")
        with col2: st.metric("APM SMP", f"{data['apm_smp']:.2f}%")
        with col3: st.metric("APM SMA", f"{data['apm_sma']:.2f}%")
        with col4: st.metric("APM PT", f"{data['apm_pt']:.2f}%")

        st.subheader("📊 Perbandingan APM Berdasarkan Jenjang")

        grafik = pd.DataFrame({
            "Jenjang": ["SD", "SMP", "SMA", "Perguruan Tinggi"],
            "APM": [data["apm_sd"], data["apm_smp"], data["apm_sma"], data["apm_pt"]]
        })

        fig = px.bar(grafik, x="Jenjang", y="APM", title="Perbandingan APM Berdasarkan Jenjang")
        fig.update_layout(
            xaxis_title="Jenjang", yaxis_title="APM (%)",
            xaxis=dict(showgrid=False), yaxis=dict(showgrid=False)
        )
        st.plotly_chart(fig, use_container_width=True)


# =========================================================
# APK
# =========================================================
elif indikator == "APK":

    st.subheader(f"🎒 Angka Partisipasi Kasar (APK) — {pilihan_wilayah}")

    admin_tabel = "apk_kabko_2025"
    admin_kolom_map = {"apk_sd": "APK SD", "apk_smp": "APK SMP", "apk_sma": "APK SMA", "apk_pt": "APK Perguruan Tinggi"}

    df = df_apk[df_apk["nama_wilayah"] == pilihan_wilayah].copy()

    if df.empty:
        st.info("Data APK tidak tersedia untuk wilayah ini.")
    else:
        kolom = [c for c in ["tahun", "apk_sd", "apk_smp", "apk_sma", "apk_pt"] if c in df.columns]
        tabel = df[kolom].rename(columns={
            "tahun": "Tahun", "apk_sd": "APK SD", "apk_smp": "APK SMP", "apk_sma": "APK SMA", "apk_pt": "APK Perguruan Tinggi"
        })

        st.dataframe(tabel, use_container_width=True, hide_index=True)

        tombol_download_excel(
            tabel, "APK 2025",
            f"APK_{pilihan_wilayah}.xlsx"
        )

        st.subheader("📌 Nilai APK Tahun 2025")
        data = df.iloc[0]
        col1, col2, col3, col4 = st.columns(4)
        with col1: st.metric("APK SD", f"{data['apk_sd']:.2f}%")
        with col2: st.metric("APK SMP", f"{data['apk_smp']:.2f}%")
        with col3: st.metric("APK SMA", f"{data['apk_sma']:.2f}%")
        with col4: st.metric("APK PT", f"{data['apk_pt']:.2f}%")

        st.subheader("📊 Perbandingan APK Berdasarkan Jenjang")

        grafik = pd.DataFrame({
            "Jenjang": ["SD", "SMP", "SMA", "Perguruan Tinggi"],
            "APK": [data["apk_sd"], data["apk_smp"], data["apk_sma"], data["apk_pt"]]
        })

        fig = px.bar(grafik, x="Jenjang", y="APK", title="Perbandingan APK Berdasarkan Jenjang")
        fig.update_layout(
            xaxis_title="Jenjang", yaxis_title="APK (%)",
            xaxis=dict(showgrid=False), yaxis=dict(showgrid=False)
        )
        st.plotly_chart(fig, use_container_width=True)


# =========================================================
# INFORMASI
# =========================================================
st.caption("Sumber data: Badan Pusat Statistik (BPS).")


# =========================================================
# PANEL ADMIN
# =========================================================

if is_admin and st.session_state.get("show_admin_panel", False) and admin_tabel:

    st.markdown("---")
    st.subheader(f"⚙️ Panel Admin — {indikator}")
    st.caption(f"Mengelola tabel: `{admin_tabel}`")

    admin_df = TABEL_MAP[admin_tabel]

    tab_tambah, tab_edit, tab_hapus = st.tabs(["➕ Tambah Data", "✏️ Edit Data", "🗑 Hapus Data"])

    # ---------------- TAMBAH ----------------
    with tab_tambah:

        metode = st.radio(
            "Metode Input",
            ["Input Manual", "Import Excel/CSV"],
            horizontal=True,
            key=f"metode_tambah_{admin_tabel}"
        )

        st.markdown("---")

        if metode == "Input Manual":

            with st.form(f"form_tambah_{admin_tabel}", clear_on_submit=True):
                col_a, col_b = st.columns(2)
                with col_a:
                    tahun_baru = st.number_input("Tahun", min_value=2000, max_value=2100, step=1)
                with col_b:
                    wilayah_baru = st.selectbox("Kabupaten/Kota", wilayah, key=f"tambah_wilayah_{admin_tabel}")

                st.markdown("**Isi nilai per indikator:**")
                nilai_input = {}
                cols = st.columns(2)
                for i, (raw, label) in enumerate(admin_kolom_map.items()):
                    with cols[i % 2]:
                        nilai_input[raw] = st.number_input(label, value=0.0, key=f"tambah_{admin_tabel}_{raw}")

                if st.form_submit_button("💾 Simpan Data Baru"):
                    data_baru = {
                        "tahun": int(tahun_baru),
                        "kode_wilayah": kode_dari_nama[wilayah_baru]
                    }
                    data_baru.update(nilai_input)

                    try:
                        supabase_admin.table(admin_tabel).insert(data_baru).execute()
                        get_data.clear()
                        set_toast("Data baru berhasil ditambahkan.")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Gagal menyimpan data: {e}")

        else:

            with st.expander("📌 Lihat daftar kode wilayah"):
                st.dataframe(
                    pd.DataFrame({
                        "kode_wilayah": list(nama_wilayah.keys()),
                        "Kabupaten/Kota": list(nama_wilayah.values())
                    }),
                    use_container_width=True, hide_index=True
                )

            kolom_wajib = ["tahun", "kode_wilayah"] + list(admin_kolom_map.keys())

            admin_import_data(
                supabase_admin=supabase_admin,
                table_name=admin_tabel,
                kolom_wajib=kolom_wajib,
                key_prefix=admin_tabel,
                kolom_teks=["kode_wilayah"],
                on_success=get_data.clear
            )

    # ---------------- EDIT ----------------
    with tab_edit:
        opsi_baris = [
            {"label": f"{row['tahun']} - {row.get('nama_wilayah', row['kode_wilayah'])}", "tahun": row["tahun"], "kode": row["kode_wilayah"]}
            for _, row in admin_df.iterrows()
        ]

        pilih_baris = st.selectbox(
            "Pilih data yang mau diedit",
            opsi_baris,
            format_func=lambda x: x["label"],
            key=f"pilih_edit_{admin_tabel}"
        )

        if pilih_baris:
            baris = admin_df[
                (admin_df["tahun"] == pilih_baris["tahun"]) & (admin_df["kode_wilayah"] == pilih_baris["kode"])
            ].iloc[0]

            with st.form(f"form_edit_{admin_tabel}"):
                st.write(f"Mengedit data: **{pilih_baris['label']}**")

                nilai_edit = {}
                cols = st.columns(2)
                for i, (raw, label) in enumerate(admin_kolom_map.items()):
                    with cols[i % 2]:
                        nilai_edit[raw] = st.number_input(
                            label,
                            value=float(baris[raw]) if raw in baris and pd.notna(baris[raw]) else 0.0,
                            key=f"edit_{admin_tabel}_{raw}"
                        )

                if st.form_submit_button("💾 Simpan Perubahan"):
                    try:
                        supabase_admin.table(admin_tabel).update(nilai_edit) \
                            .eq("tahun", pilih_baris["tahun"]).eq("kode_wilayah", pilih_baris["kode"]).execute()
                        get_data.clear()
                        set_toast("Data berhasil diperbarui.")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Gagal memperbarui data: {e}")

    # ---------------- HAPUS ----------------
    with tab_hapus:
        opsi_hapus = [
            {"label": f"{row['tahun']} - {row.get('nama_wilayah', row['kode_wilayah'])}", "tahun": row["tahun"], "kode": row["kode_wilayah"]}
            for _, row in admin_df.iterrows()
        ]

        pilih_hapus = st.selectbox(
            "Pilih data yang mau dihapus",
            opsi_hapus,
            format_func=lambda x: x["label"],
            key=f"pilih_hapus_{admin_tabel}"
        )

        if st.button("🗑 Hapus Data Ini", key=f"tombol_hapus_{admin_tabel}"):
            st.session_state[f"konfirmasi_hapus_{admin_tabel}"] = pilih_hapus

        konfirmasi_key = f"konfirmasi_hapus_{admin_tabel}"
        if st.session_state.get(konfirmasi_key):
            target = st.session_state[konfirmasi_key]
            st.warning(f"Yakin ingin menghapus data **{target['label']}**? Tindakan ini tidak bisa dibatalkan.")

            col_ya, col_batal = st.columns(2)
            with col_ya:
                if st.button("✅ Ya, Hapus Permanen", key=f"ya_hapus_{admin_tabel}"):
                    try:
                        supabase_admin.table(admin_tabel).delete().eq("tahun", target["tahun"]).eq("kode_wilayah", target["kode"]).execute()
                        get_data.clear()
                        del st.session_state[konfirmasi_key]
                        set_toast("Data berhasil dihapus.")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Gagal menghapus data: {e}")
            with col_batal:
                if st.button("❌ Batal", key=f"batal_hapus_{admin_tabel}"):
                    del st.session_state[konfirmasi_key]
                    st.rerun()